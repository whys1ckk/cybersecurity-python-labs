"""Завдання 3: Хешування, кастомні винятки, CSV-база та JSON-логування (Варіант 14)."""

import csv
import hashlib
import json
import os
import sys
from datetime import datetime
from functools import wraps
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
CSV_PATH = DATA_DIR / "users.csv"
LOG_PATH = DATA_DIR / "log.json"

SALT = f"{VARIANT_NUMBER:05d}"


class ValidationError(Exception):
    """Кастомний виняток для помилок валідації паролів."""

    pass


def log_event(func):
    """Декоратор для логування результатів виконання функцій у JSON."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().isoformat()
        try:
            result = func(*args, **kwargs)
            log_entry = {
                "timestamp": timestamp,
                "function": func.__name__,
                "status": "SUCCESS",
                "args": args,
            }
            _append_log(log_entry)
            return result
        except Exception as e:
            log_entry = {
                "timestamp": timestamp,
                "function": func.__name__,
                "status": "FAILED",
                "error": str(e),
                "args": args,
            }
            _append_log(log_entry)
            raise

    return wrapper


def _append_log(entry: dict):
    """Впоміжне додавання запису до JSON-файлу."""
    logs = []
    if LOG_PATH.exists() and LOG_PATH.stat().st_size > 0:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    logs.append(entry)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)


def hash_password(password: str) -> str:
    """Хешує пароль із сіллю за допомогою SHA-512."""
    if len(password) < 16:
        raise ValidationError(
            f"Пароль надто короткий ({len(password)} симв.). Мінімальна довжина — 16 символів!"
        )
    salted = (password + SALT).encode("utf-8")
    return hashlib.sha512(salted).hexdigest()


@log_event
def register_user(username: str, password: str):
    """Реєструє користувача та зберігає його у CSV-файл."""
    pwd_hash = hash_password(password)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_exists = CSV_PATH.exists()

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["username", "password_hash"])
        writer.writerow([username, pwd_hash])

    print(f"[УСПІХ] Користувач '{username}' успішно зареєстрований!")


def run_task3():
    """Запускає виконання третього завдання."""
    print("ЗАВДАННЯ 3: Хешування, CSV-база та JSON-логування\n")

    if CSV_PATH.exists():
        os.remove(CSV_PATH)

    test_users = [
        ("admin_user", "SuperSecurePassword123!"),  
        ("analyst_01", "Short123!"),                
        ("security_officer", "Complex_And_Long_Password_2026"),  
    ]

    for user, pwd in test_users:
        try:
            print(f"Спроба реєстрації '{user}'...")
            register_user(user, pwd)
        except ValidationError as e:
            print(f"[ПОМИЛКА ВАЛІДАЦІЇ] {e}")

    print("\nЗміст CSV-бази даних (data/users.csv):")
    if CSV_PATH.exists():
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            print(f.read())

    print("\n")


if __name__ == "__main__":
    run_task3()