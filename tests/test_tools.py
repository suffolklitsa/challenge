import tempfile
import unittest
from pathlib import Path

from tools import check_submission as cs, tabulate as tab

ROOT = Path(__file__).resolve().parents[1]
CFG = tab.load_weights(ROOT / "2027" / "rubrics" / "build-weights.toml")


def row(team, judge, a, i, u, j, p, pen=""):
    return {"team": team, "judge": judge, "accuracy": a, "issue_spotting": i, "usefulness": u, "judgment": j, "presentation": p, "penalty": pen}


class Tabulate(unittest.TestCase):
    def test_perfect_is_100(self):
        self.assertEqual(tab.tabulate([row("A", "j1", 10, 10, 10, 10, 10)], CFG)[0]["score"], 100.0)

    def test_average_across_judges_and_penalty(self):
        r = tab.tabulate([row("A", "j1", 10, 10, 10, 10, 10, 10), row("A", "j2", 5, 5, 5, 5, 5)], CFG)[0]
        self.assertEqual(r["score"], 70.0)

    def test_tie_breaks_on_accuracy(self):
        rows = [row("A", "j1", 8, 6, 6, 6, 6), row("B", "j1", 6, 8, 6, 6, 9)]
        res = tab.tabulate(rows, CFG)
        self.assertEqual(res[0]["score"], res[1]["score"])
        self.assertEqual(res[0]["team"], "A")
        self.assertEqual([r["rank"] for r in res], [1, 2])

    def test_full_tie_shares_rank(self):
        res = tab.tabulate([row("A", "j1", 7, 7, 7, 7, 7), row("B", "j1", 7, 7, 7, 7, 7)], CFG)
        self.assertEqual([r["rank"] for r in res], [1, 1])

    def test_out_of_range_rejected(self):
        with self.assertRaises(ValueError):
            tab.tabulate([row("A", "j1", 11, 7, 7, 7, 7)], CFG)


GOOD_README = "# Team Torch\n\n## Lane\nA\n\n## What it does\nx\n\n## How to use it\nx\n\n## Where this fails\nx\n"


class Submission(unittest.TestCase):
    def folder(self, files):
        d = Path(tempfile.mkdtemp())
        for name, text in files.items():
            (d / name).write_text(text)
        return d

    def test_good_submission(self):
        self.assertEqual(cs.problems(self.folder({"README.md": GOOD_README, "AI-USE.md": "## Tools\nNone\n"})), [])

    def test_missing_where_this_fails(self):
        p = cs.problems(self.folder({"README.md": GOOD_README.replace("## Where this fails\nx\n", ""), "AI-USE.md": "## Tools\nNone\n"}))
        self.assertTrue(any("Where this fails" in x for x in p))

    def test_missing_ai_disclosure(self):
        self.assertTrue(any("AI-USE.md" in x for x in cs.problems(self.folder({"README.md": GOOD_README}))))

    def test_secret_caught(self):
        p = cs.problems(self.folder({"README.md": GOOD_README, "AI-USE.md": "## Tools\nNone\n", "app.py": "KEY = 'sk-" + "a" * 30 + "'"}))
        self.assertTrue(any("secret" in x for x in p))


if __name__ == "__main__":
    unittest.main()
