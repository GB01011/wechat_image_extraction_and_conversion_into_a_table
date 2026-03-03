with open('main.py', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if 'LocalFileListener(' in line:
            print(f'Line {i}: {repr(line.strip())}')
