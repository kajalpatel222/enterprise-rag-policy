"""Generate one answer from the retrieval snapshot saved by query_pinecone.py."""

from __future__ import annotations

import json
import logging

try:
    # This works when the file is run as part of the src package.
    from .rag_pipeline import PROJECT_ROOT, answer_question, create_components
except ImportError:
    # This also supports the beginner-friendly command: python src/answer_one_question.py
    from rag_pipeline import PROJECT_ROOT, answer_question, create_components


RETRIEVAL_PATH = PROJECT_ROOT / "data" / "processed" / "preview" / "retrieval_results.json"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "preview" / "answer_result.json"

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    # Read the question and retrieved chunks produced by query_pinecone.py.
    retrieval = json.loads(RETRIEVAL_PATH.read_text(encoding="utf-8"))
    question = retrieval["question"]
    _vector_store, chat, _complex_chat = create_components()

    # The shared function builds the grounded prompt and calls the chat model.
    answer, _answer_seconds = answer_question(chat, question, retrieval["results"])
    result = {
        "question": question,
        "answer": answer,
        "sources": [
            {
                "section_title": item["metadata"]["section_title"],
                "source_file": item["metadata"]["source_file"],
                "score": item["score"],
            }
            for item in retrieval["results"]
        ],
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    logger.info("Answer received and saved to %s", OUTPUT_PATH)
    print(f"\nAnswer:\n{answer}")


if __name__ == "__main__":
    main()
