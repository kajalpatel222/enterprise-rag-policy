"""Generate one grounded answer from the saved retrieval results."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RETRIEVAL_PATH = PROJECT_ROOT / "data" / "processed" / "preview" / "retrieval_results.json"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "preview" / "answer_result.json"

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    retrieval = json.loads(RETRIEVAL_PATH.read_text(encoding="utf-8"))
    question = retrieval["question"]
    context = "\n\n---\n\n".join(
        f"Source: {result['metadata']['source_file']}\n"
        f"Section: {result['metadata']['section_title']}\n"
        f"{result['text']}"
        for result in retrieval["results"]
    )

    prompt = f"""Answer the employee's question using only the policy context below.
If the context does not contain the answer, say that the policy corpus does not provide
enough information. Keep the answer concise and cite the relevant section title.

Question:
{question}

Policy context:
{context}
"""

    logger.info("Sending retrieved context to chat model: %s", os.environ["CHAT_MODEL"])
    chat = ChatOpenAI(
        model=os.environ["CHAT_MODEL"],
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url=os.environ["OPENROUTER_BASE_URL"],
        temperature=0,
    )
    response = chat.invoke(prompt)
    answer = response.content
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
    OUTPUT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    logger.info("Answer received and saved to %s", OUTPUT_PATH)
    print(f"\nAnswer:\n{answer}")


if __name__ == "__main__":
    main()
