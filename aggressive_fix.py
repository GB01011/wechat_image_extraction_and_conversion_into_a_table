#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""强制修复 main.py"""

import os

file_path = r'D:\acceptance_file\one\WeChat_Excel_Automator\main.py'

# 读取原文件
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 强制找到包含 listen_dir=listen_dir 的行
modified = False
for i, line in enumerate(lines):
    if 'LocalFileListener(listen_dir=listen_dir)' in line:
        print(f'找到错误行在第 {i+1} 行')
        print(f'原始: {repr(line.strip())}')
        lines[i] = line.replace('LocalFileListener(listen_dir=listen_dir)', 
                                'LocalFileListener(watch_dir=listen_dir)')
        print(f'修改后: {repr(lines[i].strip())}')
        modified = True

if not modified:
    print('ERROR: 未找到要修改的行！')
    exit(1)

# 强制写回文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('✓ 文件已修改并保存')

# 再次验证
with open(file_path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if 'LocalFile Listener(' in line:
            print(f'验证 Line {i}: {line.strip()}')
