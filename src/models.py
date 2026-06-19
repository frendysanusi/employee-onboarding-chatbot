from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Employee(Base):
    __tablename__ = "employees"

    employee_id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    lastname: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    phone_number: Mapped[str | None]
    position: Mapped[str]
    department: Mapped[str]
    skills: Mapped[list[str]] = mapped_column(JSONB, default=list)
    location: Mapped[str]
    hire_date: Mapped[date]
    salary: Mapped[float | None] = mapped_column(Numeric(10, 2, asdecimal=False))

    user: Mapped[User | None] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )
    tickets: Mapped[list[HRTicket]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    password_hash: Mapped[str]
    employee_id: Mapped[str] = mapped_column(
        ForeignKey("employees.employee_id"), unique=True
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    employee: Mapped[Employee] = relationship(back_populates="user")


class HRTicket(Base):
    __tablename__ = "hr_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees.employee_id"))
    topic: Mapped[str]
    details: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    employee: Mapped[Employee] = relationship(back_populates="tickets")
