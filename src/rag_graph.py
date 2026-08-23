"""LangGraph workflow that orchestrates retrieval, routing, and answering."""

from __future__ import annotations

import time
from typing import Any, Literal, TypedDict

from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langgraph.graph import END, START, StateGraph

from .rag_pipeline import answer_question, retrieve, select_answer_model


class RAGState(TypedDict, total=False):
    """Information carried from one graph node to the next."""

    question: str
    retrieved: list[dict[str, Any]]
    route: str
    route_reason: str
    answer: str
    retrieval_seconds: float
    answer_seconds: float


def create_rag_graph(
    vector_store: PineconeVectorStore,
    standard_chat: ChatOpenAI,
    complex_chat: ChatOpenAI,
):
    """Build and compile the policy assistant's LangGraph workflow."""

    def retrieve_node(state: RAGState) -> dict[str, Any]:
        """Find and rerank the policy evidence for the current question."""
        retrieval_start = time.perf_counter()
        retrieved = retrieve(vector_store, state["question"])
        return {
            "retrieved": retrieved,
            "retrieval_seconds": time.perf_counter() - retrieval_start,
        }

    def route_node(state: RAGState) -> dict[str, str]:
        """Record which answer path should handle the question and why."""
        _chat, route, reason = select_answer_model(
            state["question"],
            standard_chat,
            complex_chat,
        )
        return {"route": route, "route_reason": reason}

    def choose_answer_path(
        state: RAGState,
    ) -> Literal["answer_standard", "answer_complex"]:
        """Send graph state to exactly one of the two answer nodes."""
        if state["route"] == "complex":
            return "answer_complex"
        return "answer_standard"

    def answer_with_standard_model(state: RAGState) -> dict[str, Any]:
        """Answer a simple question with the lower-cost model."""
        answer, answer_seconds = answer_question(
            standard_chat,
            state["question"],
            state["retrieved"],
        )
        return {"answer": answer, "answer_seconds": answer_seconds}

    def answer_with_complex_model(state: RAGState) -> dict[str, Any]:
        """Answer a multi-part or reasoning-heavy question with the stronger model."""
        answer, answer_seconds = answer_question(
            complex_chat,
            state["question"],
            state["retrieved"],
        )
        return {"answer": answer, "answer_seconds": answer_seconds}

    graph = StateGraph(RAGState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("route", route_node)
    graph.add_node("answer_standard", answer_with_standard_model)
    graph.add_node("answer_complex", answer_with_complex_model)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "route")
    graph.add_conditional_edges("route", choose_answer_path)
    graph.add_edge("answer_standard", END)
    graph.add_edge("answer_complex", END)
    return graph.compile()

