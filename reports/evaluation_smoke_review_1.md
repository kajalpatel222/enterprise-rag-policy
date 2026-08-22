# Targeted Quality Audit

This audit intentionally used a small, diverse question set instead of another full paid
evaluation run.

## Coverage

- Simple cross-policy answer
- Multi-policy scenario
- Incident response process
- Direct technical scope
- Vendor approval process
- Privileged-access scenario
- Exact technical terms
- RTO/RPO comparison
- Conflicting policies
- Unsupported question

## Timing

- Five-question smoke test average: 3.65 seconds
- Five-question smoke test maximum: 7.45 seconds
- Focused EQ2-04 check: 3.05 seconds
- Partial Run 6 contained one 11.57-second response, showing model/API variability

## Quality Findings

- Correctness: requested facts, deadlines, contacts, and technical terms were correct.
- Faithfulness: no unsupported requirement was found in the final smoke answers.
- Duplicate handling: repeated requirements were stated once in the tested answers.
- Oversharing: the direct-scope rule removed unrelated refresh-token details from EQ2-04.
- Conflict handling: EQ2-18 explained only the Day 90 versus six-month conflict.
- No-answer behavior: EQ2-19 gave a brief refusal without unrelated benefit details.
- Format: simple answers used paragraphs; process and comparison answers used lists.
- Tone: answers were direct and readable, without sounding like raw retrieved text.

## Remaining Considerations

- EQ2-07 is the longest smoke answer because the question broadly asks for all protections.
  Its details are relevant, but the question can be narrowed when a shorter answer is wanted.
- The configured chat model is `~openai/gpt-latest`. This alias can resolve to a newer
  flagship model without a code change, so quality, latency, and pricing are not fixed.
- Pin a concrete OpenRouter model slug before final benchmarking or deployment.

## Decision

The clean, structured prompt with explicit scope and faithfulness rules is the strongest
current version. Future prompt checks should use the smoke set and `--ids` before deciding
whether a full 20-question evaluation is necessary.
