"""
单元测试：数据验证模块
"""

import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_validator import DataValidator


class TestDataValidator(unittest.TestCase):
    """数据验证模块单元测试"""
    
    def test_valid_data(self):
        """测试有效数据"""
        data = [
            {
                "品名": "钢管",
                "规格": "Φ10*1.5",
                "材质": "碳钢",
                "产地": "天津",
                "仓库": "库房A",
                "价格": "150元/支"
            }
        ]
        result = DataValidator.validate_and_clean(data)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["品名"], "钢管")
        self.assertEqual(result[0]["规格"], "Φ10*1.5")
    
    def test_missing_required_field(self):
        """测试缺少必填字段"""
        data = [
            {"规格": "Φ10*1.5", "材质": "碳钢"}  # 缺少品名
        ]
        result = DataValidator.validate_and_clean(data)
        self.assertEqual(len(result), 0)
    
    def test_empty_required_field(self):
        """测试必填字段为空"""
        data = [
            {"品名": "", "规格": "Φ10*1.5"}  # 品名为空
        ]
        result = DataValidator.validate_and_clean(data)
        self.assertEqual(len(result), 0)
    
    def test_duplicate_removal(self):
        """测试去重功能"""
        data = [
            {
                "品名": "钢管",
                "规格": "Φ10*1.5",
                "材质": "碳钢",
                "产地": "天津",
                "仓库": "库房A",
                "价格": "150元/支"
            },
            {
                "品名": "钢管",
                "规格": "Φ10*1.5",  # 与第一条重复
                "材质": "碳钢",
                "产地": "天津",
                "仓库": "库房A",
                "价格": "150元/支"
            }
        ]
        result = DataValidator.validate_and_clean(data, enable_dedup=True)
        self.assertEqual(len(result), 1)
    
    def test_no_deduplication(self):
        """测试禁用去重"""
        data = [
            {"品名": "钢管", "规格": "Φ10*1.5"},
            {"品名": "钢管", "规格": "Φ10*1.5"}
        ]
        result = DataValidator.validate_and_clean(data, enable_dedup=False)
        self.assertEqual(len(result), 2)
    
    def test_whitespace_cleanup(self):
        """测试空格清理"""
        data = [
            {"品名": "  钢管  ", "规格": " Φ10*1.5 "}
        ]
        result = DataValidator.validate_and_clean(data)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["品名"], "钢管")
        self.assertEqual(result[0]["规格"], "Φ10*1.5")
    
    def test_invalid_data_format(self):
        """测试无效数据格式"""
        result = DataValidator.validate_and_clean("not a list")
        self.assertEqual(len(result), 0)
        
        result = DataValidator.validate_and_clean(None)
        self.assertEqual(len(result), 0)
    
    def test_missing_fields_recovery(self):
        """测试缺失字段的恢复"""
        data = [
            {"品名": "钢管"}  # 只有品名
        ]
        result = DataValidator.validate_and_clean(data)
        self.assertEqual(len(result), 1)
        # 验证所有字段都被补齐
        self.assertEqual(len(result[0]), 6)
        self.assertEqual(result[0]["规格"], "")
        self.assertEqual(result[0]["材质"], "")


class TestDataValidatorField(unittest.TestCase):
    """单个字段验证测试"""
    
    def test_validate_brand_field(self):
        """测试品名字段验证"""
        self.assertTrue(DataValidator.validate_field("品名", "钢管"))
        self.assertFalse(DataValidator.validate_field("品名", ""))
        self.assertFalse(DataValidator.validate_field("品名", "   "))
    
    def test_validate_price_field(self):
        """测试价格字段验证"""
        self.assertTrue(DataValidator.validate_field("价格", "150元/支"))
        self.assertTrue(DataValidator.validate_field("价格", ""))
        self.assertTrue(DataValidator.validate_field("价格", "2元/个"))


class TestDataQualityAssessment(unittest.TestCase):
    """数据质量评估测试"""
    
    def test_quality_score_perfect(self):
        """测试完美数据的质量分数"""
        data = [
            {
                "品名": "钢管",
                "规格": "Φ10*1.5",
                "材质": "碳钢",
                "产地": "天津",
                "仓库": "库房A",
                "价格": "150元/支"
            }
        ]
        score = DataValidator.assess_data_quality(data)
        self.assertEqual(score, 100.0)
    
    def test_quality_score_partial(self):
        """测试不完整数据的质量分数"""
        data = [
            {"品名": "钢管", "规格": "Φ10*1.5", "材质": "", "产地": "", "仓库": "", "价格": ""}
        ]
        score = DataValidator.assess_data_quality(data)
        self.assertGreater(score, 0)
        self.assertLess(score, 100)
    
    def test_quality_score_empty(self):
        """测试空数据的质量分数"""
        score = DataValidator.assess_data_quality([])
        self.assertEqual(score, 0.0)


if __name__ == '__main__':
    unittest.main()
