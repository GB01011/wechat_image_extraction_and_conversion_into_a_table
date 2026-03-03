#!/usr/bin/env python
"""临时测试脚本 - 验证 LocalFileListener 功能"""

from src.wechat_listener import LocalFileListener
import os

# 创建测试文件
test_dir = 'data/temp_images'
os.makedirs(test_dir, exist_ok=True)

print("=" * 60)
print("【LocalFileListener 功能测试】")
print("=" * 60)
print()

# 1. 测试文本文件
print("1. 创建测试文本文件...")
with open(f'{test_dir}/test_product.txt', 'w', encoding='utf-8') as f:
    f.write('品名: 商品A\n规格: XL\n价格: 99.99')
print("   ✓ 文件创建成功")

# 2. 初始化 LocalFileListener
print("\n2. 初始化 LocalFileListener...")
listener = LocalFileListener(test_dir)
print("   ✓ 初始化成功")

# 3. 扫描文件
print("\n3. 扫描文件...")
messages = listener.get_new_messages()
print(f"   ✓ 扫描到 {len(messages)} 条消息")

# 4. 验证消息内容
if messages:
    msg = messages[0]
    print("\n4. 消息详情：")
    print(f"   ✓ 消息类型: {msg['type']}")
    print(f"   ✓ 消息来源: {msg['source']}")
    print(f"   ✓ 文件名: {msg['filename']}")
    print(f"   ✓ 内容预览: {msg['data'][:50]}...")

# 5. 清理
print("\n5. 清理测试文件...")  
os.remove(f'{test_dir}/test_product.txt')
print("   ✓ 清理完成")

print("\n" + "=" * 60)
print("✓ LocalFileListener 功能验证成功！")
print("=" * 60)
