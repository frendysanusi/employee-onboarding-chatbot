from __future__ import annotations

import re
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from src.retriever import embed, ensure_index
from utils.constants import CHUNK_OVERLAP, CHUNK_SIZE, EMBED_BATCH_SIZE

PDF_PATH = Path("data/umbrella_corp_policies.pdf")


def normalize(text: str) -> str:
    text = text.replace("\t", " ")
    text = re.sub(r"[ ]{2,}", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def build_chunks(pdf_path: Path) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    source = pdf_path.stem
    chunks: list[dict] = []
    for page_number, page in enumerate(PdfReader(str(pdf_path)).pages, start=1):
        text = normalize(page.extract_text() or "")
        if not text:
            continue
        for chunk_index, chunk in enumerate(splitter.split_text(text)):
            chunks.append(
                {
                    "id": f"{source}-p{page_number}-c{chunk_index}",
                    "text": chunk,
                    "page": page_number,
                }
            )
    return chunks


def upsert_chunks(chunks: list[dict]) -> None:
    index = ensure_index()
    for start in range(0, len(chunks), EMBED_BATCH_SIZE):
        batch = chunks[start : start + EMBED_BATCH_SIZE]
        vectors = embed([c["text"] for c in batch])
        index.upsert(
            vectors=[
                {
                    "id": c["id"],
                    "values": vector,
                    "metadata": {"text": c["text"], "page": c["page"]},
                }
                for c, vector in zip(batch, vectors)
            ]
        )


def main() -> None:
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

    chunks = build_chunks(PDF_PATH)

    print(f"Extracted {len(chunks)} chunks from {PDF_PATH.name}")

    upsert_chunks(chunks)

    print(f"Upserted {len(chunks)} vectors to Pinecone index.")


if __name__ == "__main__":
    main()
