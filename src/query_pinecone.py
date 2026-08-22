"""Retrieve the most relevant policy chunks for one question."""

from __future__ import annotations

import json
import logging
import os
import argparse
import re
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "preview" / "retrieval_results.json"

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "by",
    "can",
    "does",
    "how",
    "is",
    "must",
    "of",
    "the",
    "to",
    "what",
    "when",
    "with",
}


def keyword_score(question: str, text: str) -> float:
    """Measure how many meaningful question terms appear in a chunk."""
    question_terms = {
        word
        for word in re.findall(r"\b[a-z0-9]+\b", question.lower())
        if word not in STOP_WORDS
    }
    text_terms = set(re.findall(r"\b[a-z0-9]+\b", text.lower()))
    if not question_terms:
        return 0.0
    return len(question_terms & text_terms) / len(question_terms)


def main() -> None:
    # Read the question from the terminal instead of hardcoding it in the file.
    parser = argparse.ArgumentParser(description="Retrieve policy chunks for a question")
    parser.add_argument("--question", required=True, help="The employee question")
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="How many chunks to return after hybrid ranking (default: 5)",
    )
    parser.add_argument(
        "--candidate-k",
        type=int,
        default=10,
        help="How many semantic candidates to retrieve first (default: 10)",
    )
    args = parser.parse_args()
    question = args.question
    # Load credentials and model settings without printing secret values.
    load_dotenv(PROJECT_ROOT / ".env")
    logger.info("Question: %s", question)

    logger.info("Embedding the question with %s", os.environ["EMBEDDING_MODEL"])

    # The question must use the same embedding model as the indexed documents.
    embeddings = OpenAIEmbeddings(
        model=os.environ["EMBEDDING_MODEL"],
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url=os.environ["OPENROUTER_BASE_URL"],
    )
    # This object knows how to query our existing Pinecone index.
    vector_store = PineconeVectorStore(
        index_name=os.environ["PINECONE_INDEX_NAME"],
        namespace=os.environ["PINECONE_NAMESPACE"],
        embedding=embeddings,
        pinecone_api_key=os.environ["PINECONE_API_KEY"],
    )

    logger.info("Searching Pinecone for %d semantic candidates", args.candidate_k)
    # First retrieve a broad semantic shortlist from Pinecone.
    matches = vector_store.similarity_search_with_score(question, k=args.candidate_k)
    scored_matches = []
    for document, vector_score in matches:
        lexical_score = keyword_score(question, document.page_content)
        # Combine meaning similarity with exact term overlap locally.
        hybrid_score = (0.7 * vector_score) + (0.3 * lexical_score)
        scored_matches.append((document, vector_score, lexical_score, hybrid_score))
    scored_matches.sort(key=lambda item: item[3], reverse=True)
    selected_matches = scored_matches[: args.top_k]
    logger.info("Selected top %d chunks after hybrid ranking", len(selected_matches))
    results = [
        {
            "score": hybrid_score,
            "vector_score": vector_score,
            "keyword_score": lexical_score,
            "text": document.page_content,
            "metadata": document.metadata,
        }
        for document, vector_score, lexical_score, hybrid_score in selected_matches
    ]
    # Save retrieval results so we can inspect them before asking the chat model.
    OUTPUT_PATH.write_text(
        json.dumps(
            {"question": question, "results": results},
            indent=2,
        ),
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
