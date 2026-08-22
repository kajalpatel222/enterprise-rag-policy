# Evaluation Review: Version 2, Run 5

Run file: `evaluation_questions_2_results_5.json`

## Comparison

| Run | Average | Maximum | Assessment |
| --- | ---: | ---: | --- |
| Run 4 | 3.32s | 9.85s | Better answer scope and faithfulness |
| Run 5 | 3.75s | 8.84s | Shorter prompt, but more over-sharing |

## Findings

- The shorter prompt did not improve average latency. Model generation time remains the
  largest part of the response time.
- `EQ2-04` included refresh-token details that were not needed for the question.
- `EQ2-07` included monitoring, data-protection, and many remote-work details beyond the
  immediate question.
- `EQ2-08` included extra failover and exercise details.
- `EQ2-18` still included nearly every remote-work rule after explaining the conflict.
- `EQ2-19` was concise and improved compared with Run 4.

## Decision

Run 4 remains the better quality baseline. A shorter prompt is not automatically better:
the explicit scope instructions helped the model stay faithful and focused. The project
will keep the more explicit prompt until a smaller prompt can be tested without losing
answer discipline.
