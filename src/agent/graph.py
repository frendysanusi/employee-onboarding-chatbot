from __future__ import annotations

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph

from config import settings
from src.agent.prompts import system_prompt
from src.agent.tools import build_tools
from src.models import Employee


def build_agent(employee: Employee, checkpointer=None) -> CompiledStateGraph:
    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0,
        streaming=True,
        stream_usage=True,
    )
    return create_agent(
        llm,
        build_tools(employee),
        system_prompt=system_prompt(employee),
        checkpointer=checkpointer,
    )
