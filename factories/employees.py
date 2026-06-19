from __future__ import annotations

import random

from faker import Faker

from src.models import Employee

fake = Faker()

COMMON_SKILLS = ("Project Management", "Data Analysis", "Technical Writing")

ORG = {
    "Research & Development": {
        "positions": (
            "Research Scientist",
            "Virologist",
            "Geneticist",
            "Lab Technician",
            "Biosafety Officer",
        ),
        "skills": (
            "Viral Engineering",
            "Gene Therapy",
            "Biodefense Research",
            "BSL-4 Containment",
            "Specimen Handling",
        ),
    },
    "Manufacturing & Production": {
        "positions": (
            "Production Engineer",
            "Manufacturing Technician",
            "Process Chemist",
            "Operations Manager",
        ),
        "skills": (
            "Process Scale-Up",
            "GMP Compliance",
            "Quality Control",
            "Supply Chain Management",
        ),
    },
    "Quality Assurance & Control": {
        "positions": (
            "QA Analyst",
            "Compliance Officer",
            "Quality Control Inspector",
            "Regulatory Affairs Specialist",
        ),
        "skills": (
            "Regulatory Compliance",
            "Audit & Inspection",
            "Quality Assurance",
            "Risk Assessment",
        ),
    },
    "Security & Emergency Response": {
        "positions": (
            "Security Officer",
            "Containment Specialist",
            "Emergency Response Coordinator",
            "Surveillance Analyst",
        ),
        "skills": (
            "Incident Response",
            "Containment Protocols",
            "Access Control",
            "Crisis Management",
        ),
    },
    "Administrative & Support Services": {
        "positions": (
            "HR Specialist",
            "Facilities Manager",
            "Procurement Officer",
            "Finance Analyst",
        ),
        "skills": (
            "Human Resources",
            "Procurement",
            "Facilities Management",
            "Budgeting",
        ),
    },
}

LOCATIONS = (
    "Raccoon City HQ",
    "Umbrella Europe",
    "Umbrella Asia",
    "Umbrella South America",
    "Secret Underground Facility",
)


def generate_employee() -> Employee:
    name = fake.first_name()
    lastname = fake.last_name()
    department = random.choice(list(ORG))
    unit = ORG[department]
    skill_pool = unit["skills"] + COMMON_SKILLS

    return Employee(
        employee_id=fake.uuid4(),
        name=name,
        lastname=lastname,
        email=f"{name}.{lastname}@umbrellacorp.com".lower(),
        phone_number=fake.phone_number(),
        position=random.choice(unit["positions"]),
        department=department,
        skills=random.sample(skill_pool, k=random.randint(2, 4)),
        location=random.choice(LOCATIONS),
        hire_date=fake.date_between(start_date="-5y", end_date="today"),
        salary=round(random.uniform(40_000, 120_000), 2),
    )


def generate_roster(n: int = 8) -> list[Employee]:
    return [generate_employee() for _ in range(n)]
