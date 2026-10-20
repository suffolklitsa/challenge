
# Judge Ballots and Score Tabulation

This guide explains how to record judges' scores and generate team rankings for the Build Challenge.

## 1. Prepare the Ballot

Use `templates/judge-ballot.csv` as the ballot template.

Import it into Google Sheets or Excel. Keep these column names exactly as written:

```csv
team,judge,accuracy,issue_spotting,usefulness,judgment,presentation,penalty
```

Each row represents one judge's scores for one team.

## 2. Enter Scores

Complete the following fields:

| Field | Description |
|---|---|
| team | Team name |
| judge | Judge identifier |
| accuracy | Accuracy score, 0–10 |
| issue_spotting | Issue-spotting score, 0–10 |
| usefulness | Usefulness score, 0–10 |
| judgment | Judgment score, 0–10 |
| presentation | Presentation score, 0–10 |
| penalty | Points deducted from the weighted total; leave blank if none |

Use fictional data when testing. Never add personal information to example files.

## 3. Scoring Weights

The weights are defined in `2027/rubrics/build-weights.toml`.

| Category | Weight |
|---|---|
| Accuracy | 35% |
| Issue spotting | 20% |
| Usefulness | 20% |
| Judgment | 15% |
| Presentation | 10% |

Each score is converted from the 0–10 scale to its weighted contribution out of 100.

Penalties are deducted after weighting. The final team score is the average of its judges' totals.

The current configuration expects two judges per team. The tabulator warns when fewer scores are available.

## 4. Export Scores

After judges complete their ballots:

1. Collect all completed rows in one spreadsheet.
2. Keep exactly the eight required column headers.
3. Export or download the spreadsheet as CSV.
4. Save it as `scores.csv` in the repository root.
5. Ensure the CSV is encoded as UTF-8 without a byte-order mark (BOM).

Do not include extra title rows above the column headers.

## 5. Generate Rankings

Run this command from the repository root:

```bash
python tools/tabulate.py 2027/rubrics/build-weights.toml scores.csv
```

The script calculates team scores and prints the rankings.

Ties are resolved in this order:

1. Higher average accuracy
2. Higher average issue spotting
3. Higher average judgment

If teams remain tied, they share the same rank.

## 6. Example CSV

A ready-to-run example is available at `templates/example-scores.csv`.

```csv
team,judge,accuracy,issue_spotting,usefulness,judgment,presentation,penalty
Team Alpha,Judge 1,9,8,8,9,8,
Team Alpha,Judge 2,8,9,8,8,9,0
Team Beta,Judge 1,7,8,9,7,8,
Team Beta,Judge 2,8,7,8,8,8,2
```

Run the example:

```bash
python tools/tabulate.py 2027/rubrics/build-weights.toml templates/example-scores.csv
```

Expected rankings:

```text
rank   score  judges  team
   1   84.00       2  Team Alpha
   2   76.50       2  Team Beta
```

## 7. Check Before Finalizing

Make sure each team has the expected judge entries, every scoring category is between 0 and 10, and penalties are entered as point deductions when applicable.

Run the automated tests:

```bash
python -m unittest discover -s tests
```

Review the generated rankings before publishing the results.
