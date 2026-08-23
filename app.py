"""Streamlit chat interface for the Enterprise Policy Q&A Bot."""

from __future__ import annotations

import streamlit as st

from src.rag_graph import create_rag_graph
from src.rag_pipeline import create_components


st.set_page_config(page_title="ACME Policy Assistant")


@st.cache_resource
def load_pipeline():
    """Create and cache the clients plus the compiled LangGraph workflow."""
    vector_store, standard_chat, complex_chat = create_components()
    return create_rag_graph(vector_store, standard_chat, complex_chat)


st.title("ACME Policy Assistant")
st.caption("Ask questions about the enterprise policy corpus.")

with st.sidebar:
    st.subheader("Retrieval settings")
    st.write("Semantic candidates: 10")
    st.write("Exact-term reranking: 30%")
    st.write("Answer context: top 5 chunks")
    st.write("Orchestration: LangGraph")
    st.divider()
    st.caption("Answers are grounded in the indexed policy documents.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("sources"):
            with st.expander("Retrieved sources"):
                st.caption(
                    f"Answer route: {message.get('route', 'standard')} · "
                    f"{message.get('route_reason', 'answered before routing was enabled')}"
                )
                for source in message["sources"]:
                    st.markdown(
                        f"**{source['section']}**  \n"
                        f"`{source['file']}` · hybrid score: `{source['score']:.3f}`"
                    )
                st.caption(
                    f"Retrieval: {message['retrieval_seconds']:.2f}s · "
                    f"Answer: {message['answer_seconds']:.2f}s"
                )

question = st.chat_input("Ask an enterprise policy question")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            graph = load_pipeline()
            result = graph.invoke({"question": question})
            retrieved = result["retrieved"]
            route = result["route"]
            route_reason = result["route_reason"]
            answer = result["answer"]
            retrieval_seconds = result["retrieval_seconds"]
            answer_seconds = result["answer_seconds"]
            st.markdown(answer)

            sources = [
                {
                    "section": item["metadata"].get("section_title", "Unknown section"),
                    "file": item["metadata"].get("source_file", "Unknown file"),
                    "score": item["score"],
                }
                for item in retrieved
            ]
            with st.expander("Retrieved sources"):
                st.caption(f"Answer route: {route} · {route_reason}")
                for source in sources:
                    st.markdown(
                        f"**{source['section']}**  \n"
                        f"`{source['file']}` · hybrid score: `{source['score']:.3f}`"
                    )
                st.caption(
                    f"Retrieval: {retrieval_seconds:.2f}s · "
                    f"Answer: {answer_seconds:.2f}s"
                )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "retrieval_seconds": retrieval_seconds,
                    "answer_seconds": answer_seconds,
                    "route": route,
                    "route_reason": route_reason,
                }
            )
        except Exception as error:
            # Keep the error visible during development without exposing secret values.
            st.error(f"The assistant could not answer this question: {error}")
