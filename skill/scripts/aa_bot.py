#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AA记账机器人 - 主程序入口
=====================================
一个基于 AI 的 AA 制记账助手

用法：
  python aa_bot.py add "今天聚餐花了200，我和张三李四吃的，我付的"
  python aa_bot.py add "打车花了30，我和张三，张三付的" --relation 好朋友
  python aa_bot.py list                      # 查看所有账单
  python aa_bot.py settle                     # 计算净结算
  python aa_bot.py remind <bill_id>           # 生成催款消息
  python aa_bot.py report                     # 生成汇总报告
  python aa_bot.py delete <bill_id>           # 删除账单
  python aa_bot.py clear                      # 清空所有数据（测试用）
  python aa_bot.py test                       # 运行测试用例

环境变量：
  AA_BOT_API_KEY    - API密钥（必填，用于AI解析）
  AA_BOT_API_BASE   - API地址（默认DeepSeek）
  AA_BOT_MODEL      - 模型名称（默认deepseek-chat）
  AA_BOT_USER       - 当前用户名（默认"我"）
"""

import sys
import os
import argparse

# 修复 Windows 终端编码问题
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# 将脚本目录加入路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import API_KEY, DEFAULT_USER
from storage import (
    save_bill, get_all_bills, get_unsettled_bills,
    mark_bill_settled, delete_bill, clear_all_bills,
    save_settlement, get_all_settlements, clear_all_settlements,
)
from bill_parser import parse_bill_input, parse_bill_offline
from settlement import calculate_split, calculate_net_settlements, format_settlement_summary, get_balance_summary
from reminder_gen import generate_reminder, generate_summary_report


def cmd_add(args):
    """添加一笔账单"""
    print(f"\n🤖 正在解析你的输入...")
    print(f"   输入: {args.description}")

    # 尝试用AI解析
    use_ai = bool(API_KEY) and not args.offline

    if use_ai:
        try:
            bill_data = parse_bill_input(args.description, args.user)
            print("   ✅ AI解析成功！")
        except Exception as e:
            print(f"   ⚠️ AI解析失败: {e}")
            print("   🔄 降级到离线解析模式...")
            bill_data = parse_bill_offline(args.description, args.user)
    else:
        if not API_KEY:
            print("   ℹ️ 未配置API Key，使用离线解析模式")
            print("   （离线模式只能处理简单格式，建议配置API以获得完整体验）")
        bill_data = parse_bill_offline(args.description, args.user)

    # 保存账单
    saved = save_bill(bill_data)

    # 显示解析结果
    print(f"\n📝 账单已记录：")
    print(f"   序号: #{saved['id']}")
    print(f"   消费: {bill_data['description']}")
    print(f"   金额: ¥{bill_data['amount']:.2f}")
    print(f"   参与人: {', '.join(bill_data['participants'])}")
    print(f"   付款人: {bill_data['payer']}")

    # 计算分摊
    split = calculate_split(
        bill_data["amount"],
        bill_data["participants"],
        bill_data["payer"],
        bill_data.get("shares", {})
    )

    print(f"\n💰 分摊明细：")
    for person, amount in split["each_owes"].items():
        if person == bill_data["payer"]:
            print(f"   {person}: ¥{amount:.2f} (已付，应收 ¥{amount * (len(bill_data['participants'])-1):.2f})")
        else:
            print(f"   {person}: ¥{amount:.2f}")

    # 生成催款消息
    if split["settlements"]:
        print(f"\n📨 催款消息（关系：{args.relation}）：")
        print("-" * 40)
        message = generate_reminder(bill_data, split, args.relation)
        print(message)
        print("-" * 40)
        print("   （复制以上消息发送到群里即可）")
    else:
        print("\n✅ 只有付款人自己，无需催款")

    return saved


def cmd_list(args):
    """列出所有账单"""
    bills = get_all_bills()
    if not bills:
        print("\n📭 还没有账单记录")
        return

    print(f"\n📋 所有账单（共 {len(bills)} 笔）：")
    print("=" * 60)

    total = 0
    for b in bills:
        status = "✅已结算" if b.get("settled") else "⏳待结算"
        print(f"  #{b['id']} | {b['timestamp'][:10]} | {b['description']}")
        print(f"       金额: ¥{b['amount']:.2f} | 付款: {b['payer']} | 参与: {', '.join(b['participants'])} | {status}")
        total += b["amount"]

    print("=" * 60)
    print(f"  合计: ¥{total:.2f}")


def cmd_settle(args):
    """计算净结算"""
    bills = get_all_bills()
    if not bills:
        print("\n📭 还没有账单记录")
        return

    unsettled = [b for b in bills if not b.get("settled", False)]
    if not unsettled:
        print("\n✅ 所有账单都已结算！")
        return

    settlements = calculate_net_settlements(unsettled)

    print(f"\n📊 净结算计算（基于 {len(unsettled)} 笔未结算账单）：")
    print()

    # 显示余额
    balance = get_balance_summary(unsettled)
    print("各人余额：")
    for person, amt in balance.items():
        if amt > 0:
            print(f"  📈 {person}: +¥{amt:.2f} (应收)")
        elif amt < 0:
            print(f"  📉 {person}: -¥{abs(amt):.2f} (应支)")
        else:
            print(f"  ➖ {person}: ¥0.00")

    print()
    print(format_settlement_summary(settlements))

    if settlements:
        print("\n💡 转账建议：按以上方案转账后，所有人两清")


def cmd_remind(args):
    """生成指定账单的催款消息"""
    bills = get_all_bills()
    bill = None
    for b in bills:
        if b["id"] == args.bill_id:
            bill = b
            break

    if not bill:
        print(f"❌ 找不到账单 #{args.bill_id}")
        return

    split = calculate_split(
        bill["amount"],
        bill["participants"],
        bill["payer"],
        bill.get("shares", {})
    )

    if not split["settlements"]:
        print("\n✅ 该账单无需催款")
        return

    print(f"\n📨 账单 #{bill['id']} 的催款消息：")
    print("-" * 40)
    message = generate_reminder(bill, split, args.relation)
    print(message)
    print("-" * 40)


def cmd_report(args):
    """生成汇总报告"""
    bills = get_all_bills()
    if not bills:
        print("\n📭 还没有账单记录")
        return

    unsettled = [b for b in bills if not b.get("settled", False)]
    settlements = calculate_net_settlements(unsettled) if unsettled else []

    print("\n" + "=" * 50)
    report = generate_summary_report(bills, settlements)
    print(report)
    print("=" * 50)


def cmd_delete(args):
    """删除账单"""
    delete_bill(args.bill_id)
    print(f"\n🗑️ 已删除账单 #{args.bill_id}")


def cmd_clear(args):
    """清空所有数据"""
    clear_all_bills()
    clear_all_settlements()
    print("\n🧹 已清空所有账单和结算记录")


def cmd_test(args):
    """运行内置测试用例"""
    from test_runner import run_tests
    run_tests()


def cmd_status(args):
    """显示系统状态"""
    print("\n🔧 AA记账机器人 系统状态")
    print("=" * 40)
    print(f"  API地址: {os.getenv('AA_BOT_API_BASE', 'https://api.deepseek.com/v1')}")
    print(f"  模型: {os.getenv('AA_BOT_MODEL', 'deepseek-chat')}")
    print(f"  API Key: {'✅ 已配置' if API_KEY else '❌ 未配置'}")
    print(f"  当前用户: {DEFAULT_USER}")

    bills = get_all_bills()
    print(f"  账单数量: {len(bills)} 笔")
    print(f"  总金额: ¥{sum(b['amount'] for b in bills):.2f}")

    if not API_KEY:
        print("\n⚠️ 未配置API Key，当前为离线模式")
        print("  配置方法：")
        print("  Windows: set AA_BOT_API_KEY=your_api_key")
        print("  Linux/Mac: export AA_BOT_API_KEY=your_api_key")
        print("  获取免费Key: https://platform.deepseek.com/")


def main():
    parser = argparse.ArgumentParser(
        description="🤖 AA记账机器人 - 基于AI的AA制记账助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python aa_bot.py add "今天聚餐花了200，我和张三李四吃的，我付的"
  python aa_bot.py add "打车30，我和张三，他付的" --relation 好朋友
  python aa_bot.py list
  python aa_bot.py settle
  python aa_bot.py remind 1
  python aa_bot.py report
  python aa_bot.py status
  python aa_bot.py test
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # add
    p_add = subparsers.add_parser("add", help="添加一笔账单")
    p_add.add_argument("description", help='自然语言描述，如 "聚餐花了200，我和张三李四吃的，我付的"')
    p_add.add_argument("--relation", default="朋友", help="关系程度（好朋友/朋友/同学/同事）")
    p_add.add_argument("--user", default=None, help="当前用户名")
    p_add.add_argument("--offline", action="store_true", help="强制使用离线模式")
    p_add.set_defaults(func=cmd_add)

    # list
    p_list = subparsers.add_parser("list", help="查看所有账单")
    p_list.set_defaults(func=cmd_list)

    # settle
    p_settle = subparsers.add_parser("settle", help="计算净结算")
    p_settle.set_defaults(func=cmd_settle)

    # remind
    p_remind = subparsers.add_parser("remind", help="生成催款消息")
    p_remind.add_argument("bill_id", type=int, help="账单ID")
    p_remind.add_argument("--relation", default="朋友", help="关系程度")
    p_remind.set_defaults(func=cmd_remind)

    # report
    p_report = subparsers.add_parser("report", help="生成汇总报告")
    p_report.set_defaults(func=cmd_report)

    # delete
    p_delete = subparsers.add_parser("delete", help="删除账单")
    p_delete.add_argument("bill_id", type=int, help="账单ID")
    p_delete.set_defaults(func=cmd_delete)

    # clear
    p_clear = subparsers.add_parser("clear", help="清空所有数据")
    p_clear.set_defaults(func=cmd_clear)

    # test
    p_test = subparsers.add_parser("test", help="运行测试用例")
    p_test.set_defaults(func=cmd_test)

    # status
    p_status = subparsers.add_parser("status", help="显示系统状态")
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
