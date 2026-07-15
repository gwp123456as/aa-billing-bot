# AA记账机器人 使用指南

## 快速开始

### 第一步：安装

```bash
# 克隆仓库
git clone https://github.com/你的用户名/aa-billing-bot.git
cd aa-billing-bot

# 安装依赖
pip install requests
```

### 第二步：配置 API Key

```bash
# Windows
set AA_BOT_API_KEY=sk-your-key-here

# Linux/Mac
export AA_BOT_API_KEY=sk-your-key-here
```

> 获取免费 API Key：访问 https://platform.deepseek.com/ 注册即送

### 第三步：开始记账

```bash
# 记一笔账
python skill/scripts/aa_bot.py add "今天聚餐花了200，我和张三李四吃的，我付的"

# 查看所有账单
python skill/scripts/aa_bot.py list

# 计算净结算
python skill/scripts/aa_bot.py settle

# 生成催款消息
python skill/scripts/aa_bot.py remind 1 --relation 好朋友

# 生成汇总报告
python skill/scripts/aa_bot.py report
```

## 命令详解

### add - 添加账单

```bash
python skill/scripts/aa_bot.py add "描述" [选项]
```

**选项：**
- `--relation`：关系程度（好朋友/朋友/同学/同事），默认"朋友"
- `--user`：当前用户名，覆盖默认值
- `--offline`：强制使用离线模式（不用AI）

**示例：**

```bash
# 基本用法
python skill/scripts/aa_bot.py add "今天聚餐花了200，我和张三李四吃的，我付的"

# 指定关系
python skill/scripts/aa_bot.py add "打车30，我和张三，他付的" --relation 好朋友

# 自定义分摊
python skill/scripts/aa_bot.py add "买奶茶花了75，我一杯25张三一杯50，我付的"

# 离线模式
python skill/scripts/aa_bot.py add "聚餐花了300，我和张三李四，我付的" --offline
```

### list - 查看账单

```bash
python skill/scripts/aa_bot.py list
```

显示所有账单记录，包含序号、日期、描述、金额、付款人、参与人、状态。

### settle - 净结算

```bash
python skill/scripts/aa_bot.py settle
```

汇总所有未结算账单，计算最少的转账方案。

**核心算法：** 贪心算法，确保转账笔数最少。

### remind - 生成催款消息

```bash
python skill/scripts/aa_bot.py remind <账单ID> [选项]
```

**选项：**
- `--relation`：关系程度

```bash
python skill/scripts/aa_bot.py remind 1 --relation 好朋友
```

### report - 汇总报告

```bash
python skill/scripts/aa_bot.py report
```

生成包含消费概况、各人余额、转账明细的汇总报告。

### delete - 删除账单

```bash
python skill/scripts/aa_bot.py delete <账单ID>
```

### clear - 清空数据

```bash
python skill/scripts/aa_bot.py clear
```

⚠️ 此操作会删除所有账单和结算记录，不可恢复。

### test - 运行测试

```bash
python skill/scripts/aa_bot.py test
```

运行内置测试套件，验证核心功能正确性。

### status - 系统状态

```bash
python skill/scripts/aa_bot.py status
```

显示API配置、账单数量、总金额等信息。

## 离线模式

当未配置 API Key 时，系统自动降级到离线模式：

| 功能 | 在线模式（AI） | 离线模式 |
|------|--------------|---------|
| 账单解析 | 理解任意自然语言 | 仅支持 "花了XX" 简单格式 |
| 催款消息 | 个性化、自然语言 | 固定模板 |
| 汇总报告 | AI生成友好报告 | 固定格式报告 |
| 结算计算 | ✅ 相同 | ✅ 相同 |

> 离线模式验证了 AI 的核心价值：复杂自然语言理解只有 AI 能做到。

## 常见问题

### Q: 报错 "未设置 API Key"

设置环境变量 `AA_BOT_API_KEY`，或使用 `--offline` 参数。

### Q: API 调用失败

1. 检查网络连接
2. 确认 API Key 有效
3. 确认 API 地址正确（默认 DeepSeek）

### Q: 解析结果不准确

尝试更清晰地描述，包含关键信息：金额、参与人、付款人。

### Q: 数据存储在哪里？

所有数据存储在 `data/bills.json` 和 `data/settlements.json`。
