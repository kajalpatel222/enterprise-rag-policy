# LangGraph Smoke Review 1

## Purpose

Verify that the implemented LangGraph workflow preserves the tested retrieval and answer
behavior on both conditional model branches.

## Results

| ID | Route | Total time | Quality review |
| --- | --- | ---: | --- |
| EQ2-18 | Complex | 7.08s | Correctly identifies the Day-90 versus six-month conflict without choosing a rule. |
| EQ2-19 | Standard | 1.93s | Gives a concise, faithful unsupported-answer response. |

Both requests completed within the 10-second target. LangGraph adds orchestration but does not
add another model call, so its overhead is negligible compared with retrieval and generation.

