# Evidence-First Experiment Review

Model: `openai/gpt-4.1-mini`

The experiment compared the current one-call answer with a two-call flow:

1. Extract structured evidence from retrieved chunks.
2. Generate the final answer using only that evidence.

## Timing

| ID | Baseline total | Evidence-first total | Result |
| --- | ---: | ---: | --- |
| EQ2-03 | 3.64s | 7.33s | Under 10s |
| EQ2-07 | 3.74s | 12.06s | Failed latency target |
| EQ2-18 | 1.73s | 7.24s | Under 10s |

- Baseline average: 3.04 seconds
- Evidence-first average: 8.88 seconds

## Quality

### EQ2-03: P1 personal-data incident

- Improvement: removed the unsupported word “immediately.”
- Regression: evidence extraction omitted conditional state and financial notification
  requirements, so the final answer was incomplete.

### EQ2-07: Remote privileged administrator

- Improvement: preserved least privilege, MFA, quarterly review, individual/auditable
  accounts, shared-account prohibition, and full-disk encryption.
- Regression: evidence extraction omitted TLS, AES-256, and acceptable-use safeguards.
- Latency: 12.06 seconds exceeded the target.

### EQ2-18: Day 90 versus six months

- Improvement: the final answer recognized that the policy did not provide a clear rule,
  unlike the incorrect baseline answer.
- Limitation: the structured extractor put the discrepancy in missing information instead
  of explicitly recording it as a conflict.

## Decision

Do not enable this evidence-first flow in Streamlit yet. It improved conflict handling but
made completeness dependent on a first extraction call that can itself miss evidence. It
also raised average latency from 3.04 to 8.88 seconds and exceeded 10 seconds once.

The better next direction is model routing: keep a low-cost model for simple questions and
send difficult multi-policy or conflict questions to a stronger fixed model.
