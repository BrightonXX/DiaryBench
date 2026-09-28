"""Synthetic-only regression tests; never load the runner or evaluation data.

Run from the repository root:
    python3 -m unittest discover -s tests -p test_score_demo.py -v
"""
import unittest

from tools.score_demo import answer_candidates, jac, parse_ms, score_run


class AnswerCandidatesTests(unittest.TestCase):
    def test_empty_input(self):
        for text in (None, "", " \n\t\u3000"):
            with self.subTest(text=text):
                self.assertEqual(answer_candidates(text), [])

    def test_last_regex_match_not_last_parseable_answer(self):
        self.assertEqual(answer_candidates("Final Answer: A\nFinal Answer: B"), ["B"])
        self.assertEqual(
            answer_candidates("Final Answer: A\nFinal Answer: **B**\nC"),
            ["**B**"],
        )

    def test_raw_then_think_stripped_candidates(self):
        self.assertEqual(
            answer_candidates("Final Answer: A\n<think>\nFinal Answer: B\n</think>"),
            ["B", "A"],
        )
        self.assertEqual(
            answer_candidates("Final Answer: A\n<think>\nFinal Answer: **B**\n</think>"),
            ["**B**", "A"],
        )

    def test_stripped_pass_can_use_bare_fallback(self):
        self.assertEqual(
            answer_candidates("A\n<think>\nFinal Answer: **B**\n</think>"),
            ["**B**", "A"],
        )

    def test_bare_line_scan_skips_trailing_malformed_prose(self):
        self.assertEqual(answer_candidates("A B\nSynthetic explanation."), ["A B"])

    def test_bare_line_dedup_can_expose_an_earlier_candidate(self):
        self.assertEqual(answer_candidates("A\nB"), ["B", "A"])
        self.assertEqual(answer_candidates("A\nA"), ["A"])

    def test_empty_prefix_does_not_always_suppress_bare_fallback(self):
        self.assertEqual(answer_candidates("A\nFinal Answer:"), ["A"])
        self.assertEqual(answer_candidates("Final Answer:\nB"), ["B"])
        self.assertEqual(answer_candidates("Final Answer: A\nFinal Answer:"), ["A"])

    def test_prefix_is_unanchored_case_insensitive_and_cross_line(self):
        for text, expected in (
            ("Synthetic preface; fInAl AnSwEr: a", ["a"]),
            ("FinalAnswer：A", ["A"]),
            ("Final\nAnswer:\nA", ["A"]),
            ("Final Answer: A\r\n", ["A"]),
        ):
            with self.subTest(text=text):
                self.assertEqual(answer_candidates(text), expected)


class ParseMultiSelectTests(unittest.TestCase):
    def test_perfect_and_duplicate_letters(self):
        for text in ("Final Answer: A B", "Final Answer: ab", "Final Answer: a,A,b,B,a"):
            with self.subTest(text=text):
                self.assertEqual(parse_ms(text, 4), {1, 2})

    def test_unicode_colon_comma_and_whitespace(self):
        for text in (
            "Final Answer：a，b",
            "Final Answer:\u3000A\u00a0B\u2003",
            "Final Answer: A\tB",
            "Final Answer: A\u2028B",
        ):
            with self.subTest(text=text):
                self.assertEqual(parse_ms(text, 4), {1, 2})

    def test_empty_selection_tokens(self):
        for token in ("none", "NONE", "无", "∅"):
            with self.subTest(token=token):
                self.assertEqual(parse_ms(f"Final Answer: {token}", 4), set())

    def test_empty_selection_token_case_is_historical(self):
        for token in ("None", "NoNe", "NONE."):
            with self.subTest(token=token):
                self.assertIsNone(parse_ms(f"Final Answer: {token}", 4))
        # Mixed-case English is not an empty token; with enough options it is letters.
        self.assertEqual(parse_ms("Final Answer: None", 26), {5, 14, 15})
        self.assertEqual(parse_ms("Final Answer: none", 26), set())

    def test_bare_empty_tokens_depend_on_strict_syntax(self):
        for text in ("none", "NONE"):
            with self.subTest(text=text):
                self.assertEqual(parse_ms(text, 4), set())
        for text in ("无", "∅"):
            with self.subTest(text=text):
                self.assertIsNone(parse_ms(text, 4))

    def test_legacy_bare_line_and_all_letter_prose(self):
        self.assertEqual(parse_ms("Synthetic explanation.\nA B", 4), {1, 2})
        self.assertEqual(parse_ms("BAD", 4), {1, 2, 4})
        self.assertEqual(parse_ms("A\nZ", 4), {1})

    def test_empty_and_refusal_inputs(self):
        for text in (None, "", " \n\t", "I cannot answer this synthetic question.", "Final Answer:"):
            with self.subTest(text=text):
                self.assertIsNone(parse_ms(text, 4))

    def test_malformed_matched_payload_has_no_same_pass_rescue(self):
        for payload in ("**A**", "A.", "A、B", "(A)", "A/B", "A;B", "1", ",，", "Ａ", "é", "选A"):
            with self.subTest(payload=payload):
                self.assertIsNone(parse_ms(f"A\nFinal Answer: {payload}\nB", 4))

    def test_last_matched_answer_wins_even_when_it_fails(self):
        self.assertEqual(parse_ms("Final Answer: A\nFinal Answer: B", 4), {2})
        self.assertIsNone(parse_ms("Final Answer: A\nFinal Answer: **B**", 4))
        self.assertIsNone(parse_ms("Final Answer: A\nFinal Answer: Z", 4))
        self.assertEqual(parse_ms("Final Answer: A\nFinal Answer: none", 4), set())

    def test_raw_valid_answer_takes_priority_over_stripped_answer(self):
        self.assertEqual(
            parse_ms("Final Answer: A\n<think>\nFinal Answer: B\n</think>", 4),
            {2},
        )

    def test_think_stripped_retry(self):
        for draft in ("**B**", "Z"):
            with self.subTest(draft=draft):
                self.assertEqual(
                    parse_ms(f"Final Answer: A\n<think>\nFinal Answer: {draft}\n</think>", 4),
                    {1},
                )
        self.assertEqual(parse_ms("A\n<think>\nFinal Answer: **B**\n</think>", 4), {1})

    def test_think_stripping_requires_complete_lowercase_tags(self):
        for text in (
            "Final Answer: A\n<THINK>\nFinal Answer: **B**\n</THINK>",
            "Final Answer: A\n<think>\nFinal Answer: **B**",
        ):
            with self.subTest(text=text):
                self.assertIsNone(parse_ms(text, 4))
        self.assertEqual(
            parse_ms("<think>\nFinal Answer: **B**\n</think>\nA\n<think>\nFinal Answer: Z\n</think>", 4),
            {1},
        )

    def test_out_of_range_responses_fail_without_clamping(self):
        for text, count in (
            ("Final Answer: E", 4),
            ("Final Answer: A E", 4),
            ("Final Answer: Z", 4),
            ("Final Answer: B", 1),
        ):
            with self.subTest(text=text, count=count):
                self.assertIsNone(parse_ms(text, count))
        self.assertEqual(parse_ms("Final Answer: A", 1), {1})
        self.assertEqual(parse_ms("Final Answer: Z", 26), {26})

    def test_invalid_option_counts(self):
        for count in (0, -1, 27, True, False, 4.0, "4", None):
            with self.subTest(count=count):
                with self.assertRaisesRegex(ValueError, "n_options"):
                    parse_ms("Final Answer: A", count)


class JaccardTests(unittest.TestCase):
    def test_exact_partial_extras_disjoint_and_empty(self):
        cases = (
            ({1, 2}, {1, 2}, 1.0),
            ({1}, {1, 2}, 0.5),
            ({1, 2, 3}, {1, 2}, 2 / 3),
            ({2, 3}, {1, 2}, 1 / 3),
            ({3}, {1, 2}, 0.0),
            (set(), {1}, 0.0),
            ({1}, set(), 0.0),
            (set(), set(), 1.0),
        )
        for selected, correct, expected in cases:
            with self.subTest(selected=selected, correct=correct):
                self.assertAlmostEqual(jac(selected, correct), expected)
                self.assertAlmostEqual(jac(correct, selected), expected)


class ScoreRunTests(unittest.TestCase):
    def test_perfect_run(self):
        self.assertEqual(
            score_run(["Final Answer: A B", "Final Answer: C"], [{1, 2}, {3}]),
            {"board": 100.0, "exact": "2/2", "eval_error": 0, "per_q": [1.0, 1.0]},
        )

    def test_partial_extra_selected_options_and_wrong_answers(self):
        self.assertEqual(
            score_run(["Final Answer: A", "Final Answer: A B C", "Final Answer: D"], [{1, 2}, {1, 2}, {1}]),
            {"board": 38.89, "exact": "0/3", "eval_error": 0, "per_q": [0.5, 0.67, 0.0]},
        )

    def test_board_uses_unrounded_question_scores(self):
        self.assertEqual(
            score_run(["Final Answer: A", "Final Answer: B"], [{1, 2, 3}, {2}]),
            {"board": 66.67, "exact": "1/2", "eval_error": 0, "per_q": [0.33, 1.0]},
        )

    def test_none_is_valid_even_when_incorrect(self):
        self.assertEqual(
            score_run(["Final Answer: none", "Final Answer: ∅", "Final Answer: A"], [set(), {1}, set()]),
            {"board": 33.33, "exact": "1/3", "eval_error": 0, "per_q": [1.0, 0.0, 0.0]},
        )

    def test_refusal_malformed_empty_and_explicit_missing_are_errors(self):
        self.assertEqual(
            score_run(["I cannot answer this synthetic question.", "Final Answer: **A**", "", None], [{1}] * 4),
            {"board": 0.0, "exact": "0/4", "eval_error": 4, "per_q": [0.0] * 4},
        )

    def test_missing_trailing_responses_are_not_truncated(self):
        self.assertEqual(
            score_run(["Final Answer: A"], [{1}, {2}, {3}, {4}]),
            {"board": 25.0, "exact": "1/4", "eval_error": 3, "per_q": [1.0, 0.0, 0.0, 0.0]},
        )

    def test_explicit_missing_does_not_shift_later_responses(self):
        self.assertEqual(
            score_run([None, "Final Answer: B"], [{1}, {2}, {3}]),
            {"board": 33.33, "exact": "1/3", "eval_error": 2, "per_q": [0.0, 1.0, 0.0]},
        )

    def test_all_responses_omitted(self):
        self.assertEqual(
            score_run([], [{1}, {2}]),
            {"board": 0.0, "exact": "0/2", "eval_error": 2, "per_q": [0.0, 0.0]},
        )

    def test_short_runs_equal_explicit_missing_padding(self):
        key = [{1}, {2}, set(), {4}]
        responses = ["Final Answer: A", None, "Final Answer: none", "Final Answer: D"]
        for length in range(len(key) + 1):
            with self.subTest(length=length):
                short = responses[:length]
                result = score_run(short, key)
                self.assertEqual(result, score_run(short + [None] * (len(key) - length), key))
                self.assertEqual(len(result["per_q"]), len(key))

    def test_missing_or_failed_is_not_an_empty_selection(self):
        self.assertEqual(
            score_run([None, "Final Answer: **A**", "Final Answer: none"], [set()] * 4),
            {"board": 25.0, "exact": "1/4", "eval_error": 3, "per_q": [0.0, 0.0, 1.0, 0.0]},
        )

    def test_excess_responses_are_rejected_even_if_missing(self):
        for responses in (["Final Answer: A", "Final Answer: B"], ["Final Answer: A", None]):
            with self.subTest(responses=responses):
                with self.assertRaisesRegex(ValueError, "outnumber"):
                    score_run(responses, [{1}])

    def test_empty_key_is_rejected(self):
        for responses in ([], ["Final Answer: A"], [None]):
            with self.subTest(responses=responses):
                with self.assertRaisesRegex(ValueError, "at least one"):
                    score_run(responses, [])

    def test_invalid_option_counts_are_rejected_even_without_responses(self):
        for count in (0, -1, 27, True, False, 4.0, "4", None):
            with self.subTest(count=count):
                with self.assertRaisesRegex(ValueError, "n_options"):
                    score_run([], [{1}], count)

    def test_key_indices_are_validated_even_for_missing_responses(self):
        for index in (0, -1, 5, True, False, 1.0, "1", None):
            with self.subTest(index=index):
                with self.assertRaisesRegex(ValueError, "key indices"):
                    score_run([], [{1}, {index}])

    def test_valid_option_count_boundaries(self):
        for count, letter in ((1, "A"), (26, "Z")):
            with self.subTest(count=count):
                self.assertEqual(score_run([f"Final Answer: {letter}"], [{count}], count)["board"], 100.0)

    def test_out_of_range_response_is_an_error_not_invalid_configuration(self):
        self.assertEqual(
            score_run(["Final Answer: E"], [{1}]),
            {"board": 0.0, "exact": "0/1", "eval_error": 1, "per_q": [0.0]},
        )

    def test_inputs_are_not_mutated(self):
        responses = ["Final Answer: A A", None]
        key = [{1}, {2}, set()]
        original_responses = list(responses)
        original_key = [set(correct) for correct in key]
        score_run(responses, key)
        self.assertEqual(responses, original_responses)
        self.assertEqual(key, original_key)

    def test_original_synthetic_demo(self):
        self.assertEqual(
            score_run(
                [
                    "Final Answer: A B",
                    "<think>draft: A C</think>\nFinal Answer: B C",
                    "Synthetic refusal.",
                    "Final Answer: **A**",
                ],
                [{1, 2}, {3}, {2, 4}, {1}],
            ),
            {"board": 37.5, "exact": "1/4", "eval_error": 2, "per_q": [1.0, 0.5, 0.0, 0.0]},
        )


if __name__ == "__main__":
    unittest.main()
