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
    prompt = f"""You are a helpful internal ACME policy assistant.
Answer the employee's question using only the policy context below.
If the context does not contain the answer, say that the policy corpus does not provide
enough information. Speak naturally and directly, like a knowledgeable colleague helping
an employee. Start with the answer instead of repeating the question.
For a simple question, use one or two short paragraphs rather than a bullet list.
Use bullets only when the question asks for several separate steps, comparisons, or items.
When an answer comes from multiple policy sections, prefer one concise sentence per
section using this style: "Under **[Policy Section]**, ...". Keep the answer concise and
cite the relevant section title naturally in the sentence.
If the same requirement appears in more than one section, state it only once and cite
the supporting sections together instead of repeating the requirement.
For scenario questions, include the controls needed to resolve that scenario and omit
nearby policy details that do not change the answer.
Preserve conditional wording exactly: do not turn "if applicable", "if involved", or
similar conditions into unconditional requirements.
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
    return answer, time.perf_counter() - answer_start
