# -*- coding: utf-8 -*-
"""
AA记账机器人 - 催款消息生成模块
使用 LLM 生成友好、不尴尬的催款消息

核心 AI 价值：
- 催钱这件事最大的痛点是「不好意思开口」
- AI 能根据关系亲疏、金额大小、场合选择合适的语气
- 没有AI根本做不到这种「察言观色」的个性化消息生成
"""

import json
import requests
from config import API_BASE_URL, API_KEY, MODEL_NAME


REMINDER_SYSTEM_PROMPT = """你是一个AA记账催款消息生成助手。你需要根据账单信息生成一条友好的催款消息。

生成原则：
1. 语气轻松自然，不要像催债
2. 可以用emoji让消息不那么严肃
3. 根据关系程度调整语气（好朋友可以更随意，普通朋友更礼貌）
4. 清楚说明：什么事、多少钱、转给谁
5. 不要提"催"字，用"方便的话转一下"这类说法
6. 消息长度控制在2-3句话

输出格式（纯文本消息，直接可以复制发送）：
就是消息本身，不需要JSON，不需要解释。"""


def generate_reminder(bill_data, split_result, relationship="朋友"):
    """
    使用 LLM 生成催款消息

    :param bill_data: 账单数据
    :param split_result: 分摊结果
    :param relationship: 关系程度（好朋友/朋友/同学/同事）
    :return: str，催款消息文本
    """
    if not API_KEY:
        # 无API时使用模板消息
        return _template_reminder(bill_data, split_result)

    settlements = split_result.get("settlements", [])
    if not settlements:
        return "✅ 大家都两清了，不用转账~"

    # 构建给AI的输入
    info = {
        "消费描述": bill_data["description"],
        "总金额": bill_data["amount"],
        "付款人": bill_data["payer"],
        "分摊明细": [
            f"{s['from']} → {s['to']}：¥{s['amount']:.2f}"
            for s in settlements
        ],
        "关系": relationship,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": REMINDER_SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(info, ensure_ascii=False)},
        ],
        "temperature": 0.7,  # 稍高温度让消息更自然多样
    }

    try:
        resp = requests.post(
            f"{API_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception:
        # 降级到模板消息
        return _template_reminder(bill_data, split_result)


def _template_reminder(bill_data, split_result):
    """模板催款消息（无API时的降级方案）"""
    settlements = split_result.get("settlements", [])
    desc = bill_data["description"]
    payer = bill_data["payer"]

    lines = [f"🍽️ 昨天{desc}的账单来啦~"]
    for s in settlements:
        lines.append(f"  {s['from']} 方便的话转给 {s['to']} ¥{s['amount']:.2f} 😊")
    lines.append(f"  谢谢大家！")
    return "\n".join(lines)


def generate_summary_report(bills, settlements):
    """
    使用 LLM 生成月底/周期结算汇总报告

    :param bills: 所有账单列表
    :param settlements: 净结算列表
    :return: str，汇总报告文本
    """
    if not API_KEY:
        return _template_summary(bills, settlements)

    from settlement import get_balance_summary, format_settlement_summary

    balance = get_balance_summary(bills)
    summary_text = format_settlement_summary(settlements)

    info = {
        "账单数量": len(bills),
        "总消费": sum(b["amount"] for b in bills),
        "各人余额": balance,
        "结算明细": summary_text,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": "你是一个AA记账汇总助手。根据数据生成一份简洁友好的月度结算汇总报告，包含消费概况、各人余额、需转账明细。语气轻松，用emoji点缀。"
            },
            {"role": "user", "content": json.dumps(info, ensure_ascii=False)},
        ],
        "temperature": 0.5,
    }

    try:
        resp = requests.post(
            f"{API_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception:
        return _template_summary(bills, settlements)


def _template_summary(bills, settlements):
    """模板汇总报告"""
    from settlement import get_balance_summary, format_settlement_summary

    balance = get_balance_summary(bills)
    summary = format_settlement_summary(settlements)

    lines = ["📊 结算汇总报告", "=" * 30]
    lines.append(f"总账单数：{len(bills)} 笔")
    lines.append(f"总消费：¥{sum(b['amount'] for b in bills):.2f}")
    lines.append("")
    lines.append("各人余额（正=应收，负=应支）：")
    for person, amt in balance.items():
        sign = "📈" if amt > 0 else "📉" if amt < 0 else "➖"
        lines.append(f"  {sign} {person}: ¥{amt:.2f}")
    lines.append("")
    lines.append(summary)
    return "\n".join(lines)
