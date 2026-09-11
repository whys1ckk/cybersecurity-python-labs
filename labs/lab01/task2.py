"""Завдання 2: Симуляція системи контролю доступу (Варіант 14)."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

ACCESS_LEVELS = ("GUEST", "USER", "ADMIN")

BLOCKED_USERS = {"attacker_01", "malware_bot", "suspended_user"}

USERS = {
    "alice": ("USER", 1),
    "bob": ("ADMIN", 2),
    "guest_user": ("GUEST", 0),
    "attacker_01": ("USER", 1),
}


def check_access(username: str, required_level: int) -> bool:
    """Перевіряє, чи має користувач доступ до ресурсу."""
    if username in BLOCKED_USERS:
        print(f"[ВІДМОВА] Користувач '{username}' заблокований у системі.")
        return False

    if username not in USERS:
        print(f"[ВІДМОВА] Користувач '{username}' не знайдений.")
        return False

    role, clear_level = USERS[username]

    if clear_level >= required_level:
        print(
            f"[ДОЗВОЛЕНО] Користувач '{username}' ({role}, рівень {clear_level}) "
            f"отримав доступ до ресурсу рівню {required_level}."
        )
        return True

    print(
        f"[ВІДМОВА] Користувач '{username}' ({role}, рівень {clear_level}) "
        f"не має достатнього рівня доступу (потрібно {required_level})."
    )
    return False


def run_task2():
    """Запускає виконання другого завдання."""
    print("ЗАВДАННЯ 2: Система контролю доступу\n")

    test_cases = [
        ("alice", 1),
        ("bob", 2),
        ("guest_user", 1),
        ("attacker_01", 1),
        ("unknown_user", 1),
    ]

    for user, req_level in test_cases:
        check_access(user, req_level)
    print("\n")


if __name__ == "__main__":
    run_task2()