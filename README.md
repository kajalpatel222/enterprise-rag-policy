# Enterprise Policy Q&A Bot

Week 2 RAG project workspace.

## Goal

Build a Python and Streamlit application that answers questions from a curated enterprise policy corpus, cites its sources, and refuses questions unsupported by the corpus.

## Workspace layout

- `data/raw/` - Source policy documents exactly as downloaded.
- `data/processed/` - Temporary generated files; the folder itself is kept empty in Git.
- `docs/architecture.md` - Diagrams for ingestion, retrieval, routing, and framework usage.
- `src/rag_graph.py` - LangGraph state and conditional answer-model workflow.
- `src/rag_pipeline.py` - Reusable Pinecone retrieval and grounded answer logic.
- `src/prepare_chunks.py` - Turns source policy sections into structured chunks.
- `src/index_corpus.py` - Embeds chunks and uploads them to Pinecone.
- `src/query_pinecone.py` - Optional terminal retrieval inspection tool.
- `src/answer_one_question.py` - Optional terminal answer inspection tool.
- `tests/run_evaluation.py` - Evaluation runner for the question sets in `evals/`.
- `reports/` - Evaluation results and project-submission material.

The Python files contain comments around the important steps: loading settings, embedding
questions, retrieving chunks, reranking exact terms, and asking the answer model. The
short version is: `rag_pipeline.py` is reusable logic; the other Python files are small
commands that call it for one specific job.

We will choose the corpus, retrieval strategy, and dependencies before adding application code.

## Current Retrieval Baseline

The current retrieval flow is intentionally simple:

1. Pinecone retrieves the top 10 candidates using dense semantic search.
2. Local keyword overlap scoring reranks those candidates.
3. LangGraph carries the retrieved state and routes the question by complexity.
4. The best 5 chunks are sent to the selected answer model.
5. The answer model must stay within the retrieved policy context.

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
The live request flow is orchestrated by LangGraph.

## Run an evaluation

```bash
python tests/run_evaluation.py \
  --eval-file evals/evaluation_questions_2.md \
  --output reports/evaluation_questions_2_results_2.json
```

The evaluation questions live in `evals/`, and each run is saved separately in `reports/`.
This keeps experiments from overwriting earlier results.

For a cheaper focused check, run only selected question IDs:

```bash
python tests/run_evaluation.py \
  --eval-file evals/evaluation_smoke.md \
  --ids EQ2-04,EQ2-18 \
  --output reports/evaluation_smoke_results.json
```
