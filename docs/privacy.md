# Privacy and reproducibility boundaries

The boundary protects **exam contents**, not the identity of the creator. Brighton / Yi Xu, the website, the public repository and the benchmark's purpose can be attributed normally.

## What is released

- General task design, evaluation rigs, scoring definition and limitations.
- Whole-exam aggregate scores, observed min–max, run counts and refusal flags for public configurations.
- An illustrative scoring implementation and tests with fully synthetic inputs.
- An older aggregate-only set30 snapshot, explicitly separated from the current set50 results.

The website also offers broad segment aggregates. This repository does not add item identifiers or mappings that would make those groups easier to reconstruct.

## What is not released

- Diary text, quotations, excerpts, paraphrases or rewritten “anonymized” passages.
- Real question stems, options, answer keys, authoring drafts or prompts containing them.
- Actual model responses, reasoning, citations to diary passages, or per-question selected-option/correctness vectors.
- Private logs, archives, credentials, local paths to private inputs or hashes of private keys and small answer sets.

Replacing names in a real item is **not** sufficient: the item would still be exposed. Public examples are invented independently and labelled synthetic; they teach the interface or arithmetic without resembling a released exam item.

## What openness means here

Anyone can audit the public scoring formula, run the toy tests and reuse the reported table. They cannot independently run the private exam or verify its labels. No per-attempt score log is published, but aggregates can reveal individual run scores up to rounding: one run is its mean, two runs are the min/max, and three can be recovered from the mean and extrema. This does not reveal item-level answer selections or correctness. The release is not marketed as full exam reproducibility.

The author supplies diary and exam material to models during evaluation. Keeping it off the public web reduces public exposure, but does not prove that every provider retains nothing or excludes the material from training. The full answer key is not part of the released evaluation inputs or public artifacts. Author-verified ground truth is also a design choice with a single-author limitation, not a population-wide measure of emotional understanding.

## Release hygiene

Before publishing, review both the candidate files **and the Git history being uploaded**. Private source repositories and run archives must not be merged into this repository. `.gitignore` is an accident guard, not a security boundary, and does not remove files already tracked or historical blobs.

Only reviewed release snapshots may be published. Earlier exploratory material can contain item-group diagnostics even without literal question text; it must not be carried into the public history. Use a clean snapshot for an empty remote when necessary, retaining local development history separately. Do not silently force-push or assume deleting a current file removes its earlier contents.

No literal-match scan can guarantee absence of semantic clues. The release therefore uses a small file allowlist and a manual review of findings and examples, in addition to checks for raw material and credentials. New data exports must use explicit aggregate columns, never a wholesale copy of a private results directory.
