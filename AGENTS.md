# AGENTS.md

Instructions for AI coding agents working in this repo, and for the people using them. Read README.md and CONTRIBUTING.md too.

## What this repo is

The public side of LITSA's annual challenge: overview, rules, lanes, rubrics, starter kits, and tools (`tools/tabulate.py`, `tools/check_submission.py`). Standard-library Python.

## Commands

```
python3 -m unittest discover -s tests
python3 tools/check_submission.py path/to/entry
python3 tools/tabulate.py 2027/rubrics/build-weights.toml scores.csv
```

## Rules for this repo

- **Branches:** work from `staging` and open pull requests against it. Never target `main`; maintainers promote `staging` to `main`.
- **Nothing from the private case file.** No case facts, answer-key content or hidden tests here. Released materials arrive only through the private repo's release script.
- **Rules and rubrics must match the tools.** If you change scoring or submission requirements, change the tool, its tests and the docs in one pull request.
- **Write for a first-year.** Plain words, short sections; lanes A and C stay doable without code.
- **Competitors' questions** about the case aren't answered in code comments or docs; they go through official channels.

## Rules for every LITSA repo

- **No secrets.** Never write API keys, tokens or passwords into a file, a commit, an issue or a test. Keys come from environment variables. If you find one committed, stop and tell a maintainer.
- **No personal data.** No real names, emails, student records, sign-in sheets or mailing lists in code, tests, fixtures, screenshots or commit messages. Use made-up examples (`jane.doe@example.edu`).
- **No invented law.** Anything stating a rule, statute, case or requirement must come from a source you can link. Never make up a citation. If you can't find the source, say so in the pull request instead of guessing.
- **Small changes.** One issue per pull request. Don't reformat or rename things the issue didn't ask about.
- **Run the checks** listed above before saying the work is done, and report what they printed. If one fails, fix it or say plainly that it fails.
- **Plain writing.** Docs and messages use short, ordinary sentences a first-year law student would follow.
- **Disclose AI use.** The person opening the pull request notes which AI tools helped, in the description. They own every line either way.
