from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import cohere
from openai import OpenAI
from pinecone import Index, Pinecone, ServerlessSpec

from config import settings
from utils.constants import EMBED_DIM, EMBED_MODEL, RERANK_MODEL
from utils.usage import log_usage


@dataclass(frozen=True, slots=True)
class Passage:
    text: str
    page: int
    score: float


@lru_cache
def _openai() -> OpenAI:
    return OpenAI(api_key=settings.openai_api_key)


@lru_cache
def _pinecone() -> Pinecone:
    return Pinecone(api_key=settings.pinecone_api_key)


@lru_cache
def _cohere() -> cohere.ClientV2:
    return cohere.ClientV2(api_key=settings.cohere_api_key)


@lru_cache
def get_index() -> Index:
    return _pinecone().Index(settings.pinecone_index)


def ensure_index() -> Index:
    pc = _pinecone()
    if not pc.has_index(settings.pinecone_index):
        pc.create_index(
            name=settings.pinecone_index,
            dimension=EMBED_DIM,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    return get_index()


def embed(texts: list[str]) -> list[list[float]]:
    response = _openai().embeddings.create(model=EMBED_MODEL, input=texts)
    log_usage(
        "openai",
        EMBED_MODEL,
        input_tokens=response.usage.prompt_tokens,
        total_tokens=response.usage.total_tokens,
    )
    return [item.embedding for item in response.data]


def search(query: str, candidates: int = 10, top_n: int = 4) -> list[Passage]:
    matches = get_index().query(
        vector=embed([query])[0],
        top_k=candidates,
        include_metadata=True,
    ).matches
    if not matches:
        return []

    documents = [m.metadata["text"] for m in matches]
    reranked = _cohere().rerank(
        model=RERANK_MODEL,
        query=query,
        documents=documents,
        top_n=min(top_n, len(documents)),
    )
    billed = getattr(getattr(reranked, "meta", None), "billed_units", None)
    if billed is not None:
        log_usage("cohere", RERANK_MODEL, search_units=getattr(billed, "search_units", 0) or 0)
    return [
        Passage(
            text=documents[r.index],
            page=int(matches[r.index].metadata.get("page", 0)),
            score=r.relevance_score,
        )
        for r in reranked.results
    ]
