# Five-Minute Demo Outline

## 0:00-0:35 - Problem and Goal

- Introduce the Enterprise Policy Q&A Bot.
- Explain that employees otherwise search separate HR, compliance, and technical documents.
- State the goal: grounded answers, visible sources, safe refusals, and responses around the
  10-second target.

## 0:35-1:15 - Corpus and Indexing

- Show `data/raw/` and the three policy files.
- Show `src/prepare_chunks.py`: one numbered section becomes one structural chunk with metadata.
- Show `src/index_corpus.py`: chunks become LangChain Documents, are embedded, and stored in
  Pinecone using stable IDs.

## 1:15-2:05 - Retrieval and LangGraph

- Show `docs/rag_graph.jpg` or the Mermaid diagram.
- Explain: retrieve 10 dense candidates, apply 30% exact-term reranking, keep 5.
- Explain the LangGraph state and its standard versus complex model branch.
- Clarify that LangChain performs embeddings, Pinecone access, and model calls; LangGraph
  controls the workflow.

## 2:05-3:25 - Live Application

- Open Streamlit and expand the retrieval settings.
- Ask one challenging multi-policy question.
- Show the conversational answer, policy-section citations, selected route, retrieved sources,
  and timings.
- Ask one unsupported question such as: "Does ACME provide a home-office equipment stipend?"
- Show the safe refusal.

## 3:25-4:20 - Evaluation

- Open `reports/evaluation_langgraph_full_review_1.md`.
- Explain the 20-question mix: direct, exact term, multi-document, process, comparison, conflict,
  and unsupported questions.
- State the results: 18 clean passes, 2 minor passes, 0 failures, 4.86-second average, and 19/20
  within 10 seconds.
- Mention the two known minor issues to demonstrate honest evaluation.

## 4:20-5:00 - Iterations and Learning

- Summarize dense retrieval, top-10 candidates, exact-term reranking, prompt refinement,
  evidence-first experimentation, model comparison, routing, and LangGraph.
- Explain that evidence-first was rejected because it increased latency and omitted facts.
- Close with the main lesson: good RAG depends on chunking, retrieval, grounded generation, and
  evaluation together, not only on choosing a powerful model.

