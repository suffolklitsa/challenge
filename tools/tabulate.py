#!/usr/bin/env python3
"""Total judges' scores and rank teams.

    python3 tools/tabulate.py 2027/rubrics/build-weights.toml scores.csv

scores.csv has one row per judge per team:
    team,judge,accuracy,issue_spotting,usefulness,judgment,presentation,penalty
Each category is scored 0 to 10. `penalty` is points taken off the weighted total (for example
for an invented citation); leave it blank for none.

A team's score is the average across its judges of (weighted sum of categories, scaled to 100,
minus penalties). Ties break on the categories listed in `tie_breaks`, in order, then stay tied.

The run stops, naming the team, judge and column, if the CSV is missing the team, judge or a
category column, if a judge has two rows for the same team, if a score is blank, not a number
or outside 0 to 10, or if a penalty is not a number or is negative.
"""
from __future__ import annotations

import csv
import sys
import tomllib
from collections import defaultdict
from pathlib import Path


def load_weights(path: Path) -> dict:
    with path.open("rb") as f:
        cfg = tomllib.load(f)
    weights = cfg["weights"]
    total = sum(weights.values())
    if abs(total - 100) > 1e-9:
        raise ValueError(f"weights must add to 100, got {total}")
    for t in cfg.get("tie_breaks", []):
        if t not in weights:
            raise ValueError(f"tie break {t!r} isn't a scored category")
    return cfg


def check_columns(fieldnames: list[str] | None, weights: dict) -> None:
    missing = [c for c in ["team", "judge", *weights] if c not in (fieldnames or [])]
    if missing:
        raise ValueError(f"the scores CSV is missing the column(s): {', '.join(missing)}")


def number(row: dict, col: str, *, blank: float | None = None) -> float:
    where = f"{row.get('team')} / {row.get('judge')}: {col}"
    value = row.get(col)
    if value is None or (isinstance(value, str) and not value.strip()):
        if blank is None:
            raise ValueError(f"{where} is blank")
        return blank
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"{where} is not a number: {value!r}") from None


def judge_total(row: dict, weights: dict) -> float:
    total = 0.0
    for cat, w in weights.items():
        score = number(row, cat)
        if not 0 <= score <= 10:
            raise ValueError(f"{row['team']} / {row['judge']}: {cat} must be 0 to 10, got {score}")
        total += score / 10 * w
    penalty = number(row, "penalty", blank=0.0)
    if penalty < 0:
        raise ValueError(f"{row['team']} / {row['judge']}: penalty can't be negative, got {penalty}")
    return total - penalty


def tabulate(rows: list[dict], cfg: dict) -> list[dict]:
    weights = cfg["weights"]
    by_team = defaultdict(list)
    seen = set()
    for r in rows:
        key = (r["team"].strip(), r["judge"].strip())
        if key in seen:
            raise ValueError(f"{key[0]} / {key[1]}: this judge has two rows for this team")
        seen.add(key)
        by_team[key[0]].append(r)
    results = []
    for team, judged in by_team.items():
        totals = [judge_total(r, weights) for r in judged]
        cats = {c: sum(number(r, c) for r in judged) / len(judged) for c in weights}
        results.append({"team": team, "judges": len(judged), "score": round(sum(totals) / len(totals), 2), **{f"avg_{c}": round(v, 2) for c, v in cats.items()}})
    keys = ["score"] + [f"avg_{c}" for c in cfg.get("tie_breaks", [])]
    results.sort(key=lambda r: tuple(-r[k] for k in keys))
    rank = 0
    prev = None
    for i, r in enumerate(results, 1):
        sig = tuple(r[k] for k in keys)
        if sig != prev:
            rank = i
        r["rank"], prev = rank, sig
    return results


def main(argv: list[str]) -> int:
    if len(argv) not in (2, 4):
        print(__doc__)
        return 2

    out_path = None
    if len(argv) == 4:
        if argv[2] != "--out":
            print(__doc__)
            return 2
        out_path = Path(argv[3])

    cfg = load_weights(Path(argv[0]))
    try:
        with open(argv[1], newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            check_columns(reader.fieldnames, cfg["weights"])
            results = tabulate(list(reader), cfg)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if out_path is not None:
        fieldnames = ["rank", "team", "score", "judges"]
        fieldnames += [f"avg_{cat}" for cat in cfg["weights"]]
        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    print(f"{'rank':>4}  {'score':>6}  {'judges':>6}  team")
    for r in results:
        print(f"{r['rank']:>4}  {r['score']:>6.2f}  {r['judges']:>6}  {r['team']}")
    few = [r["team"] for r in results if r["judges"] < cfg.get("judges_per_team", 2)]
    if few:
        print(f"\nfewer judges than expected: {', '.join(few)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
