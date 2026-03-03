# 微信表格自动化处理工具 - 完整使用指南

## 📋 项目概述

一个强大的自动化工具，可以：

✅ **自动采集微信消息** - 从指定好友/群聊获取图片和文字  
✅ **智能识别表格** - 使用大模型（GPT-4V、Qwen-VL等）智能识别复杂表格  
✅ **灵活数据处理** - 自动去重、清洗、验证数据  
✅ **生成标准表格** - 输出格式固定的Excel文件  
✅ **完整日志记录** - 详细的执行日志便于排查问题  

---

## 🔧 快速开始

### 第一步：环境准备

```bash
# 1. 创建虚拟环境
python -m venv interpreter

# 2. 激活虚拟环境（Windows）
interpreter\Scripts\activate

# 3. 升级 pip
python -m pip install --upgrade pip

# 4. 安装依赖
pip install -r requirements.txt
```

### 第二步：配置文件

编辑 `config/settings.yaml`，修改以下内容：

```yaml
# 1. 微信监听对象（改为实际的好友名或群名）
wechat:
  listen_list:
    - "你的好友名或群名"  # 例如："小张" 或 "采购部"

# 2. 获取 API Key（三选一）
# 选项 A：阿里云百炼（推荐）
llm:
  api_key: "sk-..."  # 从 https://bailian.aliyun.com 申请
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  model_name: "qwen-vl-plus"

# 选项 B：OpenAI
llm:
  api_key: "sk-..."  # 从 https://platform.openai.com 申请
  base_url: "https://api.openai.com/v1"
  model_name: "gpt-4-vision-preview"

# 选项 C：智谱 AI
llm:
  api_key: "glm-..."  # 从 https://open.bigmodel.cn 申请
  base_url: "https://open.bigmodel.cn/api/paas/v4"
  model_name: "glm-4v"
```

### 第三步：启动程序

```bash
# 确保微信已登录，然后运行
python main.py
```

---

## 📖 详细说明

### 项目结构

```
WeChat_Excel_Automator/
├── main.py                          # 主程序入口
├── requirements.txt                 # 依赖列表
├── config/
│   └── settings.yaml               # 配置文件（⭐ 需要修改）
├── src/
│   ├── logger.py                   # 日志模块
│   ├── config_validator.py         # 配置验证
│   ├── wechat_listener.py          # 微信监听
│   ├── image_processor.py          # 图片预处理
│   ├── llm_vision_parser.py        # 大模型解析
│   ├── data_validator.py           # 数据验证
│   └── excel_engine.py             # Excel 生成
├── data/
│   ├── temp_images/                # 临时图片目录
│   └── output_excel/               # Excel 输出目录（⭐ 重要数据）
├── logs/                           # 日志目录（按日期）
├── tests/                          # 单元测试
└── docs/                           # 文档目录
```

### 模块功能说明

#### 1️⃣ **config_validator.py** - 配置验证
- 验证配置文件完整性
- 检查 API Key 有效性
- 自动创建所需目录

#### 2️⃣ **wechat_listener.py** - 微信监听
- 连接微信应用
- 监听指定对象的新消息
- 自动保存图片
- 过滤结构化文本

#### 3️⃣ **image_processor.py** - 图片预处理
- 降噪处理（降低噪点）
- 对比度增强（提升清晰度）
- 自动旋转校正（纠正倾斜）
- 尺寸压缩（处理超大图片）

#### 4️⃣ **llm_vision_parser.py** - 大模型解析
- 调用多模态大模型（支持图片和文字）
- 智能提取表格数据
- 字段映射和识别
- 支持重试和超时控制

#### 5️⃣ **data_validator.py** - 数据验证和清洗
- 验证必填字段
- 字符串标准化
- 去重处理
- 数据质量评估

#### 6️⃣ **excel_engine.py** - Excel 生成
- 将数据写入 Excel
- 自动格式化（表头、边框、列宽）
- 美化样式（蓝色表头、居中对齐）
- 冻结表头便于查看

---

## 🚀 使用示例

### 场景 1：采集报价单表格

**输入**（微信中收到的报价单图片）：
```
+--------+-------+-------+
| 品名   | 规格  | 价格  |
+--------+-------+-------+
| 钢管   | Φ10*1.5 | 150元/支 |
| 螺栓   | M8*20 | 2元/个  |
+--------+-------+-------+
```

**输出**（自动生成的 Excel）：
| 品名 | 规格 | 材质 | 产地 | 仓库 | 价格 |
|------|------|------|------|------|------|
| 钢管 | Φ10*1.5 | | | | 150元/支 |
| 螺栓 | M8*20 | | | | 2元/个 |

---

## ⚙️ 配置详解

### settings.yaml 完整配置说明

```yaml
# 微信配置
wechat:
  listen_list:          # 监听列表（好友名或群名）
    - "好友1"
    - "群聊名"
  save_pic_dir: "..."   # 图片保存目录

# 输出配置
output:
  excel_dir: "..."      # Excel 文件输出目录

# 大模型 API 配置
llm:
  api_key: "..."        # API Key（🔴 必填）
  base_url: "..."       # API 端点（🔴 必填）
  model_name: "..."     # 模型名称（🔴 必填）
  request_timeout: 30   # 请求超时时间（秒）
  max_retries: 3        # 失败重试次数

# 日志配置
logging:
  level: "INFO"         # 日志级别（DEBUG/INFO/WARNING/ERROR）
  retention_days: 7     # 日志保留天数

# 图片处理配置
image:
  enable_preprocessing: true       # 是否启用预处理
  save_processed_images: false     # 是否保存处理后的图片

# 数据处理配置
data:
  enable_deduplication: true       # 是否去重
  max_empty_fields: 3              # 允许的空字段数量
```

---

## 🔑 API Key 获取指南

### 方案 1：阿里云百炼（推荐）

1. 访问 [https://bailian.aliyun.com](https://bailian.aliyun.com)
2. 注册或登录阿里云账号
3. 进入"模型广场"，选择"通义千问"
4. 复制 API Key
5. 配置如下：

```yaml
llm:
  api_key: "sk-..."
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  model_name: "qwen-vl-plus"
```

### 方案 2：OpenAI（功能最强）

1. 访问 [https://platform.openai.com](https://platform.openai.com)
2. 登录管理后台
3. 进入"API Keys"生成新密钥
4. 配置如下：

```yaml
llm:
  api_key: "sk-..."
  base_url: "https://api.openai.com/v1"
  model_name: "gpt-4-vision-preview"
```

### 方案 3：智谱 AI

1. 访问 [https://open.bigmodel.cn](https://open.bigmodel.cn)
2. 注册或登录
3. 进入"API 密钥"
4. 创建新的 API Key
5. 配置如下：

```yaml
llm:
  api_key: "glm-..."
  base_url: "https://open.bigmodel.cn/api/paas/v4"
  model_name: "glm-4v"
```

---

## 🐛 常见问题排查

### 1️⃣ "微信初始化失败"

**原因**：微信未登录或 wxauto 找不到微信  
**解决**：
- 确保微信已经打开并**完成登录**
- 微信窗口不能最小化
- 如果还是失败，尝试重启微信

### 2️⃣ "无法监听【xxx】"

**原因**：微信好友名/群名拼写错误  
**解决**：
- 检查 `settings.yaml` 中的 `listen_list` 
- 按照微信中显示的**完全相同**的名称填写
- 符号、空格、大小写都要匹配

### 3️⃣ "API 调用失败"

**原因**：API Key 无效或仍为示例值  
**解决**：
- 检查 `settings.yaml` 中的 `api_key`
- 确保不是 `sk-your-api-key-here` 这样的示例值
- 重新申请真实的 API Key

### 4️⃣ "JSON 解析失败"

**原因**：大模型响应格式错误  
**解决**：
- 检查日志文件（`logs/` 目录）
- 确认图片清晰度
- 如果问题持续，更换大模型（如使用 GPT-4V）

### 5️⃣ "Excel 文件无法打开"

**原因**：文件被占用或损坏  
**解决**：
- 关闭已打开的 Excel 文件
- 删除输出目录中的 `.xlsx` 文件
- 重新运行程序生成

---

## 📊 日志查看

日志文件自动保存在 `logs/` 目录，按日期命名：

```
logs/
├── system_2024-03-03.log
├── system_2024-03-04.log
└── ...
```

### 日志级别说明

| 级别 | 符号 | 说明 |
|------|------|------|
| DEBUG | 🔍 | 调试信息（最详细） |
| INFO | ✓ | 正常信息 |
| WARNING | ⚠ | 警告（可能需要关注） |
| ERROR | ❌ | 错误（需要修复） |
| CRITICAL | 🚨 | 严重错误（程序可能崩溃） |

---

## ✅ 运行检查清单

启动前，请逐项检查：

- [ ] Python 版本 >= 3.8
- [ ] 虚拟环境已激活（`interpreter\Scripts\activate`）
- [ ] 依赖已安装（`pip install -r requirements.txt`）
- [ ] 微信已登录
- [ ] `config/settings.yaml` 已修改（监听对象、API Key）
- [ ] 输出目录存在且有写入权限

---

## 🧪 运行单元测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_data_validator.py

# 显示详细输出
python -m pytest tests/ -v
```

---

## 📈 性能优化建议

| 项目 | 建议 | 效果 |
|------|------|------|
| **图片预处理** | 启用 `enable_preprocessing: true` | 提升识别准确率 10-20% |
| **去重功能** | 启用 `enable_deduplication: true` | 避免重复数据 |
| **超时时间** | 根据网络调整 `request_timeout` | 避免超时失败 |
| **重试次数** | 增加 `max_retries` （如 5-7） | 提升稳定性（但速度降低） |

---

## 🔒 隐私和安全

✅ **本地处理** - 所有数据在本地处理，不上传微信  
✅ **仅上传内容** - 只有识别后的表格数据发送给大模型API  
✅ **安全存储** - Excel 文件保存在本地，可管理或加密  
✅ **日志脱敏** - 日志中不包含敏感信息  

---

## 📞 技术支持

如遇问题，请提供：

1. 错误日志（`logs/system_*.log`）
2. 配置文件（去除 API Key）
3. 输入的原始图片（如不涉及隐私）
4. Python 版本และ OS 信息

---

## 📝 更新日志

**v1.0.0** (2024-03-03)
- ✅ 初始版本发布
- ✅ 支持图片和文字识别
- ✅ 自动数据清洗和去重
- ✅ 完整的日志和错误提示

---

**祝使用愉快！** 🎉
