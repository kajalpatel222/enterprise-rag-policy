"""Create and save an embedding for the first chunk only."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHUNK_PATH = PROJECT_ROOT / "data" / "processed" / "preview" / "first_chunk.json"
OUTPUT_PATH = (
    PROJECT_ROOT / "data" / "processed" / "preview" / "first_chunk_embedding.json"
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    logger.info("Loaded configuration from %s", PROJECT_ROOT / ".env")
    logger.info("Embedding provider: %s", os.environ["OPENROUTER_BASE_URL"])
    logger.info("Embedding model: %s", os.environ["EMBEDDING_MODEL"])

    chunk = json.loads(CHUNK_PATH.read_text(encoding="utf-8"))
    text = chunk["text"]
    logger.info("Selected chunk: %s", chunk["section_title"])
    logger.info("Source file: %s", chunk["source_file"])
    logger.info("Text length: %d characters", len(text))
    logger.info("Text preview: %s...", " ".join(text.split())[:120])

    embeddings = OpenAIEmbeddings(
        model=os.environ["EMBEDDING_MODEL"],
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url=os.environ["OPENROUTER_BASE_URL"],
    )
    logger.info("Sending text to the embedding model")
    vector = embeddings.embed_query(text)
    logger.info("Received vector with %d dimensions", len(vector))

    result = {
        "source_file": chunk["source_file"],
        "section_title": chunk["section_title"],
        "embedding_model": os.environ["EMBEDDING_MODEL"],
        "dimension": len(vector),
        "vector": vector,
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    logger.info("Saved embedding artifact: %s", OUTPUT_PATH)
    logger.info("First five vector values: %s", vector[:5])


if __name__ == "__main__":
    main()
