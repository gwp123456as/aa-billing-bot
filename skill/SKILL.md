---
name: aa-billing-bot
description: AA记账机器人——基于AI的AA制记账与催款助手。输入自然语言描述消费场景，AI自动解析金额、参与人、付款人，计算每人应付金额，并生成友好的催款消息。
version: "1.0.0"
author: AI个人系统实践
tags:
  - 记账
  - AA制
  - 生活日常
  - AI
---

# AA记账机器人 Skill

## 概述

AA记账机器人是一个基于 AI 的 AA 制记账工具。它解决的核心痛点是：

> **聚餐AA算账麻烦，有人忘付有人垫钱算不清，催钱不好意思开口。**

### AI 的核心价值

这个 Skill 中 AI 不可替代的环节：

1. **自然语言解析**：用户只需说"今天聚餐花了200，我和张三李四吃的，我付的"，AI 自动提取金额、参与人、付款人、消费描述，并理解自定义分摊比例。传统工具需要手动逐项填表。
2. **催款消息生成**：AI 根据关系亲疏、金额大小、场合，生成不尴尬的催款消息。这是传统工具做不到的——它需要"察言观色"的语言理解能力。

## 安装与配置

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置 API Key

获取免费的 DeepSeek API Key（学生可领免费额度）：

1. 访问 https://platform.deepseek.com/ 注册账号
2. 在 API Keys 页面创建 Key
3. 设置环境变量：

```bash
# Windows
set AA_BOT_API_KEY=sk-your-key-here

# Linux/Mac
export AA_BOT_API_KEY=sk-your-key-here
```

### 3. 可选配置

```bash
# 切换其他 OpenAI 兼容 API
set AA_BOT_API_BASE=https://api.openai.com/v1
set AA_BOT_MODEL=gpt-4o-mini

# 设置当前用户名（默认"我"）
set AA_BOT_USER=张三
```

## 使用方式

### 添加账单

```bash
python skill/scripts/aa_bot.py add "今天聚餐花了200，我和张三李四吃的，我付的"
```

AI 会自动解析并生成催款消息。

### 查看所有账单

```bash
python skill/scripts/aa_bot.py list
```

### 计算净结算

多笔账单汇总后，计算谁该给谁转多少钱：

```bash
python skill/scripts/aa_bot.py settle
```

### 生成催款消息

```bash
python skill/scripts/aa_bot.py remind 1 --relation 好朋友
```

### 生成汇总报告

```bash
python skill/scripts/aa_bot.py report
```

### 运行测试

```bash
python skill/scripts/aa_bot.py test
```

## 文件结构

```
skill/
├── SKILL.md              # 本文件（技能定义）
├── scripts/
│   ├── aa_bot.py          # 主入口（CLI）
│   ├── bill_parser.py     # AI 自然语言解析模块
│   ├── settlement.py      # 结算计算模块（纯算法）
│   ├── reminder_gen.py    # AI 催款消息生成模块
│   ├── storage.py          # JSON 本地存储
│   ├── config.py           # 配置管理
│   └── test_runner.py      # 测试运行器
└── references/
    ├── prompt_template.md  # AI 提示词模板
    ├── usage_guide.md      # 使用指南
    └── api_setup.md        # API 配置说明
```

## 工作流程

```
用户输入自然语言
       │
       ▼
┌─────────────────┐
│  bill_parser.py  │  ← AI 解析自然语言 → 结构化数据
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  settlement.py   │  ← 纯算法计算分摊
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ reminder_gen.py │  ← AI 生成催款消息
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   storage.py    │  ← JSON 持久化存储
└─────────────────┘
```

## 离线降级

当未配置 API Key 时，系统自动降级到离线模式：
- 使用关键词匹配进行简单解析（仅支持 "花了XX" 格式）
- 使用模板生成催款消息
- 结算计算不受影响（纯算法，不依赖AI）

## 注意事项

- API Key 存储在环境变量中，不会泄露
- 所有数据存储在本地 JSON 文件，不上传任何信息
- 结算计算使用贪心算法，保证转账次数最少
