from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.db import session_scope
from src.models import Employee, HRTicket, User


def insert_roster(employees: Iterable[Employee], users: Iterable[User]) -> None:
    with session_scope() as session:
        session.add_all(list(employees))
        session.add_all(list(users))


def get_employee(employee_id: str) -> Employee | None:
    with session_scope() as session:
        return session.get(Employee, employee_id)


def get_employee_by_email(email: str) -> Employee | None:
    with session_scope() as session:
        return session.scalar(
            select(Employee)
            .options(joinedload(Employee.user))
            .where(Employee.email == email.lower())
        )


def insert_ticket(employee_id: str, topic: str, details: str = "") -> HRTicket:
    with session_scope() as session:
        ticket = HRTicket(employee_id=employee_id, topic=topic, details=details)
        session.add(ticket)
        session.flush()
        return ticket
