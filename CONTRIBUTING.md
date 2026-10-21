# Contributing to challenge

The org-wide guide is at [suffolklitsa/.github](https://github.com/suffolklitsa/.github/blob/main/CONTRIBUTING.md).

## Picking an issue

Issues labeled [`needs challenge context`](https://github.com/suffolklitsa/challenge/labels/needs%20challenge%20context) depend on the case file, the Commonwealth of Tremont, the rules, the rubrics or judging, so they're for LITSA members working on the challenge. If you're contributing from outside LITSA, pick a tooling or docs issue instead, such as work on `tools/check_submission.py`, `tools/tabulate.py`, the tests or the README.

## If you're competing

You're welcome to open issues about unclear rules, broken tools or problems with released materials. Don't open issues or pull requests that discuss how to argue the case or build an entry; those questions go through official channels so everyone gets the same answer.

## If you're organizing

- Rules, lanes and rubrics change through pull requests, reviewed by a second organizer and approved by the LITSA president.
- Nothing from the private case-file repo goes here except through its release script on the scheduled date.
- Keep everything understandable to a first-year: plain words, short sections.
- Tools use only the Python standard library. Run `python3 -m unittest discover -s tests` before opening a pull request.
