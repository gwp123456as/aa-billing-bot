# -*- coding: utf-8 -*-
"""
AA记账机器人 - 本地存储模块
使用 JSON 文件持久化账单和结算记录
"""

import json
import os
from datetime import datetime
from config import BILLS_FILE, SETTLEMENTS_FILE


def _load_json(filepath):
    """加载 JSON 文件，不存在则返回空列表"""
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save_json(filepath, data):
    """保存数据到 JSON 文件"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ==================== 账单操作 ====================

def save_bill(bill_data):
    """
    保存一条账单记录
    :param bill_data: dict，包含 amount, description, participants, payer, shares, timestamp
    :return: 保存后的账单 dict（含自动生成的 id）
    """
    bills = _load_json(BILLS_FILE)
    bill_data["id"] = len(bills) + 1
    bill_data["timestamp"] = bill_data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    bill_data["settled"] = False
    bills.append(bill_data)
    _save_json(BILLS_FILE, bills)
    return bill_data


def get_all_bills():
    """获取所有账单记录"""
    return _load_json(BILLS_FILE)


def get_unsettled_bills():
    """获取所有未结算的账单"""
    return [b for b in _load_json(BILLS_FILE) if not b.get("settled", False)]


def mark_bill_settled(bill_id):
    """标记某条账单为已结算"""
    bills = _load_json(BILLS_FILE)
    for b in bills:
        if b.get("id") == bill_id:
            b["settled"] = True
            break
    _save_json(BILLS_FILE, bills)


def delete_bill(bill_id):
    """删除指定账单"""
    bills = _load_json(BILLS_FILE)
    bills = [b for b in bills if b.get("id") != bill_id]
    _save_json(BILLS_FILE, bills)


def clear_all_bills():
    """清空所有账单（用于测试重置）"""
    _save_json(BILLS_FILE, [])


# ==================== 结算操作 ====================

def save_settlement(settlement_data):
    """
    保存一条结算记录（某人向某人转账）
    :param settlement_data: dict，包含 from_user, to_user, amount, bill_ids, timestamp
    """
    settlements = _load_json(SETTLEMENTS_FILE)
    settlement_data["timestamp"] = settlement_data.get(
        "timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    settlements.append(settlement_data)
    _save_json(SETTLEMENTS_FILE, settlements)


def get_all_settlements():
    """获取所有结算记录"""
    return _load_json(SETTLEMENTS_FILE)


def clear_all_settlements():
    """清空所有结算记录"""
    _save_json(SETTLEMENTS_FILE, [])
