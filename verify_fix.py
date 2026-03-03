#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证修复后的程序"""
import sys
import os

# 改变工作目录
os.chdir(r'D:\acceptance_file\one\WeChat_Excel_Automator')

# 添加 src 到路径
sys.path.insert(0, '.')

try:
    import yaml
    from src.config_validator import ConfigValidator
    from main import create_listener
    
    print("=" * 60)
    print("✓ 所有导入成功")
    print("=" * 60)
    
    # 1. 加载配置
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    print("✓ YAML 配置加载成功")
    
    # 2. 验证配置
    ConfigValidator.validate(config)
    print("✓ 配置验证通过")
    
    # 3. 创建监听器
    listener = create_listener(config)
    print(f"✓ 监听器创建成功：{type(listener).__name__}")
    print(f"✓ 监听目录：{listener.watch_dir}")
    
    print("=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ 错误：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
