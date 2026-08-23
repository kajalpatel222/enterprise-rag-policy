# Week 2 Project Documentation

## Project Overview

**One-liner:** This RAG application helps ACME employees answer HR, compliance, security, and
technical policy questions from three curated enterprise documents in a Streamlit chat
interface, targeting grounded answers and an end-to-end response time below 10 seconds.

The application retrieves policy evidence from Pinecone, reranks results for semantic and
exact-term relevance, routes questions through LangGraph, and generates answers that cite the
relevant policy sections. It also refuses questions that the corpus cannot answer.

## RAG Framework Decisions

| Field | Decision |
| --- | --- |
| Use case | Employees ask single-policy, multi-policy, process, comparison, conflict, and unsupported questions through a Streamlit chatbot. |
| Corpus | Three English plain-text ACME documents covering HR, compliance/security, and technical policy; 26 numbered sections are treated as the source of truth. |
| Ingestion and cleaning | Local text files are read as UTF-8. Numbered headings and document version information are identified; no source facts are rewritten or removed. |
| Ingestion and freshness | Indexing is currently run manually when a source document changes. Stable chunk IDs update the existing Pinecone records during re-indexing; production could trigger this process automatically on source changes. |
| Chunking and embedding | Structural chunking keeps one numbered policy section together and attaches source, department, version, section, and subsection metadata. The configured OpenAI-compatible embedding model creates dense vectors through OpenRouter. |
| Retrieval | Pinecone returns 10 dense semantic candidates. Local exact-term overlap is combined with the vector score using 70% semantic and 30% keyword weighting, and the best 5 chunks become model context. |
| Generation | LangGraph routes simple questions to GPT-4.1-mini and complex questions to Gemini 3.7 Flash. The prompt requires grounded, concise, conditional, and naturally cited answers. |
| Evaluation | Twenty questions cover direct retrieval, exact terms, multi-document synthesis, processes, comparisons, policy conflicts, and unsupported requests. Retrieval and generation latency are recorded separately. |
| Constraints | Target latency is below 10 seconds. The system should not invent missing policies, silently resolve contradictions, or remove conditional wording. |

## Dataset

The fictional ACME corpus contains:

| Dataset | Scope | Sections |
| --- | --- | ---: |
| `hr_policy.txt` | Leave, remote work, conduct, performance, onboarding, and disciplinary policy | 10 |
| `compliance_manual.txt` | Privacy, security, incident response, acceptable use, vendors, audit, and continuity | 7 |
| `tech_docs.txt` | Authentication, rate limits, errors, webhooks, deployment, and related technical guidance | 9 |

The full inventory, document versions, and corpus boundary are recorded in
`docs/corpus_inventory.md`.

## Architecture

The system has two flows:

1. **Offline indexing:** source files -> structural chunks -> LangChain Documents -> embeddings
   -> Pinecone.
2. **Online answering:** question -> retrieve 10 -> exact-term rerank -> keep 5 -> LangGraph
   routing -> grounded answer -> Streamlit.

Detailed diagrams are available in `docs/architecture.md`. The compiled LangGraph diagram is
stored in `docs/rag_graph.mmd`, with a rendered screenshot in `docs/rag_graph.jpg`.

## LangChain and LangGraph

LangChain provides the `Document`, `OpenAIEmbeddings`, `PineconeVectorStore`, and `ChatOpenAI`
building blocks. LangGraph carries shared request state and controls the conditional standard
or complex answer branch.

The graph state includes the question, retrieved chunks, route, route reason, answer, retrieval
time, and answer-generation time. LangGraph adds orchestration but no additional model call.

## Prompt and Instructions

The production prompt in `src/rag_pipeline.py` instructs the model to:

- Use only retrieved policy context and refuse unsupported questions.
- Speak naturally and answer directly.
- Use paragraphs for simple answers and bullets for steps, comparisons, or multiple controls.
- Preserve conditions such as "if applicable" and avoid invented obligations or urgency.
- Explain policy conflicts without selecting an unsupported rule.
- Include all requested actions, deadlines, exceptions, and contacts for multi-part questions.
- Avoid duplicated facts and unrelated details.

## Iterations

| Iteration | What was tested | Learning or decision |
| --- | --- | --- |
| Dense retrieval baseline | Pinecone semantic search | Good semantic coverage, but exact technical terms needed more influence. |
| Larger candidate set | Retrieve 10 instead of 5 | Improved the opportunity to recover relevant chunks before final selection. |
| Exact-term reranking | 70% vector score plus 30% local keyword overlap | Improved exact names, acronyms, error codes, and technical-term retrieval without another model call. |
| Prompt refinement | Refusal, conditional language, conflict handling, concise format | Reduced hallucination, repetition, and nearby-policy oversharing. |
| Evidence-first experiment | One model call extracted evidence and a second wrote the answer | Conflict handling improved, but latency and cost rose and extraction sometimes omitted facts; not enabled. |
| Model comparison | GPT-4o-mini, GPT-4.1-mini, and stronger alternatives | Cheaper models worked for simple questions but were less reliable for exact terms and multi-policy reasoning. |
| Model routing | Standard and complex models selected by deterministic rules | Preserved lower cost for simple lookups while improving complex answers without a classifier call. |
| LangGraph orchestration | Retrieval -> route -> standard/complex answer branch | Made request state and branching explicit while preserving existing RAG behavior. |

## Evaluation Results

The final LangGraph run evaluated all 20 questions:

- 18 clean passes
- 2 passes with minor issues
- 0 failures
- 2/2 unsupported questions safely refused
- Average end-to-end latency: 4.86 seconds
- Median end-to-end latency: 4.61 seconds
- 19/20 answers completed within the 10-second target
- Slowest answer: 10.39 seconds

Known minor findings are documented rather than hidden: one broad scenario omitted two policy
qualifiers and exceeded the latency target by 0.39 seconds, while one direct answer added a
reasonable but not explicitly stated explanatory sentence.

The complete per-question review is in `reports/evaluation_langgraph_full_review_1.md`, and the
raw outputs, timings, routes, and retrieved sections are in
`reports/evaluation_langgraph_full_1.json`.

## Learnings and Observations

- Retrieval quality and answer quality are separate. A model can omit a fact even when the
  correct chunk was retrieved.
- Structural chunking worked well because each numbered section represents one policy topic.
- Dense search handles meaning; local exact-term reranking helps names, numbers, and acronyms.
- More model calls do not automatically improve quality; evidence-first answering increased
  latency and introduced a new omission point.
- Deterministic model routing provided a useful cost-quality tradeoff without classifier cost.
- Honest evaluation includes unsupported questions, contradictory policies, and known defects,
  not only successful examples.

## Current Limitations

- Index freshness is manual rather than scheduled.
- Keyword matching is exact and does not stem words such as `terminate` and `terminated`.
- Chat history is temporary Streamlit session state and is not sent to the model for follow-up
  question resolution.
- The retrieval blend is a local hybrid-style reranker, not a native Pinecone dense-sparse index.
- The project corpus is intentionally small and fictional.

## AI Coding Tools

Codex was used as a coding partner to explain Python incrementally, organize the repository,
implement and test retrieval experiments, create evaluation reports, add LangGraph, and review
submission readiness. Architecture, cost, latency, prompt, and quality decisions were reviewed
interactively rather than accepting generated changes without evaluation.

