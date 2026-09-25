"""Завдання 1: Комплексний аналізатор надійності паролів (Варіант 14)."""

import random
import string
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

PASSWORDS = [
    "C2@Command",
    "plain123",
    "Backdoor@D3tect",
    "public123",
    "Rootkit@Hunt",
    "access123",
    "Exploit@An4lysis",
    "basic",
    "Payload@D3decode",
    "default123",
]

CRITERIA = {
    "min_length": 10,
    "require_digits": True,
    "require_upper": True,
    "require_special": True,
}

FORBIDDEN_PASSWORDS = {
    "plain123",
    "public123",
    "access123",
    "basic",
    "default123",
    "user",
}


def prepare_passwords(passwords_list: list[str]) -> list[str]:
    """Випадковим чином вибирає 3 паролі та додає їх дублікати в кінець списку."""
    working_list = passwords_list.copy()
    random_indices = random.sample(range(len(working_list)), 3)
    duplicates = [working_list[idx] for idx in random_indices]
    working_list.extend(duplicates)
    return working_list


def evaluate_password(password: str, all_passwords: list[str]) -> str:
    """Оцінює надійність конкретного пароля за правилами методички."""
    min_len = CRITERIA["min_length"]

    if password in FORBIDDEN_PASSWORDS or len(password) < min_len:
        return "Заборонений"

    has_digit = any(char.isdigit() for char in password)
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_special = any(char in string.punctuation for char in password)

    checks = [has_digit, has_upper, has_lower, has_special]
    passed_count = sum(checks)
    all_criteria_met = (
        has_digit and has_upper and has_lower and has_special
    )

    is_unique = all_passwords.count(password) == 1

    if all_criteria_met and len(password) >= min_len + 4 and is_unique:
        return "Дуже сильний"

    if all_criteria_met and len(password) < min_len + 4:
        return "Сильний"

    if passed_count > 1 and not all_criteria_met:
        return "Середній"

    return "Слабкий"


def run_task1():
    """Запускає виконання першого завдання."""
    print("ЗАВДАННЯ 1: Аналізатор надійності паролів\n")

    prepared_passwords = prepare_passwords(PASSWORDS)

    print(f"{'Пароль':<20} | {'Оцінка надійності':<20}")
    print("-" * 43)
    for pwd in prepared_passwords:
        status = evaluate_password(pwd, prepared_passwords)
        print(f"{pwd:<20} | {status:<20}")
    print("\n")


if __name__ == "__main__":
    run_task1()