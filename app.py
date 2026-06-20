from __future__ import annotations

import streamlit as st
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    HumanMessage,
    ToolMessage,
)
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from config import settings
from src.agent.graph import build_agent
from src.agent.prompts import WELCOME_MESSAGE
from src.auth import authenticate
from utils.usage import log_usage

st.set_page_config(page_title="Umbrella Onboarding Assistant", page_icon="☂️")


@st.cache_resource
def get_checkpointer() -> PostgresSaver:
    pool = ConnectionPool(
        settings.database_url,
        kwargs={"autocommit": True, "row_factory": dict_row},
        open=True,
    )
    checkpointer = PostgresSaver(pool)
    checkpointer.setup()
    return checkpointer


def thread_config(employee) -> dict:
    return {"configurable": {"thread_id": f"emp-{employee.employee_id}"}}


def load_history(agent, config) -> list[dict]:
    state = agent.get_state(config)
    messages = state.values.get("messages", []) if state.values else []
    history: list[dict] = []
    pending_sources: list[str] = []
    for message in messages:
        if isinstance(message, HumanMessage):
            history.append({"role": "user", "content": message.content, "sources": []})
        elif isinstance(message, ToolMessage) and message.name == "search_policies":
            pending_sources.append(message.content)
        elif isinstance(message, AIMessage) and message.content:
            history.append(
                {"role": "assistant", "content": message.content, "sources": pending_sources}
            )
            pending_sources = []
    return history


def stream_response(agent, config, user_text: str, sources: list[str]):
    for chunk, _ in agent.stream(
        {"messages": [{"role": "user", "content": user_text}]},
        config,
        stream_mode="messages",
    ):
        if isinstance(chunk, AIMessageChunk):
            if chunk.content:
                yield chunk.content
            if chunk.usage_metadata:
                log_usage("openai", settings.openai_model, **chunk.usage_metadata)
        elif isinstance(chunk, ToolMessage) and chunk.name == "search_policies":
            sources.append(chunk.content)


def render_sources(sources: list[str]) -> None:
    if sources:
        with st.expander("Sources"):
            for source in sources:
                st.markdown(source)


def login_view() -> None:
    st.title("☂️ Umbrella Corporation")
    st.caption("Employee Onboarding Assistant")

    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")

    if submitted:
        employee = authenticate(email, password)
        if employee is None:
            st.error("Invalid email or password.")
            return
        st.session_state.employee = employee
        st.session_state.agent = build_agent(employee, checkpointer=get_checkpointer())
        st.session_state.messages = load_history(
            st.session_state.agent, thread_config(employee)
        )
        st.rerun()


def sidebar(employee) -> None:
    with st.sidebar:
        st.header(f"{employee.name} {employee.lastname}")
        st.caption(f"{employee.position} · {employee.department}")
        st.write(f"**Location:** {employee.location}")
        st.write(f"**Start date:** {employee.hire_date:%B %d, %Y}")
        st.write(f"**Skills:** {', '.join(employee.skills)}")
        if st.button("Log out"):
            for key in ("employee", "agent", "messages"):
                st.session_state.pop(key, None)
            st.rerun()


def chat_view(employee) -> None:
    sidebar(employee)
    config = thread_config(employee)

    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown(WELCOME_MESSAGE)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            render_sources(message.get("sources", []))

    if prompt := st.chat_input("Ask about policies, benefits, or safety protocols…"):
        st.session_state.messages.append({"role": "user", "content": prompt, "sources": []})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            sources: list[str] = []
            answer = st.write_stream(
                stream_response(st.session_state.agent, config, prompt, sources)
            )
            render_sources(sources)
        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "sources": sources}
        )


st.session_state.setdefault("employee", None)
st.session_state.setdefault("messages", [])

if st.session_state.employee is None:
    login_view()
else:
    chat_view(st.session_state.employee)
