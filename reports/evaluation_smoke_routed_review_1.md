# Routed Model Evaluation Review 1

## Configuration

- Standard route: `openai/gpt-4.1-mini`
- Complex route: `google/gemini-3.7-flash`
- Routing method: deterministic phrase and multi-part checks; no classifier LLM call
- Evaluation set: `evals/evaluation_smoke.md` (6 questions)

## Timing

- Average total time: 5.49 seconds
- Median total time: 5.23 seconds
- Fastest: EQ2-19 at 1.27 seconds on the standard route
- Slowest: EQ2-07 at 9.69 seconds on the complex route
- All six questions completed within the 10-second target.

## Quality Review

| ID | Route | Review |
| --- | --- | --- |
| EQ2-04 | Complex | Correct and complete: explains 429, retry headers/backoff, and token lifetime. |
| EQ2-07 | Complex | Faithful but initially overshared password and eligibility details. A focused retry removed them and retained applicable security and remote-work controls. |
| EQ2-10 | Complex | Correct and complete, including five retries, exponential backoff, and HMAC-SHA256 validation. |
| EQ2-13 | Complex | Faithful and concise. The corpus provides expanded names and values but does not define the operational concepts further. |
| EQ2-18 | Complex | Correctly identifies the Day-90 versus six-month conflict and does not choose one rule. |
| EQ2-19 | Standard | Correct, brief unsupported-answer response. |

## Decision

Keep routing enabled. It fixes the earlier exact-term and conflict failures while reserving
the stronger model for questions that combine, compare, or reconcile policy facts. The
standard route remains appropriate for simple lookups and unsupported questions.

The focused EQ2-07 retry took 9.93 seconds, so complex scenario latency should continue
to be monitored. The output remained within the current 10-second target.
