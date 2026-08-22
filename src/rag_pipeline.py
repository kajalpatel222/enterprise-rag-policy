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
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Common question words do not help identify the relevant policy section.
STOP_WORDS = {
    "a", "an", "and", "are", "by", "can", "does", "how", "is",
    "must", "of", "the", "to", "what", "when", "with",
}

# These phrases usually indicate that the model must combine, compare, or reconcile
# several policy facts. Routing them does not require another paid LLM call.
COMPLEX_QUESTION_MARKERS = {
    "but not",
    "compare",
    "difference",
    "how should",
    "process",
    "protections",
    "requirements",
    "safeguards",
    "steps",
    "what must",
}


class EvidenceFact(BaseModel):
    """One policy fact that is directly useful for answering the question."""

    section: str = Field(description="Policy section containing the fact")
    fact: str = Field(description="Exact fact, including required numbers and terms")
    condition: str | None = Field(
        default=None,
        description="Any condition such as 'if applicable'; null when unconditional",
    )


class EvidenceConflict(BaseModel):
    """Two or more policy facts that cannot all be applied as one clear rule."""

    sections: list[str] = Field(description="Sections containing the conflicting rules")
    description: str = Field(description="A concise explanation of the conflict")


class EvidencePacket(BaseModel):
    """Structured evidence extracted before the final answer is written."""

    facts: list[EvidenceFact]
    conflicts: list[EvidenceConflict]
    missing_information: list[str]


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


def create_chat_model(model_name: str) -> ChatOpenAI:
    """Create one OpenRouter chat client for a specific model."""
    return ChatOpenAI(
        model=model_name,
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url=os.environ["OPENROUTER_BASE_URL"],
        temperature=0,
    )


def create_components() -> tuple[PineconeVectorStore, ChatOpenAI, ChatOpenAI]:
    """Create Pinecone plus the standard and complex-question chat clients."""
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
    standard_chat = create_chat_model(os.environ["CHAT_MODEL"])
    complex_chat = create_chat_model(os.environ["COMPLEX_CHAT_MODEL"])
    return vector_store, standard_chat, complex_chat


def select_answer_model(
    question: str,
    standard_chat: ChatOpenAI,
    complex_chat: ChatOpenAI,
) -> tuple[ChatOpenAI, str, str]:
    """Choose a model using simple, visible rules instead of a classifier call."""
    normalized = question.lower()
    matched_markers = sorted(
        marker for marker in COMPLEX_QUESTION_MARKERS if marker in normalized
    )

    # Several clauses joined by commas and "and" usually form a multi-part request.
    is_multi_part = normalized.count(",") >= 1 and " and " in normalized
    if matched_markers:
        reason = f"complex phrase: {', '.join(matched_markers)}"
        return complex_chat, "complex", reason
    if is_multi_part:
        return complex_chat, "complex", "multiple requested parts"
    return standard_chat, "standard", "simple lookup or unsupported question"


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

Answer using only the policy context below. If the answer is not there, say so clearly.
Speak naturally and directly without repeating the question.

Writing rules:
- Use one or two short paragraphs for simple questions.
- Use bullets only for steps, comparisons, or multiple requirements.
- For multiple policies, cite each relevant section once and state duplicate facts once.
- For scenarios, prioritize rules triggered by the stated role or situation; omit general rules.
- Answer only what was requested; omit related facts from the same section unless needed.

Faithfulness rules:
- Do not invent facts, deadlines, obligations, urgency, or interpretations.
- Preserve conditions such as "if applicable" and "if involved".
- Apply a conditional rule only when its condition is present; otherwise state the condition.
- For conflicts, explain only the conflicting rules and what cannot be determined.
- For unsupported questions, give a brief refusal without nearby unrelated details.
- For multi-part questions, include every requested action, deadline, exception, and contact.

Question:
{question}

Policy context:
{context}
"""
    answer_start = time.perf_counter()
    answer = chat.invoke(prompt).content
    return answer, time.perf_counter() - answer_start


def extract_evidence(
    chat: ChatOpenAI,
    question: str,
    retrieved: list[dict[str, Any]],
) -> tuple[EvidencePacket, float]:
    """Extract relevant facts and conflicts before attempting an answer."""
    context = "\n\n---\n\n".join(
        f"Section: {item['metadata'].get('section_title')}\n{item['text']}"
        for item in retrieved
    )
    prompt = f"""Extract the policy evidence needed to answer the question.

Rules:
- Include every fact needed for each part of the question.
- Preserve exact numbers, deadlines, technical terms, and conditions.
- Exclude nearby facts that do not affect the answer.
- Compare all relevant sections and record contradictions as conflicts.
- Do not choose between conflicting rules.
- Record what is missing when the context cannot answer part of the question.

Question:
{question}

Policy context:
{context}
"""
    # Structured output forces the first call to return evidence instead of prose.
    structured_chat = chat.with_structured_output(EvidencePacket, method="json_schema")
    extraction_start = time.perf_counter()
    evidence = structured_chat.invoke(prompt)
    return evidence, time.perf_counter() - extraction_start


def answer_from_evidence(
    chat: ChatOpenAI,
    question: str,
    evidence: EvidencePacket,
) -> tuple[str, float]:
    """Write the final response using only a previously extracted evidence packet."""
    prompt = f"""You are a helpful internal ACME policy assistant.

Answer using only the structured evidence below.
- Answer directly and conversationally.
- Include every requested fact, condition, deadline, exact term, and contact.
- State conflicts without selecting a rule.
- If evidence is missing, say the policy corpus does not provide enough information.
- Do not add facts or interpretations that are absent from the evidence.
- Use short paragraphs unless steps or multiple requirements need bullets.

Question:
{question}

Structured evidence:
{evidence.model_dump_json(indent=2)}
"""
    answer_start = time.perf_counter()
    answer = chat.invoke(prompt).content
    return answer, time.perf_counter() - answer_start
