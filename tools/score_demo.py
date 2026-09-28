#!/usr/bin/env python3
"""Illustrative DiaryBench multi-select parsing and Jaccard scoring.

Adapted from legacy runner helpers, not a reproduction of the full live
evaluation pipeline. This demo contains only synthetic inputs. No private
corpus or real question text, answer keys, model responses, or per-question
scores are included.

Legacy parsing boundaries (preserved for illustration):
  - Try the raw text, then text with complete lowercase <think> blocks removed.
    In each pass, use the last regex-matched Final Answer payload, not the last
    successfully parsed answer. An earlier matching line is not retried in
    that pass; a valid raw candidate takes priority over the stripped pass.
  - Only a pass with no regex match scans backward for a bare line containing
    ASCII letters, whitespace, or commas. This is a legacy fallback, not the
    required output format: it can even interpret all-letter prose as options.
  - The Final Answer regex is case-insensitive and unanchored, accepts either
    colon, and lets whitespace cross line boundaries. An empty-looking prefix
    can capture the next line; an unmatched prefix does not suppress fallback.
  - A decorated/malformed matched payload suppresses bare-line fallback in
    that pass, but the think-stripped pass can still produce a valid candidate.
    Only when all candidates fail does parsing return None (eval_error).
  - Letters are ASCII, case-insensitive, and deduplicated. ASCII/Chinese commas
    and Unicode whitespace are allowed. The empty selection tokens are exactly
    `none`, `NONE`, `无`, and `∅`; the latter two require a matched payload since
    bare-line fallback admits only the strict letter/separator syntax.
  - Score per question = |S ∩ C| / |S ∪ C| (Jaccard); board = mean × 100.
    Two empty sets score 1. Missing/failed responses score 0 and count as errors;
    every key entry contributes to the denominator and per-question output.
  - A key must contain at least one question (individual correct sets may be
    empty). Excess responses are rejected. Option counts must be integers in
    1..26, and key indices must be integers in 1..n_options (booleans excluded).

Run as-is for a synthetic self-test on fake data: python3 tools/score_demo.py
"""
import re

THINK_RE = re.compile(r"<think>.*?</think>", re.S)
FINAL_RE = re.compile(r"Final\s*Answer\s*[:：]\s*([^\n]+)", re.I)
MS_STRICT_RE = re.compile(r"^[A-Za-z\s,，]+$")
MS_NONE_RE = re.compile(r"^\s*(无|none|NONE|∅)\s*$")


def answer_candidates(text: str | None) -> list[str]:
    """Return legacy candidates in raw-then-think-stripped priority order.

    Each pass uses its last regex match, or scans backward for strict bare
    syntax if no match exists. Candidates are deduplicated; historically, a
    repeated bare line is skipped and scanning continues to an earlier line.
    These are syntax candidates, not necessarily valid in-range selections.
    """
    out: list[str] = []
    for body in (text or "", THINK_RE.sub("", text or "")):
        tails = [m.group(1).strip() for m in FINAL_RE.finditer(body)]
        if tails:
            if tails[-1] not in out:
                out.append(tails[-1])
            continue  # a regex match suppresses bare-line fallback in this pass
        for line in reversed(body.splitlines()):
            s = line.strip()
            if s and MS_STRICT_RE.match(s) and s not in out:
                out.append(s)
                break
    return out


def _validate_n_options(n_options: int) -> None:
    if (
        isinstance(n_options, bool)
        or not isinstance(n_options, int)
        or not 1 <= n_options <= 26
    ):
        raise ValueError("n_options must be an integer from 1 to 26")


def parse_ms(text: str | None, n_options: int) -> set[int] | None:
    """Parse legacy candidates into 1-based indices, or None on parse failure.

    Empty-selection tokens return an empty set, distinct from a parse failure.
    Invalid option counts raise ValueError; out-of-range responses fail parsing.
    """
    _validate_n_options(n_options)
    for cand in answer_candidates(text):
        if MS_NONE_RE.match(cand):
            return set()
        if not MS_STRICT_RE.match(cand):
            continue
        letters = [c.upper() for c in cand if c.isalpha()]
        pos = {ord(l) - 64 for l in letters}
        if letters and pos <= set(range(1, n_options + 1)):
            return pos
    return None


def jac(selected: set[int], correct: set[int]) -> float:
    union = selected | correct
    return len(selected & correct) / len(union) if union else 1.0


def score_run(responses: list[str | None], key: list[set[int]], n_options: int = 4) -> dict:
    """Score an illustrative run, with one result per key entry.

    None or an omitted trailing response is missing: score zero and increment
    eval_error. Wrong but parseable selections are not errors. Reject an empty
    key, excess responses, invalid option counts, or out-of-range/non-integer
    key indices with ValueError. Individual correct sets may be empty.
    """
    _validate_n_options(n_options)
    if not key:
        raise ValueError("key must contain at least one question")
    if len(responses) > len(key):
        raise ValueError("responses must not outnumber key entries")
    for correct in key:
        for index in correct:
            if (
                isinstance(index, bool)
                or not isinstance(index, int)
                or not 1 <= index <= n_options
            ):
                raise ValueError("key indices must be integers from 1 to n_options")

    js, exact, eval_err = [], 0, 0
    for i, correct in enumerate(key):
        text = responses[i] if i < len(responses) else None
        if text is None:
            eval_err += 1
            js.append(0.0)
            continue
        sel = parse_ms(text, n_options=n_options)
        if sel is None:
            eval_err += 1
            js.append(0.0)
            continue
        js.append(jac(sel, correct))
        exact += sel == correct
    n = len(key)
    return {
        "board": round(100 * sum(js) / n, 2),
        "exact": f"{exact}/{n}",
        "eval_error": eval_err,
        "per_q": [round(v, 2) for v in js],
    }


if __name__ == "__main__":
    # Synthetic self-test — fake questions, fake key (1-based option indices), fake responses.
    key = [{1, 2}, {3}, {2, 4}, {1}]  # noqa: fake answer key
    responses = [
        "…per-option reasoning citing dates…\nFinal Answer: A B",        # exact → 1.0
        "<think>draft: A C</think>\n…reasoning…\nFinal Answer: B C",     # last line wins → {B,C} vs {C} = 0.5
        "All options seem defensible to some degree overall.",           # no valid answer line → eval_error
        "…reasoning…\nFinal Answer: **A**",                              # decorated → not rescued → eval_error
    ]
    r = score_run(responses, key)
    print("Synthetic run (4 fake questions):")
    print(f"  board      = {r['board']}   (expected 37.5 = mean of [1.0, 0.5, 0.0, 0.0])")
    print(f"  exact      = {r['exact']}      (expected 1/4)")
    print(f"  eval_error = {r['eval_error']}       (expected 2 — malformed lines score 0, separately counted)")
    print(f"  per_q      = {r['per_q']}")
    assert r["board"] == 37.5 and r["exact"] == "1/4" and r["eval_error"] == 2
    print("OK — parsing and scoring rules behave as documented.")
