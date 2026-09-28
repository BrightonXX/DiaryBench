# Aggregate observations

These observations use only the [public set50 CSV](../results/board_set50.csv), synchronized on **2026-09-28**. They do not disclose which items are difficult, which options are correct or what any real model answered.

## Current leading configurations

The five highest reported means are GPT-6 Astra (64.83), GPT-6 Sol Extra High (63.06), Grok 4.6 (55.10), GLM 5.3 (54.28) and Claude Opus 5 (53.83). All five are harness configurations in this snapshot.

These are descriptive table values, not proof of a harness effect or statistically significant pairwise rankings. The rigs and underlying model identities are not controlled variables across the whole board. The older August “final board” was a historical snapshot, not a permanent ranking.

## Mean and observed range answer different questions

The mean summarizes available runs; the observed range describes how far those reported runs varied. For example, Omen Alpha has a reported range of 43.2–51.5 over three runs, while the legacy GPT-5.6 Sol Ultra configuration spans 50.3–50.8 over three. A narrow observed range does not guarantee the same result on future runs, and it does not show item-level agreement.

The single-run qwen3.5-plus entry has no evidence of between-run stability. Its rounded minimum and maximum should not be read as a measured uncertainty interval.

## Effort tiers should stay visible

The table includes multiple effort configurations of GPT-5.6 Terra and Sol. Their reported means differ, so collapsing them into one row should not discard the underlying configurations. The live board's grouped display and the ungrouped public CSV serve different purposes.

These small samples do not establish a universal optimal effort tier. Differences could depend on sampling, model configuration and the particular private exam.

## Refusal is a separate outcome

Claude Sonnet 5 is marked as refusing all three reported attempts. Its zero is a board representation of that outcome. It is not evidence that a completed Sonnet 5 answer would have zero Jaccard overlap.

## Claims this release cannot support

The aggregate CSV cannot reveal why an individual answer failed, validate a model's reasoning, estimate a causal rig benefit or reproduce the real exam. Those claims would require evidence intentionally absent from the public release. No per-item failure taxonomy, correct-answer hints or real reasoning excerpts are published to fill that gap.
