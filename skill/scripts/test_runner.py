# -*- coding: utf-8 -*-
"""
AA记账机器人 - 测试运行器
用于验证核心功能正确性
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from settlement import calculate_split, calculate_net_settlements, get_balance_summary
from storage import clear_all_bills, clear_all_settlements


def test_equal_split():
    """测试1：平均分摊"""
    print("\n[Test 1] 平均分摊测试")
    result = calculate_split(300, ["张三", "李四", "王五"], "张三")
    assert result["each_owes"]["张三"] == 100.0
    assert result["each_owes"]["李四"] == 100.0
    assert result["each_owes"]["王五"] == 100.0
    assert len(result["settlements"]) == 2
    assert result["settlements"][0]["from"] == "李四"
    assert result["settlements"][0]["to"] == "张三"
    assert result["settlements"][0]["amount"] == 100.0
    print("  ✅ 通过：300元3人平分，每人100元")


def test_uneven_amount():
    """测试2：不均等金额分摊"""
    print("\n[Test 2] 不均等金额分摊测试")
    shares = {"张三": 120, "李四": 80, "王五": 100}
    result = calculate_split(300, ["张三", "李四", "王五"], "张三", shares)
    assert result["each_owes"]["张三"] == 120.0
    assert result["each_owes"]["李四"] == 80.0
    assert result["each_owes"]["王五"] == 100.0
    assert result["settlements"][0]["from"] == "李四"
    assert result["settlements"][0]["amount"] == 80.0
    assert result["settlements"][1]["from"] == "王五"
    assert result["settlements"][1]["amount"] == 100.0
    print("  ✅ 通过：300元按120/80/100分摊正确")


def test_ratio_split():
    """测试3：比例分摊"""
    print("\n[Test 3] 比例分摊测试")
    shares = {"张三": 2, "李四": 1, "王五": 1}  # 2:1:1
    result = calculate_split(400, ["张三", "李四", "王五"], "李四", shares)
    assert result["each_owes"]["张三"] == 200.0
    assert result["each_owes"]["李四"] == 100.0
    assert result["each_owes"]["王五"] == 100.0
    print("  ✅ 通过：400元按2:1:1分摊，张三200/李四100/王五100")


def test_round_error():
    """测试4：除不尽的四舍五入处理"""
    print("\n[Test 4] 四舍五入误差处理测试")
    result = calculate_split(100, ["张三", "李四", "王五"], "张三")
    total = sum(result["each_owes"].values())
    assert abs(total - 100) < 0.01, f"总和应为100，实际为{total}"
    print(f"  ✅ 通过：100元3人分，每人{result['each_owes']['张三']}元，总和={total}")


def test_net_settlement():
    """测试5：多笔账单净结算"""
    print("\n[Test 5] 多笔账单净结算测试")
    bills = [
        {"amount": 300, "participants": ["张三", "李四", "王五"], "payer": "张三", "shares": {}},
        {"amount": 150, "participants": ["张三", "李四"], "payer": "李四", "shares": {}},
        {"amount": 60, "participants": ["李四", "王五"], "payer": "王五", "shares": {}},
    ]
    settlements = calculate_net_settlements(bills)
    print(f"  结算结果：{settlements}")

    # 账单1：张三付300，每人100 → 张三应收200
    # 账单2：李四付150，每人75 → 李四应收75，张三应付75
    # 账单3：王五付60，每人30 → 王五应收30，李四应付30
    # 净额：张三=200-75=125(应收), 李四=75-30-100=-55(应支), 王五=30-100=-70(应支)

    balance = get_balance_summary(bills)
    print(f"  各人余额：{balance}")

    assert balance["张三"] == 125.0, f"张三应收125，实际{balance['张三']}"
    assert balance["李四"] == -55.0, f"李四应支55，实际{balance['李四']}"
    assert balance["王五"] == -70.0, f"王五应支70，实际{balance['王五']}"

    print("  ✅ 通过：3笔账单净结算计算正确")


def test_two_person():
    """测试6：两人场景"""
    print("\n[Test 6] 两人AA测试")
    result = calculate_split(88, ["张三", "李四"], "张三")
    assert result["each_owes"]["张三"] == 44.0
    assert result["each_owes"]["李四"] == 44.0
    assert len(result["settlements"]) == 1
    print("  ✅ 通过：88元2人AA，每人44元")


def test_single_person():
    """测试7：单人场景（自己付自己吃）"""
    print("\n[Test 7] 单人场景测试")
    result = calculate_split(50, ["张三"], "张三")
    assert result["each_owes"]["张三"] == 50.0
    assert len(result["settlements"]) == 0
    print("  ✅ 通过：单人消费无需分摊")


def run_tests():
    """运行所有测试"""
    print("=" * 50)
    print("🧪 AA记账机器人 - 测试套件")
    print("=" * 50)

    tests = [
        test_equal_split,
        test_uneven_amount,
        test_ratio_split,
        test_round_error,
        test_net_settlement,
        test_two_person,
        test_single_person,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ❌ 失败：{e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ 异常：{e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"📊 测试结果：{passed} 通过 / {failed} 失败 / 共 {len(tests)} 项")
    if failed == 0:
        print("🎉 所有测试通过！")
    print("=" * 50)

    return failed == 0


if __name__ == "__main__":
    run_tests()
