# GPT-4.1-mini Smoke Review

Model: `openai/gpt-4.1-mini`

## Timing

- Questions: 6
- Average total time: 2.35 seconds
- Slowest response: 3.77 seconds
- Fastest response: 1.16 seconds

## Quality

| ID | Result |
| --- | --- |
| EQ2-04 | Correct core answer, but overshared an unrequested refresh-token instruction. |
| EQ2-07 | Included more relevant controls than GPT-4o-mini, but omitted AES-256 and overshared general remote-work rules. |
| EQ2-10 | Correct and complete, including HMAC-SHA256 and X-ACME-Signature. |
| EQ2-13 | Correct numbers and clear comparison, with some general interpretation beyond the corpus wording. |
| EQ2-18 | Incorrect: selected the six-month rule instead of identifying the Day 90 versus six-month conflict. |
| EQ2-19 | Correct concise refusal. |

## Retrieval Check

Retrieval worked correctly for the failed conflict case: `REMOTE WORK POLICY` and
`ONBOARDING PROCESS` were the top two chunks. The model received both conflicting rules.

## Decision

GPT-4.1-mini is fast and improves exact technical completeness over GPT-4o-mini, but it
still does not meet the project's conflict-handling and completeness requirements. It is
not recommended as the final chat model with the current single-call answer pipeline.
