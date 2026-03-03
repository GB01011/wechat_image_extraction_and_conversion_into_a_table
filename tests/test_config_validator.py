"""
单元测试：配置验证模块
"""

import unittest
import sys
import os
import tempfile

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config_validator import ConfigValidator


class TestConfigValidator(unittest.TestCase):
    """配置验证模块单元测试"""
    
    def test_valid_config(self):
        """测试有效配置"""
        config = {
            "wechat": {
                "listen_list": ["文件传输助手"],
                "save_pic_dir": "data/temp_images"
            },
            "output": {
                "excel_dir": "data/output_excel"
            },
            "llm": {
                "api_key": "sk-actually-valid-key",
                "base_url": "https://api.example.com/v1",
                "model_name": "qwen-vl-plus"
            }
        }
        # 应该通过验证（不抛异常）
        try:
            ConfigValidator.validate(config)
        except ValueError as e:
            self.fail(f"有效配置不应该抛出异常: {e}")
    
    def test_missing_wechat_config(self):
        """测试缺少微信配置"""
        config = {
            "output": {"excel_dir": "data/output"},
            "llm": {"api_key": "sk-key", "base_url": "https://api.example.com", "model_name": "model"}
        }
        with self.assertRaises(ValueError):
            ConfigValidator.validate(config)
    
    def test_empty_listen_list(self):
        """测试空监听列表"""
        config = {
            "wechat": {
                "listen_list": [],
                "save_pic_dir": "data/temp"
            },
            "output": {"excel_dir": "data/output"},
            "llm": {"api_key": "sk-key", "base_url": "https://api.example.com", "model_name": "model"}
        }
        with self.assertRaises(ValueError):
            ConfigValidator.validate(config)
    
    def test_invalid_api_key_format(self):
        """测试无效的API Key格式"""
        config = {
            "wechat": {"listen_list": ["test"], "save_pic_dir": "data/temp"},
            "output": {"excel_dir": "data/output"},
            "llm": {
                "api_key": "sk-your-api-key-here",  # 示例值
                "base_url": "https://api.example.com",
                "model_name": "model"
            }
        }
        with self.assertRaises(ValueError):
            ConfigValidator.validate(config)
    
    def test_empty_api_key(self):
        """测试空API Key"""
        config = {
            "wechat": {"listen_list": ["test"], "save_pic_dir": "data/temp"},
            "output": {"excel_dir": "data/output"},
            "llm": {
                "api_key": "",
                "base_url": "https://api.example.com",
                "model_name": "model"
            }
        }
        with self.assertRaises(ValueError):
            ConfigValidator.validate(config)
    
    def test_invalid_base_url(self):
        """测试无效的base_url"""
        config = {
            "wechat": {"listen_list": ["test"], "save_pic_dir": "data/temp"},
            "output": {"excel_dir": "data/output"},
            "llm": {
                "api_key": "sk-valid-key",
                "base_url": "not-a-url",
                "model_name": "model"
            }
        }
        with self.assertRaises(ValueError):
            ConfigValidator.validate(config)
    
    def test_missing_model_name(self):
        """测试缺少模型名称"""
        config = {
            "wechat": {"listen_list": ["test"], "save_pic_dir": "data/temp"},
            "output": {"excel_dir": "data/output"},
            "llm": {
                "api_key": "sk-key",
                "base_url": "https://api.example.com",
                "model_name": ""
            }
        }
        with self.assertRaises(ValueError):
            ConfigValidator.validate(config)
    
    def test_directory_creation(self):
        """测试目录创建"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                "wechat": {
                    "listen_list": ["test"],
                    "save_pic_dir": os.path.join(tmpdir, "new_dir")
                },
                "output": {"excel_dir": "data/output"},
                "llm": {"api_key": "sk-key", "base_url": "https://api.example.com", "model_name": "model"}
            }
            ConfigValidator.validate(config)
            # 验证目录已创建
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "new_dir")))


if __name__ == '__main__':
    unittest.main()
