"""Inspect policy retrieval from the terminal."""

from __future__ import annotations

import argparse
import json
import logging

try:
    # This works when the file is run as part of the src package.
    from .rag_pipeline import PROJECT_ROOT, create_components, retrieve
except ImportError:
    # This also supports the beginner-friendly command: python src/query_pinecone.py
    from rag_pipeline import PROJECT_ROOT, create_components, retrieve


OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "preview" / "retrieval_results.json"

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    # Read the question from the terminal instead of changing this file each time.
    parser = argparse.ArgumentParser(description="Retrieve policy chunks for a question")
    parser.add_argument("--question", required=True, help="The employee question")
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Chunks to return after reranking (default: 5)",
    )
    parser.add_argument(
        "--candidate-k",
        type=int,
        default=10,
        help="Semantic candidates to retrieve first (default: 10)",
    )
    args = parser.parse_args()

    # This shared function creates the Pinecone client and embedding model.
    vector_store, _chat = create_components()
    results = retrieve(
        vector_store,
        args.question,
        candidate_k=args.candidate_k,
        top_k=args.top_k,
    )

    # Save a human-readable snapshot so we can inspect retrieval separately from answering.
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps({"question": args.question, "results": results}, indent=2),
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
