# 🎯 本地文件模式快速入门指南

## 📋 项目改造完成

已将项目改造为**完全支持本地文件输入**，彻底解决 `wxauto` 依赖问题！

### 改造内容

| 文件 | 改造说明 |
|------|--------|
| `src/wechat_listener.py` | ✅ 新增 `LocalFileListener` 类（本地文件监听器） |
| `main.py` | ✅ 支持两种模式自动切换（根据配置选择） |
| `requirements.txt` | ✅ 移除 wxauto 强制依赖，改为可选 |
| `config/settings.yaml` | ✅ 新增 `mode` 配置，支持 local 和 wechat 两种模式 |

---

## 🚀 快速开始（5分钟）

### 第1步：安装依赖

```bash
# 进入虚拟环境（如果还未激活）
cd d:\acceptance_file\one\WeChat_Excel_Automator
interpreter\Scripts\activate

# 安装所有依赖（仅需一次）
pip install --no-cache-dir -r requirements.txt
```

**预期结果**：所有包都会成功安装，不会再报 `wxauto` 相关错误

### 第2步：配置 API Key

编辑 `config/settings.yaml`，在第46行填入真实的 API Key：

```yaml
llm:
  api_key: "你从阿里云/OpenAI/智谱申请的真实API Key"
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"  # 保持默认
  model_name: "qwen-vl-plus"  # 根据实际服务商修改
```

**API Key 申请指南**：
- **阿里云通义千问**（推荐）：https://bailian.aliyun.com
- OpenAI GPT-4V：https://platform.openai.com
- 智谱GLM-4V：https://open.bigmodel.cn

### 第3步：准备测试图片

1. 找一张包含表格或结构化数据的图片
2. 放到这个目录：`d:\acceptance_file\one\WeChat_Excel_Automator\data\temp_images\`
3. 支持格式：`.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`, `.webp`

**示例**：
```
data/temp_images/
├── 表格1.jpg          ← 放这里
├── 单据.png          ← 或这里
└── 报价单.webp       ← 等等
```

### 第4步：运行程序

```bash
# 确保虚拟环境已激活
python main.py
```

**输出示例**：
```
============================================================
微信表格自动化处理工具启动
============================================================
✓ 配置文件加载成功

【监听模式】本地文件模式（推荐）
【监听目录】data\temp_images
【说明】请将要处理的图片放到此目录
✓ 本地文件监听器初始化成功

正在初始化其他模块...
✓ 大模型解析模块初始化完成
✓ 图片处理模块初始化完成
✓ Excel 生成模块初始化完成
------------------------------------------------------------
系统初始化成功！开始监听消息...

💡 本地文件模式提示：
   请将要处理的图片放到: data\temp_images
   支持的图片格式: .jpg, .jpeg, .png, .bmp, .gif, .webp
   支持的文本格式: .txt
```

### 第5步：查看结果

处理完成后，Excel 文件会自动生成在：
```
data/output_excel/
├── 表格1_20240303_120000.xlsx
├── 单据_20240303_120100.xlsx
└── ...
```

---

## 📁 两种监听模式详解

### 模式 1️⃣ 本地文件模式（推荐）✨

**配置**：
```yaml
wechat:
  mode: "local"  # 选择本地模式
  listen_dir: "data/temp_images"
```

**特点**：
- ✅ **无需依赖** wxauto（无兼容性问题）
- ✅ **易于测试** 只需放图片到文件夹
- ✅ **稳定可靠** 不依赖微信客户端
- ✅ **支持批处理** 放多张图片自动处理
- ✅ **支持文本文件** `.txt` 格式

**工作流**：
```
图片放入 data/temp_images
         ↓
程序自动扫描
         ↓
自动预处理图片
         ↓
调用大模型解析
         ↓
验证和清洗数据
         ↓
生成 Excel 文件
         ↓
输出到 data/output_excel
```

### 模式 2️⃣ 微信直连模式（可选）

**配置**：
```yaml
wechat:
  mode: "wechat"  # 选择微信模式
  listen_list:
    - "文件传输助手"
    - "实际的群聊名"
  save_pic_dir: "data/temp_images"
```

**启用此模式需要**：
```bash
# 取消注释 requirements.txt 中的这一行
pip install wxauto
```

**注意**：
- ⚠️ 此模式较难配置（wxauto 兼容性问题）
- ⚠️ 仅在本地文件模式无法满足需求时才使用
- ⚠️ 需要微信客户端处于登录状态

---

## 🔍 故障排除

### 问题 1：`ModuleNotFoundError: No module named 'opencv_python'`

**解决**：
```bash
pip install --no-cache-dir opencv-python
```

### 问题 2：`ModuleNotFoundError: No module named 'openai'`

**解决**：
```bash
pip install --no-cache-dir openai
```

### 问题 3：没有看到程序处理图片

**排查**：
1. ✓ 检查图片是否在正确目录：`data/temp_images`
2. ✓ 检查配置 `wechat.mode` 是否为 `local`
3. ✓ 检查图片格式是否为支持的格式（`.jpg/.png/.webp` 等）
4. ✓ 查看日志文件：`logs/system_*.log`

### 问题 4：API 请求超时

**解决**：
```yaml
llm:
  request_timeout: 60  # 改为 60 秒（从默认 30 秒）
  max_retries: 5       # 增加重试次数
```

### 问题 5：看不到输出的 Excel 文件

**检查**：
1. ✓ Excel 输出目录是否存在：`data/output_excel`
2. ✓ 查看程序日志：`logs/system_*.log`
3. ✓ 确认 API Key 配置正确（不是示例值）

---

## 📊 整个流程概览

```
┌─────────────────────────────────────────────────────┐
│  开始使用本地文件模式                               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. pip install -r requirements.txt                 │
│     （仅需一次，快速完成）                          │
│                                                     │
│  2. 配置 config/settings.yaml                      │
│     （修改 API Key）                                │
│                                                     │
│  3. 放置测试图片到 data/temp_images               │
│     （支持批量）                                    │
│                                                     │
│  4. 运行 python main.py                             │
│     （程序自动扫描和处理）                          │
│                                                     │
│  5. 查看结果 data/output_excel/                    │
│     （Excel 文件自动生成）                          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## ✅ 验证安装成功

运行这个检查脚本：

```bash
python check_environment.py
```

**完全成功的输出**应该显示：
```
总体: 6/6 项通过 ✓
```

---

## 🎓 下一步

### 如果一切正常：
- 📸 放入更多测试图片，验证批处理能力
- 🔧 调整 `config/settings.yaml` 中的参数优化性能
- 📝 查看生成的 Excel 文件，验证数据准确性
- 💾 考虑定期备份 `data/output_excel` 中的文件

### 如果遇到问题：
- 📋 查看日志文件：`logs/system_YYYY-MM-DD.log`
- 🔍 增加日志级别来调试：`logging.level: "DEBUG"`
- 💬 检查 API Key 是否有效（尝试用官方网站测试）

---

## 📞 获取帮助

### 常见问题
1. **API Key 格式错误**：确保不是示例值 `sk-your-api-key`
2. **超时错误**：增加 `request_timeout` 到 60 或以上
3. **图片无法识别**：确保图片清晰，试试启用图片预处理

### 调试步骤
1. 启用 DEBUG 日志：修改 `logging.level: "DEBUG"`
2. 查看最新日志：`logs/system_*.log`
3. 测试单个图片而不是批量

---

## 🎉 恭喜！

你现在有一个**完全独立、无需微信客户端的表格处理工具**！

**享受自动化的便利！** 🚀
