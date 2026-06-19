from __future__ import annotations

import bcrypt

from src.models import Employee
from src.repository import get_employee_by_email


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def authenticate(email: str, password: str) -> Employee | None:
    employee = get_employee_by_email(email)
    if employee and employee.user and verify_password(password, employee.user.password_hash):
        return employee
    return None
