"""Головний модуль запуску всіх завдань Лабораторної роботи №1 (Варіант 14)."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from labs.lab01.task1 import run_task1
from labs.lab01.task2 import run_task2
from labs.lab01.task3 import run_task3
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER


def main():
    """Послідовний запуск усіх завдань лабораторної роботи."""
    print("=" * 60)
    print(f"Студент: {STUDENT_NAME} | Група: {GROUP_NAME} | Варіант: {VARIANT_NUMBER}")
    print("=" * 60 + "\n")

    run_task1()
    run_task2()
    run_task3()

    print("=" * 60)
    print("      УСІ ЗАВДАННЯ УСПІШНО ВИКОНАНО!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()