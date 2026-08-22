# GPT-4o-mini Smoke Review

Model: `openai/gpt-4o-mini`

## Timing

- Questions: 6
- Average total time: 2.04 seconds
- Slowest response: 2.91 seconds
- Fastest response: 0.93 seconds

## Quality

| ID | Result |
| --- | --- |
| EQ2-04 | Correct and appropriately scoped. |
| EQ2-07 | Undershared: omitted least-privilege, individual/auditable accounts, shared-account prohibition, and relevant acceptable-use controls. |
| EQ2-10 | Incomplete: omitted the required HMAC-SHA256 signature method. |
| EQ2-13 | Correct numbers, but described RTO/RPO using interpretation not explicitly defined in the corpus. |
| EQ2-18 | Incorrect: selected the six-month rule instead of identifying the Day 90 versus six-month conflict. |
| EQ2-19 | Correct concise refusal. |

## Retrieval Check

Retrieval worked correctly for the failed cases:

- EQ2-18 retrieved both `REMOTE WORK POLICY` and `ONBOARDING PROCESS` as the top two chunks.
- EQ2-10 retrieved `WEBHOOKS` as the top chunk.
- EQ2-07 retrieved `REMOTE WORK POLICY`, `INFORMATION SECURITY POLICY`, and `ACCEPTABLE USE POLICY` as the top three chunks.

## Decision

GPT-4o-mini is much faster and cheaper, but this run does not meet the current faithfulness
and completeness target. It should not replace the stronger model without either a more
specialized answer pipeline or another model comparison.
