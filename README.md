# Enterprise Policy Q&A Bot

Week 2 RAG project workspace.

## Goal

Build a Python and Streamlit application that answers questions from a curated enterprise policy corpus, cites its sources, and refuses questions unsupported by the corpus.

## Workspace layout

- `data/raw/` - Source policy documents exactly as downloaded.
- `data/processed/` - Cleaned, chunked, or derived data created by the pipeline.
- `src/` - Application and RAG pipeline code.
- `notebooks/` - Small experiments and retrieval comparisons.
- `tests/` - Evaluation questions and automated checks.
- `reports/` - Evaluation results and project-submission material.

We will choose the corpus, retrieval strategy, and dependencies before adding application code.

## Current Retrieval Baseline

The current retrieval flow is intentionally simple:

1. Pinecone retrieves the top 10 candidates using dense semantic search.
2. Local keyword overlap scoring reranks those candidates.
3. The best 5 chunks are sent to the answer model.
4. The answer model must stay within the retrieved policy context.

This approach improves exact-term retrieval without adding another LLM call or creating a
second sparse Pinecone index. The initial performance goal is an end-to-end response under
10 seconds, measured separately for retrieval and answer generation.

## Run the chat interface

From the project root:

```bash
source .venv/bin/activate
streamlit run app.py
```

The browser interface uses the same retrieval baseline as the evaluation runner. Expand
`Retrieved sources` below an answer to inspect the sections and response timing.
