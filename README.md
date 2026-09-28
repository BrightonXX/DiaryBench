# DiaryBench

**Nuanced emotional reasoning over long-form Chinese diaries.**

DiaryBench tests whether a model can follow emotional meaning across a long sequence of text: distinguish nearby interpretations, connect evidence across time, and avoid both under-interpreting and over-interpreting it. The source is my private diary. I am Brighton (Yi Xu), its author, and I verify the answers against the experiences behind the writing.

[Live leaderboard](https://brightonxu.com/works/llm-benchmark/) · [Methodology](docs/methodology.md) · [Public results](results/board_set50.csv) · [Scoring demo](tools/score_demo.py)

## At a glance

| Component | Public description |
|---|---|
| Task | Emotional interpretation of a long Chinese-language diary |
| Evaluation | Track 1, set50: 50 multi-select questions; four options each, 1–3 correct |
| Metric | Mean question-level Jaccard overlap, reported on a 0–100 scale |
| Ground truth | Author-verified labels, retained privately |
| Results | Mean, observed minimum/maximum, run count, rig and refusal flag |
| Release boundary | Methods, aggregate results, scoring code and fully synthetic examples; no exam material |

## What it measures

Most prominent LLM evaluations emphasize coding, tools or general reasoning. DiaryBench explores a different task: fine-grained analysis of emotionally dense writing over time. A plausible psychological explanation is not sufficient; the selected interpretations must agree with the author's verified labels.

The evaluation covers close reading, temporal reconstruction, Chinese internet registers and the distinction between supported interpretation and overreach. It is not ordinary positive/negative sentiment classification. It also does not claim to measure understanding of people in general: the corpus has one author and one language.

## How scoring works

For selected options `S` and correct options `C`:

```text
question score = |S ∩ C| / |S ∪ C|
run score      = 100 × mean(question scores over all 50 questions)
```

Partial credit is possible. Incorrect extra selections enlarge the denominator; selecting more options is not automatically better. Missing or unparseable responses receive zero rather than disappearing from the average. See the [methodology](docs/methodology.md) for parsing, refusal and reporting caveats.

## Results

The **2026-09-28 public snapshot** contains **41 evaluation configurations**, including separately reported effort tiers. These are configurations, not 41 unique model families. The default live board groups alternate efforts; the CSV preserves every published configuration so that grouping does not discard results.

- [Current set50 CSV](results/board_set50.csv): the same aggregate fields and values as the website's [download](https://brightonxu.com/works/llm-benchmark/results.csv).
- [Results schema and provenance](results/README.md): units, rounding, refusal flags and update procedure.
- [Aggregate observations](docs/findings.md): conclusions checkable from the published table, without item-level clues.
- [Historical set30 CSV](results/board_set30.csv): an earlier, different question set; not a current ranking or a directly comparable score scale.

The board mixes API, web and harness runs. Rig, effort and sampled runs matter: this is a model-plus-setup comparison, not a controlled claim that a particular harness causes an improvement. An observed min–max range is not a confidence interval.

## What you can reproduce

No third-party dependencies are needed for the illustrative scorer or its tests:

```sh
python3 tools/score_demo.py
python3 -m unittest discover -s tests -v
```

You can inspect the formula, run synthetic parsing/scoring cases and reuse the aggregate result table. **You cannot independently rerun the real exam from this repository.** The source text, questions, options, answer key and real model responses are intentionally unavailable. The demo is not the entire production evaluation harness; it does not reproduce whole-paper extraction, model calls or private adjudication.

## Disclosure and limitations

- GLM-5.3 assisted in drafting part of the question set. Author-model affinity in phrasing is a possible confound; labels remain author-verified.
- Protocols differ across rigs, and the public export does not contain every generation parameter or a per-attempt log. Do not infer unreported temperature, token budget or run dates.
- Sample counts are small; one historical configuration has only one run. Refusal is explicitly flagged and is not evidence of inability to interpret the text.
- Keeping the exam unpublished reduces public exposure. It is **not a guarantee** about a model provider's retention or training practices, nor proof of zero contamination.

See [privacy and reproducibility boundaries](docs/privacy.md). Author attribution is public; exam contents are not.

## Author and license

Created by [Brighton / Yi Xu](https://brightonxu.com/). Code in `tools/` and `tests/`: MIT. Documentation and public results: CC BY 4.0; see [LICENSE](LICENSE). The private corpus, questions and answer key are not licensed or distributed here.
