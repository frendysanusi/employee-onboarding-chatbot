# Employee Onboarding Chatbot

An **agentic RAG** onboarding assistant for the (fictional) Umbrella Corporation. The goal:
new employees log in by ID and ask questions about company policies, benefits, and safety
protocols. A LangGraph tool-calling agent decides which source to consult — a Pinecone
vector store of policy documents (with reranking) or the employee's own profile — and
answers with page-level citations.

## Stack

- **Streamlit** — chat UI with streaming and a source panel
- **LangGraph** — agentic tool-calling loop (OpenAI `gpt-4o`)
- **Pinecone** serverless — vector store (`text-embedding-3-small`)
- **Cohere** — reranking of retrieved passages
- **Postgres** — persistent conversation threads (LangGraph checkpointer)
- **LangSmith** — optional tracing
