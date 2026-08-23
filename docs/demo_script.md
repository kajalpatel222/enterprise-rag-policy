# Five-Minute Demo Outline

## Before Recording

- Target a final duration of 4 minutes 30 seconds so there is buffer below the five-minute limit.
- Open only the tabs and files listed below; close email, messages, and unrelated browser tabs.
- Never open `.env` during the recording because it contains API keys.
- Turn on Do Not Disturb and test the microphone.
- On macOS, press `Command + Shift + 5`, choose the full screen or selected portion, open
  **Options**, select the microphone, and start recording.
- Keep Streamlit open at `http://localhost:8501`.
- Use the two exact live questions below because both were included in the final evaluation.

## Demo Tabs and Files

1. Streamlit application: `http://localhost:8501`
2. LangGraph image: `docs/rag_graph.jpg`
3. Structural chunker: `src/prepare_chunks.py`
4. Indexing pipeline: `src/index_corpus.py`
5. LangGraph implementation: `src/rag_graph.py`
6. Final evaluation: `reports/evaluation_langgraph_full_review_1.md`
7. GitHub repository: `https://github.com/kajalpatel222/enterprise-rag-policy`

## 0:00-0:35 - Problem and Goal

Show the Streamlit title and say:

> This is my Week 2 Enterprise Policy Q&A Bot. It helps employees answer questions across HR,
> compliance, security, and technical policies without manually searching separate documents.
> My goals were grounded answers, visible sources, safe refusals when information is missing,
> and an end-to-end response target below 10 seconds.

## 0:35-1:15 - Corpus and Indexing

Show `data/raw/`, `src/prepare_chunks.py`, and `src/index_corpus.py`. Say:

> My corpus contains three fictional ACME documents with 26 policy sections. I use structural
> chunking, so each numbered policy section becomes one chunk with metadata such as source,
> department, version, section title, and subsection titles. Each chunk becomes a LangChain
> Document. LangChain sends the text to the embedding model and stores the vector, text,
> metadata, and stable ID in Pinecone.

## 1:15-2:05 - Retrieval and LangGraph

Show `docs/rag_graph.jpg` and briefly show `src/rag_graph.py`. Say:

> For each question, Pinecone returns 10 dense semantic candidates. Local Python reranks them
> using 70 percent semantic similarity and 30 percent exact-term overlap, and the best five
> chunks become context. LangGraph carries the question, evidence, route, answer, and timings.
> It sends simple questions to GPT-4.1-mini and complex questions to Gemini 3.7 Flash. LangChain
> performs the embeddings, Pinecone integration, and model calls; LangGraph controls the flow.

## 2:05-3:25 - Live Application

Return to Streamlit and ask:

> What are the remote-work rules for an employee who has completed Day 90 but not the 6-month
> probationary period?

While it runs, say:

> This tests retrieval across two conflicting policy sections and should use the complex route.

After the answer appears, point out that it identifies both rules instead of silently choosing
one. Expand **Retrieved sources** and show the complex route, policy sections, and timings.

Then ask:

> Does ACME provide a home-office equipment stipend?

After the response, say:

> This information is absent from the corpus, so the assistant refuses safely instead of
> inventing a benefit. This simple lookup uses the standard lower-cost route.

## 3:25-4:20 - Evaluation

Open `reports/evaluation_langgraph_full_review_1.md` and say:

> I evaluated 20 questions covering direct answers, exact technical terms, multi-document
> synthesis, processes, comparisons, conflicts, and unsupported requests. The final run had 18
> clean passes, two passes with minor issues, and zero failures. Average latency was 4.86 seconds,
> and 19 of 20 answers finished within 10 seconds. I kept the two minor issues in the report
> instead of hiding them.

## 4:20-5:00 - Iterations and Learning

Show the GitHub repository and say:

> I iterated through dense retrieval, larger candidate sets, exact-term reranking, prompt
> refinement, multiple models, deterministic model routing, and LangGraph. I also tested an
> evidence-first two-call design, but rejected it because it increased latency and sometimes
> omitted facts. Codex helped me implement, explain, and evaluate these iterations, while I
> reviewed the outputs and made the architecture and quality decisions. My main learning is
> that good RAG depends on chunking, retrieval, grounded generation, and evaluation together,
> not only on selecting a powerful model.

## After Recording

1. Stop the recording before five minutes and play it once with sound.
2. Confirm no API key or `.env` content appears.
3. Upload the video to the chosen sharing platform and verify link permissions.
4. Submit the video URL, GitHub URL, and project-document URL in the Week 2 form.
