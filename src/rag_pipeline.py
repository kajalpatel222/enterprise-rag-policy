"""Shared retrieval and answer-generation functions for the policy assistant."""

from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Common question words do not help identify the relevant policy section.
STOP_WORDS = {
    "a", "an", "and", "are", "by", "can", "does", "how", "is",
    "must", "of", "the", "to", "what", "when", "with",
}


def keyword_score(question: str, text: str) -> float:
    """Return the fraction of useful question words found in a text chunk."""
    question_terms = {
        word
        for word in re.findall(r"\b[a-z0-9]+\b", question.lower())
        if word not in STOP_WORDS
    }
    text_terms = set(re.findall(r"\b[a-z0-9]+\b", text.lower()))
    if not question_terms:
        return 0.0
    return len(question_terms & text_terms) / len(question_terms)


def create_components() -> tuple[PineconeVectorStore, ChatOpenAI]:
    """Create the Pinecone and chat-model clients from the local .env file."""
    load_dotenv(PROJECT_ROOT / ".env")

    # The same embedding model used during indexing must be used for questions.
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
    return vector_store, chat


def retrieve(
    vector_store: PineconeVectorStore,
    question: str,
    candidate_k: int = 10,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Retrieve semantic candidates, rerank them, and return the best chunks."""
    matches = vector_store.similarity_search_with_score(question, k=candidate_k)
    scored_matches = []
    for document, vector_score in matches:
        lexical_score = keyword_score(question, document.page_content)
        # Combine semantic similarity with exact-term overlap without another model call.
        hybrid_score = (0.7 * vector_score) + (0.3 * lexical_score)
        scored_matches.append((document, vector_score, lexical_score, hybrid_score))

    scored_matches.sort(key=lambda item: item[3], reverse=True)
    return [
        {
            "text": document.page_content,
            "metadata": document.metadata,
            "score": hybrid_score,
            "vector_score": vector_score,
            "keyword_score": lexical_score,
        }
        for document, vector_score, lexical_score, hybrid_score in scored_matches[:top_k]
    ]


def answer_question(
    chat: ChatOpenAI,
    question: str,
    retrieved: list[dict[str, Any]],
) -> tuple[str, float]:
    """Generate a concise answer using only the retrieved policy context."""
    context = "\n\n---\n\n".join(
        f"Source: {item['metadata'].get('source_file')}\n"
        f"Section: {item['metadata'].get('section_title')}\n"
        f"{item['text']}"
        for item in retrieved
    )
    prompt = f"""You are ACME's internal policy assistant.

Answer the question using only the policy context below.

Rules:
- If the answer is not in the context, say so clearly.
- Do not invent facts, deadlines, obligations, urgency, or interpretations.
- Preserve conditions such as "if applicable" and "if involved".
- Answer directly and conversationally without repeating the question.
- Use short paragraphs for simple questions; use bullets for steps, comparisons, or
  multiple requirements.
- For multiple policies, cite each relevant section once and do not repeat the same fact.
- For scenarios, include only controls that affect the answer.
- For conflicts, explain only the conflicting rules and what cannot be determined.
- For unsupported questions, give a brief refusal.

Question:
{question}

Policy context:
{context}
"""
    answer_start = time.perf_counter()
    answer = chat.invoke(prompt).content
    return answer, time.perf_counter() - answer_start
