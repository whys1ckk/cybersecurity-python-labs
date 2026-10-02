"""Головна точка входу для запуску demo та analyze."""

import argparse
import sys

from labs.lab02.task1 import Admin, User, UserAccount
from labs.lab02.task2 import run_analysis


def run_demo() -> None:
    """Сценарій демонстрації Завдання 1."""
    print("==================================================")
    print("      DEMONSTRATION: TASK 1 (OOP & SECURITY)     ")
    print("==================================================")

    usr = User(username="m_lopachak", email="m_lopachak@lpnu.ua")
    usr.set_password("SecurePassword2026!")
    print(f"[1] Створено об'єкт User:\n    {usr}\n")

    print("[2] Перевірка валідації email:")
    try:
        usr.email = "invalid_email_format"
    except ValueError as e:
        print(f"    [CATCH EXPECTED ERROR] {e}")
    print(f"    Поточний email: {usr.email}\n")

    acc = UserAccount(user=usr)
    print("[3] Аутентифікація:")
    login_fail = acc.login("m_lopachak", "WrongPassword", "192.168.1.50")
    print(f"    Спроба входу з невірним паролем: Success={login_fail}")

    login_ok = acc.login("m_lopachak", "SecurePassword2026!", "192.168.1.50")
    print(f"    Спроба входу з правильним паролем: Success={login_ok}")
    print(f"    Статус авторизації: {acc.is_authenticated()}\n")

    admin_usr = Admin(
        username="sys_admin", email="admin@lpnu.ua", permissions={"READ_LOGS"}
    )
    admin_usr.grant_permission("EXECUTE_COMMANDS")
    print(f"[4] Створено об'єкт Admin:\n    {admin_usr}\n")

    acc.logout()
    print("[5] Завершення сеансу (logout).")
    print(f"    Статус авторизації після logout: {acc.is_authenticated()}\n")

    acc.audit_log.show_all()
    print("==================================================\n")


def main() -> None:
    """Розбір CLI-параметрів."""
    parser = argparse.ArgumentParser(
        description="Лабораторна робота №2: CLI утиліти кібербезпеки."
    )
    subparsers = parser.add_subparsers(dest="command", help="Доступні команди")

    subparsers.add_parser("demo", help="Запустити демонстрацію Завдання 1 (ООП)")

    analyze_parser = subparsers.add_parser(
        "analyze", help="Запустити аналізатор EDR логів (Завдання 2)"
    )
    analyze_parser.add_argument(
        "--edr-log",
        type=str,
        default="labs/lab02/data/edr_alerts.json",
        help="Шлях до файлу логів EDR",
    )
    analyze_parser.add_argument(
        "--min-severity",
        type=str,
        default="low",
        choices=["low", "medium", "high", "critical"],
        help="Мінімальний рівень критичності",
    )
    analyze_parser.add_argument(
        "--out-csv",
        type=str,
        default="labs/lab02/data/edr_summary.csv",
        help="Шлях для збереження CSV",
    )
    analyze_parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Шлях системного лог-файлу утиліти",
    )

    args = parser.parse_args()

    if args.command == "demo":
        run_demo()
    elif args.command == "analyze":
        run_analysis(args.edr_log, args.min_severity, args.out_csv, args.log_file)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
