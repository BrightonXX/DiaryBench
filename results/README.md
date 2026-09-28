# Public result snapshots

## Current: `board_set50.csv`

Synchronized on **2026-09-28** from the website's public aggregate data, exported by the normal Hugo build at:

https://brightonxu.com/works/llm-benchmark/results.csv

This snapshot has **41 evaluation configurations**. It retains alternate effort tiers as separate rows; it is not a count of unique model families. The snapshot date is the synchronization date, **not** an invented run date.

| Column | Meaning |
|---|---|
| `model` | Public configuration identifier, including effort or rig suffix where present |
| `rig` | `api`, `web` or `harness` |
| `mean_jaccard_100` | Mean reported run score, on a 0–100 scale |
| `min_jaccard_100` | Lowest observed run score, on a 0–100 scale |
| `max_jaccard_100` | Highest observed run score, on a 0–100 scale |
| `runs` | Number of reported runs/attempts |
| `refused` | `true` when the configuration refused all reported attempts; otherwise `false` |

The score is the mean of 50 equally weighted question-level Jaccard overlaps, multiplied by 100. The CSV contains reported aggregates, not per-attempt logs or per-question records. With small sample counts, the mean and extrema can reveal individual run scores up to rounding; they do not recover item-level answers. Refused configurations require separate interpretation; a displayed zero is not demonstrated comprehension failure.

Mean values have two decimal places and observed extrema historically have one. The CSV uses two decimal places for consistent serialization; that does not add measurement precision. For the single-run qwen3.5-plus entry, a mean of 43.17 and extrema of 43.20 reflect historical rounding of the same run, not contradictory measurements. Preserve these source values.

The former `mean,min,max,shots` column names have been replaced by the explicit unit/count schema above. Consumers of the old snapshot need to update their column mapping. This release does not fabricate missing sampling settings, raw points or attempt dates.

## Historical: `board_set30.csv`

This file is an earlier 30-question aggregate snapshot, preserved unchanged. Its older schema is `model,mean,min,max,shots`. It does not report rig, and missing rig metadata must not be inferred. Legacy configuration identifiers are kept as recorded. Its scores and ranks should not be pooled with set50 or described as the current board.

## Updating

The website's `data/diarybench.json` is the source for its generated CSV; the public repository is a dated snapshot, not a second independent scoring pipeline. To refresh it:

1. Update and validate the already-public aggregate source on the website.
2. Build the website and copy only its generated `works/llm-benchmark/results.csv` to `board_set50.csv`.
3. Update the snapshot date, configuration count and any descriptive observations together.
4. Run `python3 -m unittest discover -s tests -v` and review the file list and release history before publication.

Never copy a private question set, run archive or response file to make this table “more reproducible.” Public documentation and result data retain the existing CC BY 4.0 license; private exam materials are not included in that license.
