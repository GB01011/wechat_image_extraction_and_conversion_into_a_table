#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复 main.py 中的参数名"""

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换错误的参数
original = 'listener = LocalFileListener(listen_dir=listen_dir)'
fixed = 'listener = LocalFileListener(watch_dir=listen_dir)'

if original in content:
    content = content.replace(original, fixed)
    
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('✓ main.py 已修复')
else:
    print('错误：未找到要替换的文本')
    print(f'  搜索: {repr(original)}')

# 验证
with open('main.py', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if 'LocalFileListener(' in line:
            print(f'Line {i}: {line.strip()}')
