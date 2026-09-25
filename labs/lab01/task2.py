"""Завдання 2: Система контролю доступу (Варіант 14)."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

USERS = {
    "blockchain_dev": {"role": "blockchain_developer", "clearance": 3, "department": "Blockchain", "active": True},
    "smart_contract_auditor": {"role": "contract_auditor", "clearance": 3, "department": "Audit", "active": True},
    "crypto_trader": {"role": "trader", "clearance": 2, "department": "Trading", "active": True},
    "wallet_user": {"role": "wallet_user", "clearance": 1, "department": "Users", "active": True},
    "mining_pool": {"role": "miner", "clearance": 1, "department": "Mining", "active": False}
}

RESOURCES = [
    ("smart_contracts", 3), ("audit_reports", 3),
    ("trading_algorithms", 2), ("wallet_interface", 1), ("private_keys", 3),
    ("public_blockchain", 1), ("defi_protocols", 3), ("validator_nodes", 3),
    ("market_data", 2), ("community_forum", 1)
]

SECURITY_LEVELS = ("Public Blockchain", "Permissioned", "Private Network", "Institutional")
BLOCKED_USERS = {"mining_pool", "flash_loan_attack", "rug_pull_scam"}


def check_access(username: str, resource_name: str, required_level: int) -> bool:
    """Перевіряє доступ користувача до ресурсу."""
    if username in BLOCKED_USERS:
        print(f"[ВІДМОВА] Користувач '{username}' заблокований у системі.")
        return False

    if username not in USERS:
        print(f"[ВІДМОВА] Користувача '{username}' не знайдено.")
        return False

    user = USERS[username]

    if not user.get("active", False):
        print(f"[ВІДМОВА] Обліковий запис '{username}' неактивний.")
        return False

    clearance = user["clearance"]
    role = user["role"]

    if clearance >= required_level:
        print(f"[ДОЗВОЛЕНО] '{username}' ({role}, рівень {clearance}) -> ресурс '{resource_name}' (потрібно {required_level})")
        return True

    print(f"[ВІДМОВА] '{username}' ({role}, рівень {clearance}) -> недостатній рівень для '{resource_name}' (потрібно {required_level})")
    return False


def run_task2():
    """Запускає тестування системи контролю доступу."""
    print("ЗАВДАННЯ 2: Система контролю доступу\n")

    test_cases = [
        ("blockchain_dev", "smart_contracts", 3),
        ("crypto_trader", "private_keys", 3),
        ("wallet_user", "wallet_interface", 1),
        ("mining_pool", "public_blockchain", 1),
        ("flash_loan_attack", "market_data", 2),
        ("unknown_user", "community_forum", 1)
    ]

    for user, res, level in test_cases:
        check_access(user, res, level)
    print("\n")


if __name__ == "__main__":
    run_task2()