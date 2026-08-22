"""Compare one-call answers with evidence-first answers on difficult questions."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.rag_pipeline import (
    answer_from_evidence,
    answer_question,
    create_components,
    extract_evidence,
    retrieve,
)


OUTPUT_PATH = PROJECT_ROOT / "reports" / "evidence_experiment_gpt4_1_mini_1.json"

# These questions exposed completeness, scope, and conflict-handling problems in mini models.
QUESTIONS = [
    {
        "id": "EQ2-03",
        "question": (
            "A P1 incident involves personal data exposed through an API. What are the "
            "response, containment, regulatory-notification, and reporting requirements?"
        ),
    },
    {
        "id": "EQ2-07",
        "question": "What protections apply to a privileged administrator who works remotely?",
    },
    {
        "id": "EQ2-18",
        "question": (
            "What are the remote-work rules for an employee who has completed Day 90 "
            "but not the 6-month probationary period?"
        ),
    },
]


def main() -> None:
    vector_store, chat = create_components()
    results: list[dict[str, object]] = []

    for item in QUESTIONS:
        retrieval_start = time.perf_counter()
        retrieved = retrieve(vector_store, item["question"])
        retrieval_seconds = time.perf_counter() - retrieval_start

        # Baseline: the model reads raw chunks and writes the answer in one call.
        baseline_answer, baseline_answer_seconds = answer_question(
            chat,
            item["question"],
            retrieved,
        )

        # Evidence-first: one call extracts facts; a second call writes from those facts.
        evidence, extraction_seconds = extract_evidence(
            chat,
            item["question"],
            retrieved,
        )
        evidence_answer, evidence_answer_seconds = answer_from_evidence(
            chat,
            item["question"],
            evidence,
        )

        results.append(
            {
                "id": item["id"],
                "question": item["question"],
                "retrieval_seconds": retrieval_seconds,
                "baseline": {
                    "answer": baseline_answer,
                    "answer_seconds": baseline_answer_seconds,
                    "total_seconds": retrieval_seconds + baseline_answer_seconds,
                },
                "evidence_first": {
                    "evidence": evidence.model_dump(),
                    "extraction_seconds": extraction_seconds,
                    "answer": evidence_answer,
                    "answer_seconds": evidence_answer_seconds,
                    "total_seconds": (
                        retrieval_seconds + extraction_seconds + evidence_answer_seconds
                    ),
                },
                "retrieved_sections": [
                    retrieved_item["metadata"].get("section_title")
                    for retrieved_item in retrieved
                ],
            }
        )
        OUTPUT_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"Completed {item['id']} ({len(results)}/{len(QUESTIONS)})", flush=True)

    print("| ID | Baseline (s) | Evidence extraction (s) | Evidence answer (s) | Total (s) |")
    print("| --- | ---: | ---: | ---: | ---: |")
    for result in results:
        baseline = result["baseline"]
        evidence_first = result["evidence_first"]
        print(
            f"| {result['id']} | {baseline['total_seconds']:.2f} | "
            f"{evidence_first['extraction_seconds']:.2f} | "
            f"{evidence_first['answer_seconds']:.2f} | "
            f"{evidence_first['total_seconds']:.2f} |"
        )
    print(f"\nFull results saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
