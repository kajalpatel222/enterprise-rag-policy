"""Run the evaluation questions through retrieval and grounded answer generation."""

from __future__ import annotations

import json
import logging
import os
import re
import textwrap
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVAL_PATH = PROJECT_ROOT / "evals" / "evaluation_questions_1.md"
OUTPUT_PATH = PROJECT_ROOT / "reports" / "evaluation_results_1.json"

logging.basicConfig(level=logging.WARNING, format="%(levelname)s | %(message)s")


def load_questions() -> list[dict[str, str]]:
    """Read question IDs and questions from the evaluation markdown table."""
    table_row = re.compile(r"^\|\s*(EQ-\d+)\s*\|\s*(.*?)\s*\|", re.MULTILINE)
    contents = EVAL_PATH.read_text(encoding="utf-8")
    return [
        {"id": question_id, "question": question}
        for question_id, question in table_row.findall(contents)
    ]


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    questions = load_questions()

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
        matches = vector_store.similarity_search_with_score(question, k=3)
        context = "\n\n---\n\n".join(
            f"Source: {document.metadata.get('source_file')}\n"
            f"Section: {document.metadata.get('section_title')}\n"
            f"{document.page_content}"
            for document, _score in matches
        )

        # The prompt tells the model to stay inside the retrieved evidence.
        prompt = f"""Answer the employee's question using only the policy context below.
If the context does not contain the answer, say that the policy corpus does not provide
enough information. Keep the answer concise and cite the relevant section title.
For multi-part or process questions, include every relevant action, deadline, notification
requirement, exception, and contact found in the context. Do not omit important details
just to make the answer shorter.

Question:
{question}

Policy context:
{context}
"""
        answer = chat.invoke(prompt).content
        top_document, top_score = matches[0]
        results.append(
            {
                "id": item["id"],
                "question": question,
                "top_score": top_score,
                "top_section": top_document.metadata.get("section_title"),
                "answer": answer,
                "retrieved": [
                    {
                        "score": score,
                        "section_title": document.metadata.get("section_title"),
                        "source_file": document.metadata.get("source_file"),
                    }
                    for document, score in matches
                ],
            }
        )

    OUTPUT_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("| ID | Top Score | Top Section | Answer |")
    print("| --- | ---: | --- | --- |")
    for result in results:
        answer = textwrap.shorten(str(result["answer"]), width=180, placeholder="...")
        answer = answer.replace("|", "\\|").replace("\n", " ")
        print(
            f"| {result['id']} | {result['top_score']:.4f} | "
            f"{result['top_section']} | {answer} |"
        )
    print(f"\nFull results saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
