#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""端到端集成测试"""

import yaml
from src.config_validator import ConfigValidator
from main import create_listener

def test_integration():
    print("=" * 60)
    print("开始端到端集成测试")
    print("=" * 60)
    
    # 1. 加载配置
    print("\n[步骤 1/3] 加载配置文件...")
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print("✓ 配置已加载，包含以下部分：")
    print(f"  - 模式: {config.get('wechat', {}).get('mode')}")
    print(f"  - 监听目录: {config.get('wechat', {}).get('listen_dir')}")
    
    # 2. 验证配置
    print("\n[步骤 2/3] 验证配置...")
    ConfigValidator.validate(config)
    print("✓ 配置验证通过！")
    
    # 3. 创建监听器
    print("\n[步骤 3/3] 创建监听器...")
    listener = create_listener(config)
    print(f"✓ 监听器创建成功！")
    print(f"  - 类型: {type(listener).__name__}")
    print(f"  - 监听目录: {listener.watch_dir}")
    
    print("\n" + "=" * 60)
    print("✅ 端到端测试完全成功！")
    print("=" * 60)

if __name__ == '__main__':
    test_integration()
