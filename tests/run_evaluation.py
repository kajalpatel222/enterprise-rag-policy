"""Run evaluation questions through the same pipeline used by the chat app."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# When this file is run directly, Python starts with tests/ on its import path.
# Adding the project root lets it find the reusable src package.
sys.path.insert(0, str(PROJECT_ROOT))

from src.rag_pipeline import answer_question, create_components, retrieve


def load_questions(eval_path: Path) -> list[dict[str, str]]:
    """Read question IDs and questions from an evaluation markdown table."""
    table_row = re.compile(
        r"^\|\s*((?:EQ-\d+|EQ2-\d+))\s*\|\s*(.*?)\s*\|",
        re.MULTILINE,
    )
    contents = eval_path.read_text(encoding="utf-8")
    return [
        {"id": question_id, "question": question}
        for question_id, question in table_row.findall(contents)
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a RAG evaluation set")
    parser.add_argument(
        "--eval-file",
        default="evals/evaluation_questions_1.md",
        help="Evaluation markdown file relative to the project root",
    )
    parser.add_argument(
        "--output",
        default="reports/evaluation_results_4.json",
        help="Output JSON file relative to the project root",
    )
    args = parser.parse_args()
    eval_path = PROJECT_ROOT / args.eval_file
    output_path = PROJECT_ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    questions = load_questions(eval_path)
    vector_store, chat = create_components()
    results: list[dict[str, object]] = []

    for item in questions:
        question_start = time.perf_counter()
        retrieval_start = time.perf_counter()
        retrieved = retrieve(vector_store, item["question"])
        retrieval_seconds = time.perf_counter() - retrieval_start
        answer, answer_seconds = answer_question(chat, item["question"], retrieved)

        results.append(
            {
                "id": item["id"],
                "question": item["question"],
                "top_score": retrieved[0]["score"],
                "top_vector_score": retrieved[0]["vector_score"],
                "top_keyword_score": retrieved[0]["keyword_score"],
                "top_section": retrieved[0]["metadata"].get("section_title"),
                "retrieval_seconds": retrieval_seconds,
                "answer_seconds": answer_seconds,
                "total_seconds": time.perf_counter() - question_start,
                "answer": answer,
                "retrieved": [
                    {
                        "score": item["score"],
                        "vector_score": item["vector_score"],
                        "keyword_score": item["keyword_score"],
                        "section_title": item["metadata"].get("section_title"),
                        "source_file": item["metadata"].get("source_file"),
                    }
                    for item in retrieved
                ],
            }
        )
        # Save after every question so an interrupted run does not lose earlier work.
        output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"Completed {item['id']} ({len(results)}/{len(questions)})", flush=True)

    print("| ID | Retrieval (s) | Answer (s) | Total (s) | Top Section |")
    print("| --- | ---: | ---: | ---: | --- |")
    for result in results:
        print(
            f"| {result['id']} | {result['retrieval_seconds']:.2f} | "
            f"{result['answer_seconds']:.2f} | {result['total_seconds']:.2f} | "
            f"{result['top_section']} |"
        )
    print(f"\nFull results saved to {output_path}")


if __name__ == "__main__":
    main()
