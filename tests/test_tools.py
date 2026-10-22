import contextlib
import csv
import io
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

    def test_duplicate_judge_row_rejected(self):
        rows = [row("Team A", "judge1", 7, 7, 7, 7, 7), row("Team A", "judge1", 8, 8, 8, 8, 8)]
        with self.assertRaisesRegex(ValueError, "Team A / judge1: this judge has two rows"):
            tab.tabulate(rows, CFG)

    def test_negative_penalty_rejected(self):
        with self.assertRaisesRegex(ValueError, "Team A / judge1: penalty can't be negative"):
            tab.tabulate([row("Team A", "judge1", 7, 7, 7, 7, 7, "-5")], CFG)

    def test_blank_score_names_team_judge_and_column(self):
        with self.assertRaisesRegex(ValueError, "^Team A / judge1: accuracy is blank$"):
            tab.tabulate([row("Team A", "judge1", "", 7, 7, 7, 7)], CFG)

    def test_non_numeric_score_names_team_judge_and_column(self):
        with self.assertRaisesRegex(ValueError, "Team A / judge1: usefulness is not a number: 'seven'"):
            tab.tabulate([row("Team A", "judge1", 7, 7, "seven", 7, 7)], CFG)

    def test_missing_column_is_named_before_rows_are_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            scores_path = Path(tmp) / "scores.csv"
            # The row's blank accuracy would fail too, but the missing column is reported first.
            scores_path.write_text("team,judge,accuracy,issue_spotting,usefulness,judgment,penalty\nTeam A,judge1,,7,7,7,\n", encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                code = tab.main([str(ROOT / "2027" / "rubrics" / "build-weights.toml"), str(scores_path)])
        self.assertEqual(code, 1)
        self.assertEqual(err.getvalue(), "error: the scores CSV is missing the column(s): presentation\n")
    
    def test_csv_output_can_be_read_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            scores_path = tmp / "scores.csv"
            output_path = tmp / "results.csv"

            with scores_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "team", "judge", "accuracy", "issue_spotting",
                        "usefulness", "judgment", "presentation", "penalty",
                    ],
                )
                writer.writeheader()
                writer.writerow(row("Team A", "judge1", 10, 10, 10, 10, 10))
                writer.writerow(row("Team B", "judge1", 5, 5, 5, 5, 5))

            self.assertEqual(
                tab.main([
                    str(ROOT / "2027" / "rubrics" / "build-weights.toml"),
                    str(scores_path),
                    "--out",
                    str(output_path),
                ]),
                0,
            )

            with output_path.open(newline="", encoding="utf-8") as f:
                results = list(csv.DictReader(f))

            self.assertEqual([r["team"] for r in results], ["Team A", "Team B"])
            self.assertEqual([r["rank"] for r in results], ["1", "2"])
            self.assertEqual(float(results[0]["score"]), 100.0)
            self.assertIn("avg_accuracy", results[0])

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

    def secret_files(self, files):
        p = cs.problems(self.folder({"README.md": GOOD_README, "AI-USE.md": "## Tools\nNone\n", **files}))
        return sorted(x.split(" ")[0] for x in p if "secret" in x)

    def test_private_key_files_are_scanned(self):
        key = "-----BEGIN " + "RSA PRIVATE KEY-----\nabc\n"
        self.assertEqual(self.secret_files({"key.pem": key, "server.key": key}), ["key.pem", "server.key"])

    def test_config_shell_react_and_extensionless_files_are_scanned(self):
        line = "KEY=sk-" + "a" * 30 + "\n"
        files = {"config.ini": line, "run.sh": line, "App.jsx": line, "notes": line}
        self.assertEqual(self.secret_files(files), ["App.jsx", "config.ini", "notes", "run.sh"])

    def test_images_pdfs_and_word_files_are_not_scanned(self):
        line = "KEY=sk-" + "a" * 30 + "\n"
        self.assertEqual(self.secret_files({"photo.png": line, "brief.pdf": line, "memo.docx": line}), [])

    def test_files_over_25_mb_are_not_scanned(self):
        d = self.folder({"README.md": GOOD_README, "AI-USE.md": "## Tools\nNone\n"})
        with (d / "big.txt").open("w") as f:
            f.write("KEY=sk-" + "a" * 30 + "\n")
            f.truncate(cs.MAX_BYTES + 1)
        self.assertEqual(cs.problems(d), ["big.txt is over 25 MB"])


if __name__ == "__main__":
    unittest.main()
