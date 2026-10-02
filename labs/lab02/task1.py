"""Завдання 1: Модель користувача й облікового запису (ООП)."""

import hashlib
import hmac
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

PBKDF2_ITERATIONS = 100_000
SESSION_TIMEOUT_SEC = 900


class User:
    """Клас, що представляє користувача системи."""

    def __init__(
        self, username: str, email: str, role: str = "user", active: bool = True
    ) -> None:
        self.username = username
        self.role = role
        self.active = active
        self.__password_hash: bytes | None = None
        self.__password_salt: bytes | None = None
        self.email = email  # Виклик сеттера @property

    @property
    def email(self) -> str:
        """Геттер для email."""
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        """Сеттер email з валідацією через регулярний вираз."""
        pattern = r"^[a-zA-Z][a-zA-Z0-9._%+-]{2,63}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, value):
            raise ValueError(f"Некоректний формат email: '{value}'")
        self._email = value

    def set_password(self, password: str) -> None:
        """Хешує пароль за допомогою PBKDF2-HMAC-SHA256 та випадкової солі."""
        self.__password_salt = os.urandom(16)
        self.__password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            self.__password_salt,
            PBKDF2_ITERATIONS,
        )

    def check_password(self, password: str) -> bool:
        """Перевіряє введений пароль порівнянням збереженого хешу."""
        if not self.__password_hash or not self.__password_salt:
            return False
        computed_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            self.__password_salt,
            PBKDF2_ITERATIONS,
        )
        return hmac.compare_digest(self.__password_hash, computed_hash)

    def deactivate(self) -> None:
        """Деактивує обліковий запис."""
        self.active = False

    def __str__(self) -> str:
        status = "Active" if self.active else "Inactive"
        return f"User(username='{self.username}', email='{self.email}', role='{self.role}', status='{status}')"


class Admin(User):
    """Клас адміністратора (успадковує User)."""

    def __init__(
        self, username: str, email: str, permissions: set[str] | list[str] | None = None
    ) -> None:
        super().__init__(username, email, role="admin", active=True)
        self.permissions: set[str] = set(permissions) if permissions else set()

    def grant_permission(self, permission: str) -> None:
        """Надає дозвіл."""
        self.permissions.add(permission)

    def revoke_permission(self, permission: str) -> None:
        """Вилучає дозвіл."""
        self.permissions.discard(permission)

    def has_permission(self, permission: str) -> bool:
        """Перевіряє наявність дозволу."""
        return permission in self.permissions

    def __str__(self) -> str:
        base_str = super().__str__()
        perms = ", ".join(sorted(self.permissions)) if self.permissions else "None"
        return f"{base_str} | Permissions: [{perms}]"


class Session:
    """Клас сесії користувача."""

    def __init__(self, ip: str) -> None:
        self.ip = ip
        now = datetime.now(timezone.utc)
        self.login_time = now
        self.last_activity = now

    def touch(self) -> None:
        """Оновлює час останньої активності."""
        self.last_activity = datetime.now(timezone.utc)

    def is_active(self, timeout_sec: int) -> bool:
        """Перевіряє активність сесії за таймаутом."""
        if timeout_sec <= 0:
            raise ValueError("Таймаут має бути додатним числом.")
        now = datetime.now(timezone.utc)
        return (now - self.last_activity) <= timedelta(seconds=timeout_sec)


@dataclass
class AuditRecord:
    """Структура запису аудіту."""

    timestamp: datetime
    username: str
    action: str


class AuditLog:
    """Клас ведення журналу аудіту."""

    def __init__(self) -> None:
        self.logs: list[AuditRecord] = []

    def add_log(self, username: str, action: str) -> None:
        """Додає запис до логу (час у UTC)."""
        record = AuditRecord(
            timestamp=datetime.now(timezone.utc),
            username=username,
            action=action,
        )
        self.logs.append(record)

    def show_all(self) -> None:
        """Виводить усі записи логу."""
        print("=== Audit Log Entries ===")
        for log in self.logs:
            time_str = log.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
            print(f"[{time_str}] User: '{log.username}' -> Action: {log.action}")


class UserAccount:
    """Управління обліковим записом через композицію (User, Session, AuditLog)."""

    def __init__(self, user: User, audit_log: AuditLog | None = None) -> None:
        self.user = user
        self.session: Session | None = None
        self.audit_log = audit_log if audit_log is not None else AuditLog()

    def login(self, username: str, password: str, ip: str) -> bool:
        """Виконує аутентифікацію та відкриває сесію."""
        if not self.user.active or self.user.username != username:
            self.audit_log.add_log(username, "login_failure")
            return False

        if self.user.check_password(password):
            self.session = Session(ip)
            self.session.touch()
            self.audit_log.add_log(username, "login_success")
            return True

        self.audit_log.add_log(username, "login_failure")
        return False

    def is_authenticated(self) -> bool:
        """Перевіряє дійсність сесії."""
        if self.session is None:
            return False
        return self.session.is_active(SESSION_TIMEOUT_SEC)

    def logout(self) -> None:
        """Завершує сесію та реєструє вихід."""
        if self.session:
            self.audit_log.add_log(self.user.username, "logout")
            self.session = None

    def __getitem__(self, key: str) -> str | bool | None:
        """Отримання значень атрибутів за ключем."""
        if key in (
            "__password_hash",
            "__password_salt",
            "password_hash",
            "password_salt",
        ):
            raise KeyError("Доступ до хешу та солі пароля заборонено!")
        allowed_keys = {
            "username": self.user.username,
            "email": self.user.email,
            "role": self.user.role,
            "active": self.user.active,
            "is_authenticated": self.is_authenticated(),
        }
        if key not in allowed_keys:
            raise KeyError(f"Невідомий ключ: '{key}'")
        return allowed_keys[key]

    def __setitem__(self, key: str, value: str | bool) -> None:
        """Зміна дозволених атрибутів за ключем."""
        if key in (
            "__password_hash",
            "__password_salt",
            "password_hash",
            "password_salt",
        ):
            raise KeyError("Доступ до хешу та солі пароля заборонено!")
        if key == "email":
            if not isinstance(value, str):
                raise TypeError("Значення email має бути рядком.")
            self.user.email = value
        elif key == "active":
            if not isinstance(value, bool):
                raise TypeError("Значення active має бути булевим типом.")
            self.user.active = value
        else:
            raise KeyError(
                f"Зміна атрибута '{key}' не підтримується через __setitem__."
            )
