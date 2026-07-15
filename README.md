# AA记账机器人 🤖

> 基于 AI 的 AA 制记账与催款助手

## 选题信息

| 项目 | 内容 |
|------|------|
| 选题名称 | AA记账机器人 |
| 选题来源 | AI实践场景清单 - 序号17 |
| 所属分类 | 生活日常 |
| 落地难度 | ★★★零门槛 |
| 核心痛点 | 聚餐AA算账麻烦，有人忘付有人垫钱算不清，催钱不好意思开口 |

## 功能简介

AA记账机器人通过 AI 理解自然语言描述的消费场景，自动完成：

1. **智能解析** 🧠 — 说一句"今天聚餐花了200，我和张三李四吃的，我付的"，AI 自动提取金额、参与人、付款人
2. **自动分摊** 💰 — 支持平均分摊、不均等金额、比例分摊三种模式
3. **净结算计算** 📊 — 多笔账单汇总后，贪心算法计算最少转账方案
4. **催款消息生成** 📨 — AI 根据关系亲疏生成不尴尬的催款消息，直接复制发送
5. **月度报告** 📈 — AI 生成消费汇总报告，清晰掌握谁该给谁多少钱

### AI 的核心价值

这个项目中 AI 不可替代的环节：

| 功能 | 传统方式 | AI 方式 |
|------|---------|---------|
| 账单录入 | 手动逐项填表 | 自然语言一句话搞定 |
| 催款消息 | 千篇一律的模板 | 根据关系个性化生成 |
| 汇总报告 | 手动统计 | AI 自动生成可读报告 |

> **没有 AI，自然语言解析和个性化催款消息这两个核心功能根本做不到。**

## 使用方式

### 快速开始

```bash
# 1. 安装依赖
pip install requests

# 2. 配置 API Key（获取免费Key: https://platform.deepseek.com/）
# Windows
set AA_BOT_API_KEY=sk-your-key-here
# Linux/Mac
export AA_BOT_API_KEY=sk-your-key-here

# 3. 记一笔账
python skill/scripts/aa_bot.py add "今天聚餐花了200，我和张三李四吃的，我付的"

# 4. 查看所有账单
python skill/scripts/aa_bot.py list

# 5. 计算净结算
python skill/scripts/aa_bot.py settle

# 6. 生成催款消息
python skill/scripts/aa_bot.py remind 1 --relation 好朋友

# 7. 运行测试
python skill/scripts/aa_bot.py test
```

### 完整命令列表

| 命令 | 说明 | 示例 |
|------|------|------|
| `add` | 添加账单 | `python aa_bot.py add "聚餐花了200，我和张三李四，我付的"` |
| `list` | 查看账单 | `python aa_bot.py list` |
| `settle` | 净结算 | `python aa_bot.py settle` |
| `remind` | 催款消息 | `python aa_bot.py remind 1 --relation 好朋友` |
| `report` | 汇总报告 | `python aa_bot.py report` |
| `delete` | 删除账单 | `python aa_bot.py delete 1` |
| `clear` | 清空数据 | `python aa_bot.py clear` |
| `test` | 运行测试 | `python aa_bot.py test` |
| `status` | 系统状态 | `python aa_bot.py status` |

## 项目结构

```
aa-billing-bot/
├── skill/                        # Skill 文件
│   ├── SKILL.md                  # 技能定义（含 YAML 前端配置）
│   ├── scripts/                  # 脚本/工具代码
│   │   ├── aa_bot.py             # 主入口（CLI 命令行工具）
│   │   ├── bill_parser.py        # AI 自然语言解析模块
│   │   ├── settlement.py         # 结算计算模块（贪心算法）
│   │   ├── reminder_gen.py       # AI 催款消息生成模块
│   │   ├── storage.py            # JSON 本地存储
│   │   ├── config.py             # 配置管理
│   │   └── test_runner.py        # 测试运行器
│   └── references/               # 参考文件
│       ├── prompt_template.md    # AI 提示词模板
│       ├── usage_guide.md        # 使用指南
│       └── api_setup.md          # API 配置说明
├── data/                         # 测试数据
│   ├── sample_bills.json         # 示例账单数据
│   └── test_cases.md             # 测试用例集
├── tests/                        # 测试记录
│   └── test_record.md            # 测试记录（含环境、步骤、结果）
├── iteration/                    # 迭代说明
│   └── iteration_log.md           # 迭代升级说明（5个方向）
├── requirements.txt              # Python 依赖
└── README.md                     # 本文件
```

## 技术栈

- **语言**：Python 3.10+
- **AI API**：DeepSeek（OpenAI 兼容，支持豆包/通义千问替换）
- **依赖**：requests（唯一的第三方依赖）
- **存储**：JSON 文件（零配置，无需数据库）
- **算法**：贪心算法（最少转账次数的净结算计算）

## 真实使用反馈

### 使用场景
- 聚餐AA分账（3-8人场景）
- 同事午餐AA
- 打车拼车费用
- 奶茶/咖啡不均等分摊

### AI 价值体现
1. **自然语言理解**：口语化表达如"搓了一顿"、"我垫的"、"他扫的码"都能正确解析
2. **语气调节**：同一条账单对好朋友和同事生成完全不同语气的催款消息
3. **智能汇总**：5人5笔账单，1秒计算出最少转账方案

## API 推荐

| 平台 | 免费额度 | 推荐度 | 注册地址 |
|------|---------|--------|---------|
| DeepSeek | 500万Token | ⭐⭐⭐⭐⭐ | https://platform.deepseek.com/ |
| 通义千问 | 学生免费 | ⭐⭐⭐⭐ | https://dashscope.aliyun.com/ |
| 豆包 | 新用户免费 | ⭐⭐⭐⭐ | https://www.volcengine.com/product/doubao |

## License

MIT
