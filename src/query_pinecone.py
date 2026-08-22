"""Retrieve the most relevant policy chunks for one question."""

from __future__ import annotations

import json
import logging
import os
import argparse
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "preview" / "retrieval_results.json"

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrieve policy chunks for a question")
    parser.add_argument("--question", required=True, help="The employee question")
    args = parser.parse_args()
    question = args.question
    load_dotenv(PROJECT_ROOT / ".env")
    logger.info("Question: %s", question)
    logger.info("Embedding the question with %s", os.environ["EMBEDDING_MODEL"])

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

    logger.info("Searching Pinecone for the top 3 matches")
    matches = vector_store.similarity_search_with_score(question, k=3)
    results = [
        {
            "score": score,
            "text": document.page_content,
            "metadata": document.metadata,
        }
        for document, score in matches
    ]
    OUTPUT_PATH.write_text(
        json.dumps({"question": question, "results": results}, indent=2),
        encoding="utf-8",
    )

    logger.info("Retrieved %d chunks", len(results))
    for index, result in enumerate(results, start=1):
        logger.info(
            "Result %d: score=%.4f, section=%s",
            index,
            result["score"],
            result["metadata"].get("section_title"),
        )
    logger.info("Saved results to %s", OUTPUT_PATH)


if __name__ == "__main__":
    main()
