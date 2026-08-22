"""Run the evaluation questions through retrieval and grounded answer generation."""

from __future__ import annotations

import json
import argparse
import logging
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

try:
    from .query_pinecone import keyword_score
except ImportError:
    from query_pinecone import keyword_score


PROJECT_ROOT = Path(__file__).resolve().parents[1]

logging.basicConfig(level=logging.WARNING, format="%(levelname)s | %(message)s")


def load_questions(eval_path: Path) -> list[dict[str, str]]:
    """Read question IDs and questions from the evaluation markdown table."""
    table_row = re.compile(r"^\|\s*((?:EQ-\d+|EQ2-\d+))\s*\|\s*(.*?)\s*\|", re.MULTILINE)
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

    load_dotenv(PROJECT_ROOT / ".env")
    questions = load_questions(eval_path)

    # Both the documents and the questions must use the same embedding model.
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
    chat = ChatOpenAI(
        model=os.environ["CHAT_MODEL"],
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url=os.environ["OPENROUTER_BASE_URL"],
        temperature=0,
    )

    results: list[dict[str, object]] = []
    for item in questions:
        question = item["question"]
        question_start = time.perf_counter()
        # Retrieve a broad semantic shortlist before applying exact-term scoring.
        retrieval_start = time.perf_counter()
        matches = vector_store.similarity_search_with_score(question, k=10)
        scored_matches = []
        for document, vector_score in matches:
            lexical_score = keyword_score(question, document.page_content)
            hybrid_score = (0.7 * vector_score) + (0.3 * lexical_score)
            scored_matches.append(
                (document, vector_score, lexical_score, hybrid_score)
            )
        scored_matches.sort(key=lambda item: item[3], reverse=True)
        selected_matches = scored_matches[:5]
        retrieval_seconds = time.perf_counter() - retrieval_start
        context = "\n\n---\n\n".join(
            f"Source: {document.metadata.get('source_file')}\n"
            f"Section: {document.metadata.get('section_title')}\n"
            f"{document.page_content}"
            for document, _vector_score, _lexical_score, _hybrid_score in selected_matches
        )

        # The prompt tells the model to stay inside the retrieved evidence.
        prompt = f"""Answer the employee's question using only the policy context below.
If the context does not contain the answer, say that the policy corpus does not provide
enough information. Keep the answer concise and cite the relevant section title.
Do not add facts, deadlines, obligations, or interpretations that are not directly stated
in the context. For a direct question, answer only what was asked. For a multi-part or
process question, include every relevant action, deadline, notification requirement,
exception, and contact found in the context, while avoiding unrelated policy details.
Question:
{question}

Policy context:
{context}
"""
        answer_start = time.perf_counter()
        answer = chat.invoke(prompt).content
        answer_seconds = time.perf_counter() - answer_start
        total_seconds = time.perf_counter() - question_start
        top_document, vector_score, lexical_score, top_score = selected_matches[0]
        results.append(
            {
                "id": item["id"],
                "question": question,
                "top_score": top_score,
                "top_vector_score": vector_score,
                "top_keyword_score": lexical_score,
                "top_section": top_document.metadata.get("section_title"),
                "retrieval_seconds": retrieval_seconds,
                "answer_seconds": answer_seconds,
                "total_seconds": total_seconds,
                "answer": answer,
                "retrieved": [
                    {
                        "score": hybrid_score,
                        "vector_score": vector_score,
                        "keyword_score": lexical_score,
                        "section_title": document.metadata.get("section_title"),
                        "source_file": document.metadata.get("source_file"),
                    }
                    for document, vector_score, lexical_score, hybrid_score in selected_matches
                ],
            }
        )
        # Save after each question so a long evaluation can resume safely after an interruption.
        output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"Completed {item['id']} ({len(results)}/{len(questions)})", flush=True)

    output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

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
