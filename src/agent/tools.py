from __future__ import annotations

from langchain_core.tools import BaseTool, tool

from src.agent.prompts import tenure_label, tenure_months
from src.models import Employee
from src.repository import insert_ticket
from src.retriever import search


def build_tools(employee: Employee) -> list[BaseTool]:
    @tool
    def search_policies(query: str) -> str:
        """Search Umbrella Corporation's policy documents for information relevant to the
        query. Returns the most relevant passages, each prefixed with its source page like
        [p.12]; cite those page numbers in your answer."""
        passages = search(query)
        if not passages:
            return "No relevant policy information was found."
        return "\n\n".join(f"[p.{p.page}] {p.text}" for p in passages)

    @tool
    def check_benefit_eligibility(benefit: str) -> str:
        """Report the employee's length of service, for evaluating tenure-based eligibility
        (leave, benefits, etc.). Combine the returned tenure with the requirement stated in
        company policy (via search_policies). `benefit` is the benefit or leave type asked about."""
        months = tenure_months(employee.hire_date)
        return (
            f"{employee.name} has been employed for {tenure_label(employee.hire_date)} "
            f"({months} months), since {employee.hire_date:%B %d, %Y}. "
            f"Evaluate eligibility for '{benefit}' against the tenure requirement in policy."
        )

    @tool
    def escalate_to_hr(topic: str, details: str = "") -> str:
        """Raise an HR ticket when a request falls outside policy scope or needs human
        follow-up. `topic` is a short subject line; `details` optionally captures specifics."""
        ticket = insert_ticket(employee.employee_id, topic, details)
        return (
            f"Raised HR ticket #{ticket.id} regarding '{topic}'. "
            f"HR will follow up with {employee.name}."
        )

    return [search_policies, check_benefit_eligibility, escalate_to_hr]
