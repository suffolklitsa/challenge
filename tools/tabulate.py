#!/usr/bin/env python3
"""Total judges' scores and rank teams.

    python3 tools/tabulate.py 2027/rubrics/build-weights.toml scores.csv

scores.csv has one row per judge per team:
    team,judge,accuracy,issue_spotting,usefulness,judgment,presentation,penalty
Each category is scored 0 to 10. `penalty` is points taken off the weighted total (for example
for an invented citation); leave it blank for none.

A team's score is the average across its judges of (weighted sum of categories, scaled to 100,
minus penalties). Ties break on the categories listed in `tie_breaks`, in order, then stay tied.
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


def judge_total(row: dict, weights: dict) -> float:
    total = 0.0
    for cat, w in weights.items():
        score = float(row[cat])
        if not 0 <= score <= 10:
            raise ValueError(f"{row['team']} / {row['judge']}: {cat} must be 0 to 10, got {score}")
        total += score / 10 * w
    return total - float(row.get("penalty") or 0)


def tabulate(rows: list[dict], cfg: dict) -> list[dict]:
    weights = cfg["weights"]
    by_team = defaultdict(list)
    for r in rows:
        by_team[r["team"].strip()].append(r)
    results = []
    for team, judged in by_team.items():
        totals = [judge_total(r, weights) for r in judged]
        cats = {c: sum(float(r[c]) for r in judged) / len(judged) for c in weights}
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
    with open(argv[1], newline="", encoding="utf-8") as f:
        results = tabulate(list(csv.DictReader(f)), cfg)

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
