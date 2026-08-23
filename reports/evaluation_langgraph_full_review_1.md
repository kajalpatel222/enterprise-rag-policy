# LangGraph Full Evaluation Review 1

## Summary

- Evaluation set: `evals/evaluation_questions_2.md` (20 questions)
- Execution path: implemented LangGraph workflow (`--graph`)
- Result file: `reports/evaluation_langgraph_full_1.json`
- Routes used: 16 complex, 4 standard
- Correct/faithful verdicts: 18 pass, 2 pass with minor issues, 0 fail
- Retrieval coverage: all questions retrieved enough evidence to answer or refuse safely
- Unsupported questions: 2/2 correctly refused without inventing policy
- Latency target: 19/20 completed within 10 seconds

## Timing

| Metric | Result |
| --- | ---: |
| Average total time | 4.86 s |
| Median total time | 4.61 s |
| Average retrieval time | 0.49 s |
| Average answer time | 4.36 s |
| Fastest | EQ2-20, 1.07 s |
| Slowest | EQ2-07, 10.39 s |
| Within 10-second target | 95% (19/20) |

The answer-model call accounts for most latency. Retrieval is generally fast; the 2.05-second retrieval for EQ2-08 was the highest retrieval time but still acceptable.

## Per-Question Audit

| ID | Verdict | Time | Quality audit |
| --- | --- | ---: | --- |
| EQ2-01 | Pass | 4.79 s | Correct Day 1 activities and least-privilege principle. Concise, natural, complete, and well structured. |
| EQ2-02 | Pass | 6.25 s | Correct HR/Legal approval, DPO approval, and EEA transfer mechanisms. Conditions are preserved and detail is proportional. |
| EQ2-03 | Pass | 6.96 s | Correct P1 response/containment, GDPR deadline, conditional financial notice, state range, and reporting contacts. Bullets suit the multi-part request. |
| EQ2-04 | Pass | 6.98 s | Correct 429 meaning, `Retry-After`, exponential backoff with jitter, and one-hour token validity. Conversational and complete. |
| EQ2-05 | Pass | 4.35 s | Correct two-hour access revocation and three-year retention period. Short and natural, with no unrelated detail. |
| EQ2-06 | Pass | 6.99 s | Correct full vendor approval sequence, personal-data DPO review, cross-border mechanism, and high-risk CISO sign-off. Appropriately detailed for a process question. |
| EQ2-07 | Pass with minor issues | 10.39 s | Faithful and readable, but omits the explicit least-privilege requirement and the remote workspace's `distraction-free` qualifier. It is also the only response over the latency target. The remaining detail is defensible because the question broadly asks which protections apply. |
| EQ2-08 | Pass | 7.14 s | Correct Tier 1 RTO/RPO, backup cadence, restoration testing, and region. Clean comparison format. |
| EQ2-09 | Pass | 5.11 s | Correct test gates, canary configuration, threshold, and rollback. It focuses on checks affecting full rollout rather than narrating every mechanical pipeline step. |
| EQ2-10 | Pass | 2.86 s | Correct five retries, exponential backoff, HMAC-SHA256 validation, signature header, and rejection behavior. Complete and concise. |
| EQ2-11 | Pass | 4.40 s | Correct authenticity purpose and rejection requirement. Direct answer with no oversharing. |
| EQ2-12 | Pass | 1.58 s | Correct distinction between wait duration and Unix reset timestamp. Backoff guidance is relevant and grounded. |
| EQ2-13 | Pass | 3.85 s | Correct RTO and RPO values. Concise; the corpus provides labels and values rather than deeper formal definitions. |
| EQ2-14 | Pass | 7.10 s | Correct MFA trigger and every listed password control. Bullets are appropriate and easy to scan. |
| EQ2-15 | Pass with minor issue | 1.97 s | Core answer is correct: SIG Lite or CAIQ is selected according to vendor criticality. The final claim that this ensures a consistent and appropriate security-posture evaluation is a reasonable inference, but it is not directly stated in the corpus. |
| EQ2-16 | Pass | 5.67 s | Correctly contrasts Article 33's 72-hour authority notice with the 30-day data-request deadline and preserves the high-risk condition for individual notice. |
| EQ2-17 | Pass | 4.44 s | Correctly identifies the two annual external audit activities and frequency. Concise and well formatted. |
| EQ2-18 | Pass | 4.02 s | Correctly recognizes and explains the Day-90 versus six-month policy conflict without choosing an unsupported rule. |
| EQ2-19 | Pass | 1.21 s | Correct safe refusal: no home-office stipend appears in the corpus. Short and clear. |
| EQ2-20 | Pass | 1.07 s | Correct safe refusal: no payroll cutoff appears in the corpus. No invented deadline. |

## Submission Assessment

The LangGraph workflow is functioning end to end: it retrieves and reranks evidence, routes questions, calls the selected answer model, and returns grounded output. The evaluation demonstrates multi-policy synthesis, exact technical-term handling, conflict detection, conditional rules, process answers, comparisons, and safe refusal.

The run is suitable as submission evidence. The two minor answer issues should be documented as known evaluation findings rather than hidden. No application code or prompts were changed during this audit.
