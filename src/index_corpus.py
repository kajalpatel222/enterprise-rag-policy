"""Embed the policy corpus through OpenRouter and upsert it into Pinecone."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

try:
    from .prepare_chunks import RAW_DATA_DIR, extract_chunks
except ImportError:
    from prepare_chunks import RAW_DATA_DIR, extract_chunks


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def build_documents() -> tuple[list[Document], list[str]]:
    """Turn policy sections into LangChain Documents and stable record IDs."""
    documents: list[Document] = []
    ids: list[str] = []

    for path in sorted(RAW_DATA_DIR.glob("*/*.txt")):
        for chunk in extract_chunks(path):
            # Pinecone metadata describes the chunk; page_content is what gets embedded.
            metadata = {key: value for key, value in chunk.items() if key != "text"}
            chunk_id = (
                f"{metadata['department']}-"
                f"{metadata['document_version']}-"
                f"section-{metadata['section_number']}"
            )
            documents.append(Document(page_content=chunk["text"], metadata=metadata))
            ids.append(chunk_id)

    return documents, ids


def main() -> None:
    # Load API keys and project settings from the local .env file.
    load_dotenv(PROJECT_ROOT / ".env")
    required = [
        "PINECONE_API_KEY",
        "PINECONE_INDEX_NAME",
        "PINECONE_NAMESPACE",
        "OPENROUTER_API_KEY",
        "OPENROUTER_BASE_URL",
        "EMBEDDING_MODEL",
    ]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")

    # Build all documents before making the embedding and Pinecone calls.
    documents, ids = build_documents()
    embeddings = OpenAIEmbeddings(
        model=os.environ["EMBEDDING_MODEL"],
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url=os.environ["OPENROUTER_BASE_URL"],
    )
    vector_store = PineconeVectorStore(
        index_name=os.environ["PINECONE_INDEX_NAME"],
        namespace=os.environ["PINECONE_NAMESPACE"],
        embedding=embeddings,
        pinecone_api_key=os.environ["PINECONE_API_KEY"],
    )
    # LangChain embeds each document and upserts the vectors plus metadata.
    vector_store.add_documents(documents=documents, ids=ids)

    print(f"Indexed {len(documents)} chunks")
    print(f"Namespace: {os.environ['PINECONE_NAMESPACE']}")
    print(f"First ID: {ids[0]}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Indexing failed: {error}", file=sys.stderr)
        raise
