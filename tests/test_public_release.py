"""Validate the public aggregate snapshot; no private evaluation inputs."""
import csv
from decimal import Decimal
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIELDS = [
    "model", "rig", "mean_jaccard_100", "min_jaccard_100",
    "max_jaccard_100", "runs", "refused",
]


class PublicReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "results/board_set50.csv").open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            cls.fields = reader.fieldnames
            cls.rows = list(reader)

    def test_only_declared_aggregate_fields(self):
        self.assertEqual(self.fields, FIELDS)
        self.assertTrue(self.rows)
        for row in self.rows:
            self.assertEqual(set(row), set(FIELDS))
            self.assertTrue(all(value is not None and value != "" for value in row.values()))

    def test_configurations_are_unique_and_typed(self):
        seen = set()
        for row in self.rows:
            identity = row["model"], row["rig"]
            self.assertNotIn(identity, seen)
            seen.add(identity)
            self.assertRegex(row["model"], r"^[a-z0-9][a-z0-9./-]*$")
            self.assertIn(row["rig"], {"api", "web", "harness"})
            self.assertRegex(row["runs"], r"^[1-9][0-9]*$")
            self.assertIn(row["refused"], {"true", "false"})

    def test_score_units_range_and_historical_rounding(self):
        for row in self.rows:
            values = [Decimal(row[field]) for field in FIELDS[2:5]]
            for value in values:
                self.assertTrue(value.is_finite())
                self.assertLessEqual(Decimal(0), value)
                self.assertLessEqual(value, Decimal(100))
            mean, low, high = values
            self.assertLessEqual(low, high)
            # Extrema historically have one decimal, means have two.
            self.assertLessEqual(low - Decimal("0.05"), mean)
            self.assertLessEqual(mean, high + Decimal("0.05"))

    def test_refusal_flag_has_explicit_zero_scores(self):
        for row in self.rows:
            if row["refused"] == "true":
                self.assertTrue(all(Decimal(row[field]) == 0 for field in FIELDS[2:5]))
        sonnet = next(row for row in self.rows if row["model"] == "claude-sonnet-5")
        self.assertEqual(sonnet["refused"], "true")

    def test_snapshot_count_and_dates_match_docs(self):
        documents = [(ROOT / name).read_text(encoding="utf-8") for name in
                     ["README.md", "results/README.md", "docs/findings.md"]]
        dates = [set(re.findall(r"2026-\d{2}-\d{2}", doc)) for doc in documents]
        self.assertEqual(dates[0], dates[1])
        self.assertEqual(dates[1], dates[2])
        for doc in documents[:2]:
            count = re.search(r"\*\*(\d+) evaluation configurations\*\*", doc)
            self.assertIsNotNone(count)
            self.assertEqual(int(count.group(1)), len(self.rows))

    def test_descriptive_top_five_are_current(self):
        top = sorted(self.rows, key=lambda row: Decimal(row["mean_jaccard_100"]), reverse=True)[:5]
        findings = (ROOT / "docs/findings.md").read_text(encoding="utf-8")
        for row in top:
            self.assertIn(f"({row['mean_jaccard_100']})", findings)
            self.assertEqual(row["rig"], "harness")

    def test_historical_snapshot_is_separate(self):
        with (ROOT / "results/board_set30.csv").open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            self.assertEqual(reader.fieldnames, ["model", "mean", "min", "max", "shots"])
            self.assertTrue(list(reader))

    def test_local_documentation_links_resolve(self):
        docs = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md")), ROOT / "results/README.md"]
        for doc in docs:
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", doc.read_text(encoding="utf-8")):
                if target.startswith(("https://", "http://", "#")):
                    continue
                path = (doc.parent / target.split("#", 1)[0]).resolve()
                self.assertTrue(path.is_relative_to(ROOT))
                self.assertTrue(path.is_file(), f"Broken local link in {doc.name}: {target}")


if __name__ == "__main__":
    unittest.main()
