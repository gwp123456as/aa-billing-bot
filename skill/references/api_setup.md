# API 配置说明

## 支持的 API

AA记账机器人支持任何 OpenAI 兼容的 API。以下是目前推荐的免费选项：

## 1. DeepSeek（推荐）

- **注册地址**: https://platform.deepseek.com/
- **免费额度**: 注册即送 500 万 Token
- **模型名称**: `deepseek-chat`
- **API 地址**: `https://api.deepseek.com/v1`
- **特点**: 中文理解能力强，免费额度充足，响应速度快

### 配置

```bash
# Windows
set AA_BOT_API_KEY=sk-your-deepseek-key
set AA_BOT_API_BASE=https://api.deepseek.com/v1
set AA_BOT_MODEL=deepseek-chat

# Linux/Mac
export AA_BOT_API_KEY=sk-your-deepseek-key
export AA_BOT_API_BASE=https://api.deepseek.com/v1
export AA_BOT_MODEL=deepseek-chat
```

## 2. 通义千问

- **注册地址**: https://dashscope.aliyun.com/
- **免费额度**: 学生认证可领免费额度
- **模型名称**: `qwen-turbo`
- **API 地址**: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- **特点**: 阿里出品，国内访问稳定

### 配置

```bash
set AA_BOT_API_KEY=sk-your-qwen-key
set AA_BOT_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
set AA_BOT_MODEL=qwen-turbo
```

## 3. 豆包

- **注册地址**: https://www.volcengine.com/product/doubao
- **免费额度**: 新用户免费体验
- **模型名称**: `doubao-pro-32k`
- **API 地址**: `https://ark.cn-beijing.volces.com/api/v3`
- **特点**: 字节跳动出品，响应快

### 配置

```bash
set AA_BOT_API_KEY=your-doubao-key
set AA_BOT_API_BASE=https://ark.cn-beijing.volces.com/api/v3
set AA_BOT_MODEL=doubao-pro-32k
```

## 环境变量一览

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `AA_BOT_API_KEY` | （空） | API 密钥（必填，否则离线模式） |
| `AA_BOT_API_BASE` | `https://api.deepseek.com/v1` | API 基础地址 |
| `AA_BOT_MODEL` | `deepseek-chat` | 模型名称 |
| `AA_BOT_USER` | `我` | 当前用户名 |

## 验证配置

配置完成后，运行以下命令检查状态：

```bash
python skill/scripts/aa_bot.py status
```

如果显示 "API Key: ✅ 已配置"，则配置成功。

## 安全说明

- API Key 仅存储在环境变量中，不会写入代码或配置文件
- 程序不会上传任何用户数据到第三方服务
- 所有账单数据存储在本地 JSON 文件中
- API 调用仅用于：解析自然语言、生成催款消息、生成汇总报告
