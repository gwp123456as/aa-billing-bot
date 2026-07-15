# -*- coding: utf-8 -*-
"""
AA记账机器人 - 账单解析模块
使用 LLM（大语言模型）将自然语言描述解析为结构化账单数据

核心 AI 价值：
- 传统方式需要手动输入金额、选择参与人、选择付款人，步骤繁琐
- AI 能直接理解 "今天聚餐花了200，我和张三李四吃的，我付的" 这种自然语言
- 没有AI根本做不到自然语言 → 结构化数据的转换
"""

import json
import requests
from config import API_BASE_URL, API_KEY, MODEL_NAME, DEFAULT_USER


# 解析账单的系统提示词
PARSE_SYSTEM_PROMPT = """你是一个AA记账解析助手。用户会用自然语言描述一笔消费，你需要将其解析为结构化的JSON数据。

解析规则：
1. 提取消费总金额（数字）
2. 提取消费描述（如"聚餐"、"打车"、"买奶茶"等）
3. 提取所有参与人名单
4. 提取付款人（谁付的钱）
5. 如果用户提到了每个人的具体消费金额或比例，记录在 shares 中；否则默认平均分配
6. 如果用户说"我"，用当前用户名替换

输出格式（严格JSON，不要添加任何其他文字）：
{
  "amount": 200.0,
  "description": "聚餐",
  "participants": ["张三", "李四", "王五"],
  "payer": "张三",
  "shares": {},
  "note": ""
}

shares 说明：
- 空对象 {} 表示平均分配
- 如果有人消费不同，如 {"张三": 100, "李四": 50, "王五": 50}，表示各自的具体金额
- 也可以用比例，如 {"张三": 2, "李四": 1, "王五": 1}，表示2:1:1

注意：
- 如果没有明确说明付款人，默认为第一个提到的人
- 如果没有明确说明参与人，根据上下文推断
- 金额必须是数字类型，不要带单位
- 只输出JSON，不要输出其他任何内容"""


def parse_bill_input(user_input, current_user=None):
    """
    使用 LLM 将自然语言解析为结构化账单数据

    :param user_input: 用户自然语言输入，如 "今天聚餐花了200，我和张三李四吃的，我付的"
    :param current_user: 当前用户名，用于替换"我"
    :return: dict，包含 amount, description, participants, payer, shares, note
    :raises Exception: 如果API调用失败或解析失败
    """
    if not API_KEY:
        raise ValueError(
            "未设置 API Key！请设置环境变量 AA_BOT_API_KEY。\n"
            "获取方式：DeepSeek 开放平台 https://platform.deepseek.com/ 注册即可领取免费额度"
        )

    user_name = current_user or DEFAULT_USER

    # 将用户输入中的"我"替换为实际用户名，帮助 AI 理解
    context_input = f'（当前用户是「{user_name}」，输入中的「我」指「{user_name}」）\n{user_input}'

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": PARSE_SYSTEM_PROMPT},
            {"role": "user", "content": context_input},
        ],
        "temperature": 0.1,  # 低温度确保输出稳定
        "response_format": {"type": "json_object"},
    }

    try:
        resp = requests.post(
            f"{API_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise Exception("网络连接失败，请检查网络或API地址是否正确")
    except requests.exceptions.Timeout:
        raise Exception("API请求超时，请稍后重试")
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 401:
            raise Exception("API Key 无效，请检查环境变量 AA_BOT_API_KEY")
        raise Exception(f"API请求失败: HTTP {resp.status_code} - {resp.text}")

    result = resp.json()
    content = result["choices"][0]["message"]["content"]

    # 解析 LLM 返回的 JSON
    try:
        bill_data = json.loads(content)
    except json.JSONDecodeError:
        # 尝试提取 JSON 部分
        import re
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            bill_data = json.loads(json_match.group())
        else:
            raise Exception(f"AI返回内容无法解析为JSON: {content}")

    # 验证必要字段
    if "amount" not in bill_data or not bill_data["amount"]:
        raise Exception("AI未能正确解析消费金额，请更清晰地描述")

    if "participants" not in bill_data or not bill_data["participants"]:
        bill_data["participants"] = [user_name]

    if "payer" not in bill_data or not bill_data["payer"]:
        bill_data["payer"] = user_name

    if "description" not in bill_data:
        bill_data["description"] = "消费"

    if "shares" not in bill_data:
        bill_data["shares"] = {}

    if "note" not in bill_data:
        bill_data["note"] = ""

    # 确保金额是浮点数
    bill_data["amount"] = float(bill_data["amount"])

    return bill_data


# ==================== 离线降级模式 ====================
# 当没有 API Key 时，提供简单的关键词解析作为降级方案
# 注意：降级模式只能处理非常简单的格式，无法理解复杂自然语言
# 这也正体现了 AI 的核心价值——复杂自然语言理解只有 AI 能做到

# 常见中文姓氏（用于离线模式切分无分隔符的人名串）
_COMMON_SURNAMES = "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卞齐康伍余元卜顾孟平黄和穆萧尹"

def _split_by_surname(name_str):
    """
    按常见姓氏切分无分隔符的中文人名串
    如 "张三李四" → ["张三", "李四"]
    这是离线模式的启发式补救，不保证100%准确
    （正因如此，AI解析才显得不可替代）
    """
    result = []
    i = 0
    while i < len(name_str):
        if name_str[i] in _COMMON_SURNAMES:
            # 找到姓氏，取姓+1~2字作为名字
            if i + 2 <= len(name_str):
                # 检查下一个字是否也是姓氏（如"张李"两人各单字名）
                if i + 2 < len(name_str) and name_str[i+2] in _COMMON_SURNAMES:
                    result.append(name_str[i:i+2])
                    i += 2
                elif i + 3 <= len(name_str) and i + 2 < len(name_str) and name_str[i+2] in _COMMON_SURNAMES:
                    # 两个单字名的情况
                    result.append(name_str[i:i+2])
                    i += 2
                else:
                    # 默认取2字
                    result.append(name_str[i:i+2])
                    i += 2
            else:
                result.append(name_str[i:])
                i = len(name_str)
        else:
            i += 1
    return result if result else [name_str]


def parse_bill_offline(user_input, current_user=None):
    """
    离线降级解析（无API时使用）
    仅支持简单格式："花了XX" + "我和XX吃的" + "XX付的"
    """
    import re

    user_name = current_user or DEFAULT_USER

    # 提取金额：匹配 "花了30" / "花30" / "30块" / 直接 "30" (在中文后)
    amount_match = re.search(r'(?:花了?|块)?\s*(\d+(?:\.\d+)?)\s*(?:块|元)?', user_input)
    # 排除纯数字开头的误匹配
    if not amount_match or float(amount_match.group(1)) == 0:
        amount_match = re.search(r'(\d+(?:\.\d+)?)', user_input)
    amount = float(amount_match.group(1)) if amount_match else 0

    # 提取描述：金额前面的中文词
    desc_match = re.search(r'([\u4e00-\u9fa5]+?)[\d\s花了块元]', user_input)
    description = desc_match.group(1) if desc_match else "消费"
    # 去掉常见时间前缀
    for prefix in ["今天", "昨天", "前天", "刚才", "中午", "晚上", "早上", "昨晚"]:
        if description.startswith(prefix):
            description = description[len(prefix):]
    if not description:
        description = "消费"

    # 提取参与人
    # 尝试匹配 "我和XXX吃的/，" 或 "XXX吃的" 模式
    participants = [user_name]
    # 先匹配 "我" 后面的内容，支持 "我和张三吃的" 和 "我和张三，他付的" 两种格式
    people_match = re.search(r'我[和与]([^付吃，,]+?)(?:吃的|吃的|，|,|$)', user_input)
    if people_match:
        raw = people_match.group(1)
        # 按各种分隔符分割
        raw = raw.replace('、', '/').replace('，', '/').replace('和', '/').replace('与', '/')
        names = [n.strip() for n in raw.split('/') if n.strip()]
        # 无分隔符的长名串，尝试按常见姓氏切分（离线模式的局限补救）
        if len(names) == 1 and len(names[0]) > 2:
            names = _split_by_surname(names[0])
        participants = [user_name] + names
    else:
        # 尝试匹配 "XXX、YYY吃的" 模式（不含"我"）
        people_match2 = re.search(r'([\u4e00-\u9fa5、，/]+)吃的', user_input)
        if people_match2:
            raw = people_match2.group(1)
            raw = raw.replace('、', '/').replace('，', '/').replace('和', '/').replace('与', '/')
            names = [n.strip() for n in raw.split('/') if n.strip()]
            if len(names) == 1 and len(names[0]) > 2:
                names = _split_by_surname(names[0])
            participants = names if names else [user_name]
        else:
            # 尝试匹配 "我和张三，" 格式
            people_match3 = re.search(r'我[和与]([\u4e00-\u9fa5]+)', user_input)
            if people_match3:
                raw = people_match3.group(1)
                raw = raw.replace('、', '/').replace('，', '/').replace('和', '/').replace('与', '/')
                names = [n.strip() for n in raw.split('/') if n.strip()]
                if len(names) == 1 and len(names[0]) > 2:
                    names = _split_by_surname(names[0])
                participants = [user_name] + names

    # 提取付款人
    payer_match = re.search(r'([\u4e00-\u9fa5]+)\s*付的', user_input)
    payer = payer_match.group(1) if payer_match else user_name
    if payer == "我":
        payer = user_name
    elif payer == "他" or payer == "她":
        # "他付的" → 找出参与人中的非"我"的人
        others = [p for p in participants if p != user_name]
        if len(others) == 1:
            payer = others[0]
        elif len(others) > 1:
            payer = others[0]  # 取第一个非"我"的人

    return {
        "amount": amount,
        "description": description,
        "participants": participants,
        "payer": payer,
        "shares": {},
        "note": "[离线解析] 建议配置API以获得更好的解析效果"
    }
