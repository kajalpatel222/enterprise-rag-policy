"""Run evaluation questions through the same pipeline used by the chat app."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# When this file is run directly, Python starts with tests/ on its import path.
# Adding the project root lets it find the reusable src package.
sys.path.insert(0, str(PROJECT_ROOT))

from src.rag_pipeline import (
    answer_question,
    create_components,
    retrieve,
    select_answer_model,
)


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
    parser.add_argument(
        "--ids",
        help="Optional comma-separated question IDs, for example EQ2-04,EQ2-18",
    )
    parser.add_argument(
        "--routed",
        action="store_true",
        help="Route complex questions to COMPLEX_CHAT_MODEL",
    )
    args = parser.parse_args()
    eval_path = PROJECT_ROOT / args.eval_file
    output_path = PROJECT_ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    questions = load_questions(eval_path)
    if args.ids:
        # Running only selected IDs keeps focused checks faster and less expensive.
        selected_ids = {question_id.strip() for question_id in args.ids.split(",")}
        questions = [item for item in questions if item["id"] in selected_ids]
        missing_ids = selected_ids - {item["id"] for item in questions}
        if missing_ids:
            raise ValueError(f"Question IDs not found: {', '.join(sorted(missing_ids))}")
    vector_store, standard_chat, complex_chat = create_components()
    results: list[dict[str, object]] = []

    for item in questions:
        question_start = time.perf_counter()
        retrieval_start = time.perf_counter()
        retrieved = retrieve(vector_store, item["question"])
        retrieval_seconds = time.perf_counter() - retrieval_start
        if args.routed:
            chat, route, route_reason = select_answer_model(
                item["question"],
                standard_chat,
                complex_chat,
            )
        else:
            chat = standard_chat
            route = "standard"
            route_reason = "routing disabled"
        answer, answer_seconds = answer_question(chat, item["question"], retrieved)

        results.append(
            {
                "id": item["id"],
                "question": item["question"],
                "route": route,
                "route_reason": route_reason,
                "model": (
                    os.environ["COMPLEX_CHAT_MODEL"]
                    if route == "complex"
                    else os.environ["CHAT_MODEL"]
                ),
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
