# API密钥配置说明

本项目支持多种方式配置API密钥，按优先级排序：

## 方式1：使用 .env 文件（推荐）

在项目根目录创建 `.env` 文件，填入你的API密钥：

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，填入你的密钥
```

编辑 `.env` 文件：

```env
# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Moonshot Kimi
MOONSHOT_API_KEY=your_moonshot_api_key_here

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

**优点：**
- 配置持久化，重启后依然有效
- 支持多种模型同时配置
- 可在Web UI中查看和修改

## 方式2：使用环境变量

在系统环境变量中设置：

**Linux/Mac:**
```bash
export ANTHROPIC_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
export MOONSHOT_API_KEY="your_key"
export DEEPSEEK_API_KEY="your_key"
```

**Windows (CMD):**
```cmd
set ANTHROPIC_API_KEY=your_key
set OPENAI_API_KEY=your_key
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="your_key"
$env:OPENAI_API_KEY="your_key"
```

**优点：**
- 安全性高，不会意外提交到Git
- 适合服务器部署

## 方式3：使用 Web UI 界面

1. 启动应用：`streamlit run app.py`
2. 进入 **⚙️ 系统设置** 页面
3. 选择模型提供商（如 Kimi 2.5）
4. 输入API密钥
5. 点击 **💾 保存设置**

密钥会自动保存到 `.env` 文件。

**优点：**
- 无需编辑文件
- 可视化操作
- 实时测试连接

## 获取API密钥

### Anthropic (Claude)
- 访问：https://console.anthropic.com/
- 注册账号 → API Keys → Create Key

### OpenAI (GPT)
- 访问：https://platform.openai.com/
- 注册账号 → API Keys → Create new secret key

### Moonshot (Kimi)
- 访问：https://platform.moonshot.cn/
- 注册账号 → API Keys → 创建API Key

### DeepSeek
- 访问：https://platform.deepseek.com/
- 注册账号 → API Keys → 创建API Key

## 配置文件示例

`.env.example` 提供了完整的配置模板，包含：
- 所有支持的模型密钥变量
- 默认模型设置
- 温度和Token数配置

复制后根据需要填写即可。

## 安全提醒

⚠️ **重要：**
1. `.env` 文件包含敏感信息，**请勿提交到Git仓库**
2. 项目已配置 `.gitignore` 忽略 `.env` 文件
3. 不要将密钥硬编码在代码中
4. 定期轮换API密钥以提高安全性

## 验证配置

启动应用后，在 **⚙️ 系统设置** 页面：
1. 查看API密钥状态（✓ 已配置 / ✗ 未配置）
2. 点击 **🧪 测试模型连接** 验证密钥是否有效

如果显示 "✅ 模型连接成功"，说明配置正确！
