# -*- coding: utf-8 -*-
"""
AA记账机器人 - 配置文件
支持任何 OpenAI 兼容 API（DeepSeek / 豆包 / 通义千问 等）
"""

import os

# ============ API 配置 ============
# 默认使用 DeepSeek API（学生可领取免费额度）
# 也可通过环境变量切换为其他 OpenAI 兼容 API
API_BASE_URL = os.getenv("AA_BOT_API_BASE", "https://api.deepseek.com/v1")
API_KEY = os.getenv("AA_BOT_API_KEY", "")
MODEL_NAME = os.getenv("AA_BOT_MODEL", "deepseek-chat")

# ============ 存储路径 ============
# 数据目录：项目根目录下的 data/
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(_PROJECT_ROOT, "data")
BILLS_FILE = os.path.join(DATA_DIR, "bills.json")
SETTLEMENTS_FILE = os.path.join(DATA_DIR, "settlements.json")

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# ============ 默认用户名 ============
# 可通过环境变量设置当前用户名
DEFAULT_USER = os.getenv("AA_BOT_USER", "我")
