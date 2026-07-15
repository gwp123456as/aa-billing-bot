# -*- coding: utf-8 -*-
"""
AA记账机器人 - 结算计算模块（纯算法，无AI依赖）

负责计算每人应付金额、汇总多笔账单后的净结算关系。
这是确定性的数学计算，不需要 AI 参与。
"""


def calculate_split(amount, participants, payer, shares=None):
    """
    计算单笔账单的分摊结果

    :param amount: 总金额
    :param participants: 参与人列表
    :param payer: 付款人
    :param shares: 自定义分摊比例/金额，空字典表示平均分配
    :return: dict，包含 each_owes（每人应付）和 settlements（谁该转给谁多少）
    """
    n = len(participants)
    if n == 0:
        return {"each_owes": {}, "settlements": []}

    each_owes = {}

    if not shares:
        # 平均分配
        per_person = round(amount / n, 2)
        for p in participants:
            each_owes[p] = per_person
        # 处理除不尽的余数，加到最后一个人
        total = sum(each_owes.values())
        if abs(total - amount) > 0.001:
            each_owes[participants[-1]] = round(each_owes[participants[-1]] + (amount - total), 2)
    else:
        # 自定义分摊
        # 判断 shares 是金额还是比例
        total_shares = sum(shares.values())
        if total_shares > amount * 0.5:
            # 可能是具体金额
            for p in participants:
                each_owes[p] = round(shares.get(p, 0), 2)
        else:
            # 按比例分配
            for p in participants:
                each_owes[p] = round(amount * shares.get(p, 0) / total_shares, 2)
        # 修正四舍五入误差
        total = sum(each_owes.values())
        if abs(total - amount) > 0.001:
            each_owes[participants[-1]] = round(each_owes[participants[-1]] + (amount - total), 2)

    # 生成结算指令：谁该转给付款人多少
    settlements = []
    for p in participants:
        if p == payer:
            continue
        if each_owes[p] > 0:
            settlements.append({
                "from": p,
                "to": payer,
                "amount": each_owes[p]
            })

    return {
        "each_owes": each_owes,
        "settlements": settlements,
        "total": amount,
        "payer": payer,
        "participants": participants
    }


def calculate_net_settlements(bills):
    """
    汇总多笔账单，计算净结算关系（谁总共该给谁多少钱）

    核心算法：
    1. 计算每个人的总应付和总已付
    2. 得出每人的净差额（正=应收，负=应支）
    3. 用贪心算法匹配：应收者从应支者收钱

    :param bills: 账单列表，每条包含 amount, participants, payer, shares
    :return: list，净结算指令 [{"from": "A", "to": "B", "amount": 50.0}, ...]
    """
    # 统计每人的总支出和总应付
    balance = {}  # 正数=别人欠TA，负数=TA欠别人

    for bill in bills:
        amount = float(bill["amount"])
        participants = bill["participants"]
        payer = bill["payer"]
        shares = bill.get("shares", {})

        split = calculate_split(amount, participants, payer, shares)

        for person, owes in split["each_owes"].items():
            if person not in balance:
                balance[person] = 0
            if person == payer:
                # 付款人：替别人垫付了钱，所以应收
                balance[person] += (amount - owes)
            else:
                # 非付款人：应付
                balance[person] -= owes

    # 分成应收和应支两组
    creditors = []  # 应收：balance > 0
    debtors = []   # 应支：balance < 0

    for person, amt in balance.items():
        if amt > 0.01:
            creditors.append((person, round(amt, 2)))
        elif amt < -0.01:
            debtors.append((person, round(-amt, 2)))

    # 贪心匹配
    settlements = []
    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        debtor_name, debt_amt = debtors[i]
        creditor_name, credit_amt = creditors[j]

        transfer = min(debt_amt, credit_amt)
        if transfer > 0.01:
            settlements.append({
                "from": debtor_name,
                "to": creditor_name,
                "amount": round(transfer, 2)
            })

        debtors[i] = (debtor_name, debt_amt - transfer)
        creditors[j] = (creditor_name, credit_amt - transfer)

        if debtors[i][1] < 0.01:
            i += 1
        if creditors[j][1] < 0.01:
            j += 1

    return settlements


def format_settlement_summary(settlements):
    """格式化结算摘要为可读文本"""
    if not settlements:
        return "🎉 所有人都已两清，无需转账！"

    lines = ["📋 结算汇总："]
    for s in settlements:
        lines.append(f"  {s['from']} → {s['to']}：¥{s['amount']:.2f}")
    total = sum(s['amount'] for s in settlements)
    lines.append(f"  ────────────────")
    lines.append(f"  共 {len(settlements)} 笔转账，合计 ¥{total:.2f}")
    return "\n".join(lines)


def get_balance_summary(bills):
    """
    获取每个人的余额摘要
    正数=别人欠你，负数=你欠别人
    """
    balance = {}
    for bill in bills:
        amount = float(bill["amount"])
        participants = bill["participants"]
        payer = bill["payer"]
        shares = bill.get("shares", {})

        split = calculate_split(amount, participants, payer, shares)

        for person, owes in split["each_owes"].items():
            if person not in balance:
                balance[person] = 0
            if person == payer:
                balance[person] += (amount - owes)
            else:
                balance[person] -= owes

    return {p: round(v, 2) for p, v in sorted(balance.items(), key=lambda x: -x[1])}
