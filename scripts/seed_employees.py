from __future__ import annotations

import argparse

from src.auth import hash_password
from src.repository import insert_roster
from factories.employees import generate_roster
from src.models import User

DEFAULT_PASSWORD = "Umbrella2026!"


def main(count: int, password: str) -> None:
    employees = generate_roster(count)
    password_hash = hash_password(password)
    users = [
        User(password_hash=password_hash, employee_id=e.employee_id)
        for e in employees
    ]
    insert_roster(employees, users)

    print(f"Seeded {len(employees)} employees. Shared password: {password}\n")
    print("Log in with any of these emails:\n")
    for e in employees:
        print(f"  {e.email:<32} {e.position} ({e.department})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--count", type=int, default=8, help="number of employees")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help="shared login password")
    args = parser.parse_args()
    main(args.count, args.password)
