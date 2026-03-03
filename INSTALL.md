# 安装和环境配置指南

## 系统要求

| 项目 | 要求 |
|------|------|
| **操作系统** | Windows 7+ （其他 OS 可能需要调整） |
| **Python** | 3.8+ |
| **微信** | PC 版（已登录） |
| **网络** | 能正常访问大模型 API |

---

## 第一步：安装 Python

### 验证 Python 版本

```bash
python --version
```

应显示 `Python 3.8.0` 或更高版本。

### 如果未安装 Python

1. 访问 [python.org](https://www.python.org/downloads/)
2. 下载 Python 3.10+
3. **重要**：勾选 "Add Python to PATH"
4. 点击 "Install Now"

---

## 第二步：创建虚拟环境

虚拟环境用于隔离项目依赖，避免与系统其他项目冲突。

```bash
# 进入项目目录
cd d:\acceptance_file\one\WeChat_Excel_Automator

# 创建虚拟环境（名为 interpreter）
python -m venv interpreter

# 激活虚拟环境（Windows）
interpreter\Scripts\activate

# ✓ 成功激活后，命令行前会出现 (interpreter)
```

### MacOS/Linux 激活虚拟环境

```bash
source interpreter/bin/activate
```

---

## 第三步：升级 pip

```bash
python -m pip install --upgrade pip
```

---

## 第四步：安装依赖

```bash
# 确保虚拟环境已激活，然后运行：
pip install -r requirements.txt
```

### 依赖清单

| 包名 | 版本 | 用途 |
|------|------|------|
| wxauto | 3.9.53.1 | 微信自动化 |
| pandas | 2.2.0 | 数据处理 |
| openpyxl | 3.1.2 | Excel 操作 |
| pyyaml | 6.0.1 | 配置文件解析 |
| loguru | 0.7.2 | 日志记录 |
| openai | 1.12.0 | 大模型 API 客户端 |
| opencv-python | 4.8.1.78 | 图片处理 |
| numpy | 1.24.3 | 数值计算 |
| Pillow | 10.1.0 | 图片库 |

### 如果安装失败

```bash
# 使用清华源加速
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或单独安装有问题的包
pip install wxauto --upgrade
pip install opencv-python
```

---

## 第五步：配置文件设置

### 1. 编辑配置文件

用文本编辑器打开 `config/settings.yaml`：

```
WeChat_Excel_Automator/
└── config/
    └── settings.yaml  ← 用记事本或 VS Code 打开
```

### 2. 修改微信监听对象

找到 `wechat` 部分，修改为你的微信好友或群名：

```yaml
wechat:
  listen_list:
    - "你真实的好友名"  # 例如："小张" 或 "张三"
    - "你真实的群name"   # 例如："采购部" 或 "销售组"
```

**⚠️ 重要**：名称必须与微信中显示的**完全相同**，包括：
- 大小写
- 符号
- 空格

### 3. 配置 API Key

根据选择的大模型服务，填入对应的 API Key：

#### 选项 A：阿里云百炼（推荐）

```bash
# 1. 访问 https://bailian.aliyun.com
# 2. 注册登录，进入"API 密钥"
# 3. 复制 API Key

# 在 settings.yaml 中填入：
llm:
  api_key: "sk-你申请的key"
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  model_name: "qwen-vl-plus"
```

#### 选项 B：OpenAI（功能最强，需付费）

```bash
# 1. 访问 https://platform.openai.com
# 2. 登录，进入 "API Keys"
# 3. 点击 "Create new secret key"
# 4. 复制密钥

# 在 settings.yaml 中填入：
llm:
  api_key: "sk-你申请的key"
  base_url: "https://api.openai.com/v1"
  model_name: "gpt-4-vision-preview"
```

#### 选项 C：智谱 AI

```bash
# 1. 访问 https://open.bigmodel.cn
# 2. 登录，进入 "API 密钥管理"
# 3. 新建 API 密钥
# 4. 复制

# 在 settings.yaml 中填入：
llm:
  api_key: "glm-你申请的key"
  base_url: "https://open.bigmodel.cn/api/paas/v4"
  model_name: "glm-4v"
```

---

## 第六步：验证安装

```bash
# 确保虚拟环境已激活，运行：
python -c "
import yaml, pandas, cv2, loguru
print('✓ 所有依赖已正确安装')
"
```

如果没有错误，说明安装成功！

---

## 第七步：启动程序

```bash
# 确保虚拉环境已激活
# 确保微信已登录
# 然后运行：

python main.py
```

### 正常启动日志示例

```
2024-03-03 10:30:45 | INFO     | ============================================================
2024-03-03 10:30:45 | INFO     | 微信表格自动化处理工具启动
2024-03-03 10:30:45 | INFO     | ============================================================
2024-03-03 10:30:46 | INFO     | ✓ 配置文件加载成功
2024-03-03 10:30:46 | INFO     | 开始验证配置文件...
2024-03-03 10:30:46 | INFO     | ✓ 微信监听列表: 文件传输助手, 报价测试群
2024-03-03 10:30:47 | INFO     | 正在连接微信...
2024-03-03 10:30:48 | INFO     | ✓ 微信连接成功
2024-03-03 10:30:48 | INFO     | ✓ 成功添加监听: 【文件传输助手】
2024-03-03 10:30:48 | INFO     | ✓ 成功添加监听: 【报价测试群】
2024-03-03 10:30:48 | INFO     | ✓ 系统初始化完成，开始持续监听消息...
```

---

## 故障排查

### 问题 1：`命令找不到: python`

**原因**：Python 未添加到 PATH  
**解决**：

```bash
# 使用完整路径运行
C:\Python310\python.exe main.py

# 或重新安装 Python，勾选 "Add Python to PATH"
```

### 问题 2：`ModuleNotFoundError: No module named 'wxauto'`

**原因**：依赖未安装或虚拟环境未激活  
**解决**：

```bash
# 确保虚拟环境已激活（会显示 (interpreter) 提示符）
interpreter\Scripts\activate

# 重新安装依赖
pip install -r requirements.txt
```

### 问题 3：`wxauto 版本过旧`

**原因**：installed wxauto 版本不兼容  
**解决**：

```bash
# 升级 wxauto
pip install --upgrade wxauto

# 如果仍有问题，卸载后重装
pip uninstall wxauto
pip install wxauto==3.9.53.1
```

### 问题 4：权限拒绝错误

**原因**：输出目录权限不足  
**解决**：

```bash
# 手动创建目录并授予权限
mkdir data\output_excel
mkdir data\temp_images
```

---

## 卸载和清理

如需重新安装、卸载或跨项目转移：

```bash
# 1. 删除虚拟环境
rm -r interpreter  # Linux/Mac
rmdir /s interpreter  # Windows

# 2. 删除缓存
rm -r __pycache__
rm -r .pytest_cache

# 3. 重新创建虚拟环境
python -m venv interpreter
interpreter\Scripts\activate
pip install -r requirements.txt
```

---

## 在 PyCharm 中配置

### 1. 打开项目

- 文件 → 打开 → 选择项目目录

### 2. 配置解释器

- 文件 → 设置 → 项目 → Python 解释器
- 点击右上角齿轮 → 添加
- 选择"现有环境"
- 浏览选择 `interpreter\Scripts\python.exe`

### 3. 运行程序

- 右键点击 `main.py`
- 选择 "运行 'main.py'"

---

## 在 VS Code 中配置

### 1. 安装扩展

- 在 VS Code 中安装 "Python" 扩展（Microsoft）

### 2. 选择解释器

- `Ctrl+Shift+P` 打开命令面板
- 搜索 "Python: Select Interpreter"
- 选择 `./interpreter/Scripts/python.exe`

### 3. 运行程序

- 点击右上角的"运行"按钮
- 或按 `F5` 使用调试器

---

**安装完成后，即可启动程序！** 🚀
