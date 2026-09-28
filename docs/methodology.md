# Methodology

This document describes DiaryBench Track 1, set50. It publishes the evaluation structure, not the exam itself. No example here is adapted from a real question.

## Task and source

The source is a long, private Chinese-language diary written by Brighton (Yi Xu). Models analyze the text across time, rather than classify isolated sentences as positive or negative. The author verifies which offered interpretations correspond to the experiences behind the writing.

The evaluation uses a fixed corpus and a fixed question set. Repeated runs within a version are intended to receive the same source material. Different question-set versions must not be pooled. The earlier set30 results are a historical snapshot, not additional runs of set50.

## Questions and labels

Set50 has **50 multi-select questions**, with **four options** and **1–3 correct options** per question. The correct-option count is not specified for individual items. Options offer nearby interpretations; a convincing analysis alone does not make an option correct.

The author validates labels. GLM-5.3 assisted with drafting part of the question set, introducing a possible phrasing/family-affinity confound. This is disclosed rather than assumed away. Private source text, question drafts, options and labels are not distributed as examples or authoring prompts.

The public website can show broad evidence-horizon and trap/clean aggregates. These describe the amount of context needed and the risk of unsupported interpretation. This repository's result CSV contains only whole-exam aggregates: no item identifiers, item-to-segment membership or item-level correctness.

## Evaluation rigs

| Rig | Evaluation setup |
|---|---|
| `api` | Per-question API calls with the diary context supplied as a shared prefix |
| `web` | Consumer web interface, generally answering the complete paper in a session |
| `harness` | An agent harness that can read the paper in chunks and manage its context |

These setups are not interchangeable. The result is a model in a particular evaluation setup; differences cannot be assigned to model capability or harness quality without a controlled comparison. Requested reasoning and answer formatting also do not guarantee identical internal model behavior.

The aggregate export reports rig and run count but does **not** provide a complete machine-readable record of generation settings, tool configuration, context management or attempt dates. Unreported temperature, token budgets and provider settings must not be guessed. The public scorer makes no model calls.

## Answer extraction

The requested format includes per-option reasoning and a `Final Answer:` line. API answers and whole-paper answers require different extraction steps. The public [scoring demo](../tools/score_demo.py) illustrates legacy single-response helpers; it is **not** a full implementation of the live web/harness paper extractor.

The illustrative legacy parser tries raw text first, then text with complete lowercase `<think>` blocks removed. Each pass uses its last regex-matched `Final Answer` payload, not its last successfully parsed answer. If no payload matches, a bare-letter-line fallback exists. This fallback is historical behavior, not a recommended output protocol; it can misinterpret all-letter prose. A malformed matched payload suppresses that fallback in the same pass. See the code and [synthetic tests](../tests/test_score_demo.py) for the exact boundaries, including whitespace and missing responses.

The demo rejects invalid keys and excess responses. An omitted trailing response contributes zero and counts as an evaluation error; it is never silently dropped by a shorter response list. Correct sets may be empty in the generic scoring helper, but the **actual set50 design has 1–3 correct options**.

## Metric

For question `i`, with selected set `S_i` and author-verified correct set `C_i`:

```text
J_i = |S_i ∩ C_i| / |S_i ∪ C_i|
run score = 100 × (J_1 + … + J_50) / 50
```

Each question has equal weight. Partial credit is built in; an incorrect extra selection increases the union without increasing the intersection. A missing or unparseable answer receives zero. The generic helper defines two empty sets as overlap 1, a boundary case outside the real set50 design.

**Entirely synthetic arithmetic example:** if `C = {A, C}` and `S = {A, B}`, the intersection has one option and the union three, giving `1/3`. These letters are invented for this example and have no connection to the exam.

## Aggregate reporting

For each evaluation configuration, the table reports the mean run score, observed minimum and maximum, run count and rig. The `_100` column suffix means a 0–100 score, not a fraction. Alternate effort tiers have separate CSV rows; the website may group them for display.

- Min–max is the observed range over available runs, **not** a confidence interval or standard deviation.
- A one-run configuration has no measured between-run variation.
- Mean and extrema have different historical rounding precision; preserve reported values rather than manufacture extra digits of accuracy.
- A configuration marked `refused=true` refused all reported attempts. Its displayed zero records the refusal outcome under the board policy, not a demonstrated zero comprehension score. Do not combine it with successfully answered runs without distinguishing that status.
- No per-attempt score log, per-question vectors, model reasoning or answer selections are published. Small-sample aggregates can nevertheless reveal individual run scores up to rounding (including all three scores when there are three runs and the mean/min/max are known). They do not recover the exam or its item-level answers, establish significance or estimate unreported variation.

See [results/README.md](../results/README.md) for the snapshot schema and [privacy.md](privacy.md) for the release boundary.
