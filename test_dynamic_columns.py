#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试动态列名功能的端到端集成测试

测试场景：
1. 模拟 LLM 识别有列名的表格
2. 模拟 LLM 识别无列名的表格
3. 测试表格结构检测
4. 测试数据规范化
5. 测试数据清洗
6. 测试 Excel 生成
"""

import sys
import json
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.getcwd())

from src.logger import logger
from src.table_structure_detector import TableStructureDetector
from src.data_validator import DataValidator
from src.excel_engine import ExcelGenerator


def test_scenario_1():
    """测试场景 1：有列名的表格"""
    logger.info("\n" + "="*60)
    logger.info("🧪 测试场景 1：有列名的表格")
    logger.info("="*60)
    
    # 模拟 LLM 返回的结果
    llm_response = {
        "has_table": True,
        "table_type": "structured",
        "columns": ["题型", "题量", "分值", "考试时间测算"],
        "rows": [
            {"题型": "单选题", "题量": "25个", "分值": "25分", "考试时间测算": "15分"},
            {"题型": "判断题", "题量": "15个", "分值": "15分", "考试时间测算": "10分"},
            {"题型": "案例分析", "题量": "2个", "分值": "15分", "考试时间测算": "20分"}
        ],
        "notes": ""
    }
    
    logger.info("📊 LLM 识别结果:")
    logger.info(f"  - 表格: {llm_response['has_table']}")
    logger.info(f"  - 列名: {llm_response['columns']}")
    logger.info(f"  - 行数: {len(llm_response['rows'])}")
    
    # 1. 表格结构检测
    logger.info("\n[步骤 1] 检测表格结构...")
    structure = TableStructureDetector.detect_structure(llm_response)
    assert structure is not None, "表格结构检测失败"
    assert structure['has_table'] == True, "应识别到表格"
    assert len(structure['columns']) == 4, "列数应为 4"
    logger.info("✓ 表格结构检测成功")
    
    # 2. 数据规范化
    logger.info("\n[步骤 2] 规范化数据...")
    normalized = TableStructureDetector.normalize_data(structure)
    assert len(normalized) == 3, "应有 3 条数据"
    logger.info(f"✓ 数据规范化成功，{len(normalized)} 条记录")
    
    # 3. 数据清洗
    logger.info("\n[步骤 3] 清洗数据...")
    cleaned = DataValidator.validate_and_clean(
        normalized,
        enable_dedup=True,
        columns=structure['columns']
    )
    assert len(cleaned) > 0, "清洗后应有数据"
    logger.info(f"✓ 数据清洗成功，{len(cleaned)} 条有效记录")
    
    # 4. 生成 Excel
    logger.info("\n[步骤 4] 生成 Excel...")
    excel_gen = ExcelGenerator()
    excel_path = excel_gen.generate(
        cleaned,
        source_name="测试场景1_有列名",
        columns=structure['columns']
    )
    assert excel_path is not None, "Excel 生成失败"
    assert os.path.exists(excel_path), f"Excel 文件不存在: {excel_path}"
    logger.info(f"✓ Excel 生成成功: {excel_path}")
    
    return True


def test_scenario_2():
    """测试场景 2：无列名的表格"""
    logger.info("\n" + "="*60)
    logger.info("🧪 测试场景 2：无列名的表格")
    logger.info("="*60)
    
    # 模拟 LLM 返回的结果（无列名）
    llm_response = {
        "has_table": True,
        "table_type": "structured",
        "columns": [],  # 无列名
        "rows": [
            ["25个", "材料A", "高强度"],
            ["15个", "材料B", "耐磨"],
            ["12个", "材料C", "防水"]
        ],
        "notes": "该表格没有明显的列名"
    }
    
    logger.info("📊 LLM 识别结果:")
    logger.info(f"  - 表格: {llm_response['has_table']}")
    logger.info(f"  - 有列名: {bool(llm_response['columns'])}")
    logger.info(f"  - 行数: {len(llm_response['rows'])}")
    
    # 1. 表格结构检测
    logger.info("\n[步骤 1] 检测表格结构...")
    structure = TableStructureDetector.detect_structure(llm_response)
    assert structure is not None, "表格结构检测失败"
    assert structure['has_table'] == True, "应识别到表格"
    assert len(structure['columns']) == 0, "无列名表格的列名数应为 0"
    logger.info("✓ 表格结构检测成功（识别为无列名表格）")
    
    # 2. 数据规范化
    logger.info("\n[步骤 2] 规范化数据...")
    normalized = TableStructureDetector.normalize_data(structure)
    assert len(normalized) == 3, "应有 3 条数据"
    assert "列1" in normalized[0], "无列名数据应使用'列N'作为键"
    logger.info(f"✓ 数据规范化成功，{len(normalized)} 条记录")
    logger.info(f"  自动生成的列名: {list(normalized[0].keys())}")
    
    # 3. 数据清洗
    logger.info("\n[步骤 3] 清洗数据...")
    cleaned = DataValidator.validate_and_clean(
        normalized,
        enable_dedup=True,
        columns=list(normalized[0].keys()) if normalized else None
    )
    assert len(cleaned) > 0, "清洗后应有数据"
    logger.info(f"✓ 数据清洗成功，{len(cleaned)} 条有效记录")
    
    # 4. 生成 Excel
    logger.info("\n[步骤 4] 生成 Excel...")
    excel_gen = ExcelGenerator()
    excel_path = excel_gen.generate(
        cleaned,
        source_name="测试场景2_无列名",
        columns=list(normalized[0].keys()) if normalized else None
    )
    assert excel_path is not None, "Excel 生成失败"
    assert os.path.exists(excel_path), f"Excel 文件不存在: {excel_path}"
    logger.info(f"✓ Excel 生成成功: {excel_path}")
    
    return True


def test_scenario_3():
    """测试场景 3：不同列名的表格（产品类表格）"""
    logger.info("\n" + "="*60)
    logger.info("🧪 测试场景 3：产品类表格（不同列名）")
    logger.info("="*60)
    
    # 模拟 LLM 返回的结果（产品类表格）
    llm_response = {
        "has_table": True,
        "table_type": "structured",
        "columns": ["品名", "规格", "材质", "产地", "仓库", "价格"],
        "rows": [
            {"品名": "钢管", "规格": "Φ10*1.5", "材质": "碳钢", "产地": "天津", "仓库": "库房A", "价格": "150元/支"},
            {"品名": "螺栓", "规格": "M8*20", "材质": "不锈钢", "产地": "浙江", "仓库": "库房B", "价格": "2元/个"},
            {"品名": "铜片", "规格": "1mm", "材质": "紫铜", "产地": "广东", "仓库": "库房C", "价格": "50元/kg"}
        ],
        "notes": ""
    }
    
    logger.info("📊 LLM 识别结果:")
    logger.info(f"  - 表格: {llm_response['has_table']}")
    logger.info(f"  - 列名: {llm_response['columns']}")
    logger.info(f"  - 行数: {len(llm_response['rows'])}")
    
    # 1. 表格结构检测
    logger.info("\n[步骤 1] 检测表格结构...")
    structure = TableStructureDetector.detect_structure(llm_response)
    assert structure is not None, "表格结构检测失败"
    assert structure['has_table'] == True, "应识别到表格"
    logger.info("✓ 表格结构检测成功")
    
    # 2. 数据规范化
    logger.info("\n[步骤 2] 规范化数据...")
    normalized = TableStructureDetector.normalize_data(structure)
    assert len(normalized) == 3, "应有 3 条数据"
    logger.info(f"✓ 数据规范化成功，{len(normalized)} 条记录")
    
    # 3. 数据清洗
    logger.info("\n[步骤 3] 清洗数据...")
    cleaned = DataValidator.validate_and_clean(
        normalized,
        enable_dedup=True,
        columns=structure['columns']
    )
    assert len(cleaned) > 0, "清洗后应有数据"
    logger.info(f"✓ 数据清洗成功，{len(cleaned)} 条有效记录")
    
    # 4. 生成 Excel
    logger.info("\n[步骤 4] 生成 Excel...")
    excel_gen = ExcelGenerator()
    excel_path = excel_gen.generate(
        cleaned,
        source_name="测试场景3_产品类",
        columns=structure['columns']
    )
    assert excel_path is not None, "Excel 生成失败"
    assert os.path.exists(excel_path), f"Excel 文件不存在: {excel_path}"
    logger.info(f"✓ Excel 生成成功: {excel_path}")
    
    return True


if __name__ == '__main__':
    logger.info("\n" + "="*60)
    logger.info("🚀 开始测试动态列名功能")
    logger.info("="*60)
    
    try:
        # 运行所有测试
        test_scenario_1()
        test_scenario_2()
        test_scenario_3()
        
        logger.info("\n" + "="*60)
        logger.info("✅ 所有测试通过！")
        logger.info("="*60)
        logger.info("\n所有修改已完成且验证成功！")
        logger.info("主要改进:")
        logger.info("  1. ✓ 支持动态列名识别")
        logger.info("  2. ✓ 支持无列名表格处理")
        logger.info("  3. ✓ 自动列名与数据对应")
        logger.info("  4. ✓ Excel 格式正确生成")
        
    except AssertionError as e:
        logger.error(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
