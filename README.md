# challenge

LITSA's annual challenge at Suffolk Law: a moot court competition and a build competition on the same case file, set in the fictional Commonwealth of Tremont. Open to law students at Suffolk and at other schools.

**Status:** planning the 2027 edition. Everything in [`2027/`](2027/) is a draft and can change until the rules are final. Watch this repo (the **Watch** button) or suffolklitsa.org for announcements.

## The 2027 challenge at a glance

- **One case, two competitions.** A fictional health system's AI agents go wrong, and patients sue. Moot teams argue it from an evidentiary hearing through an appeal. Build teams work on the fallout.
- **Moot court:** virtual trial-court and appellate rounds in March, final in person at Suffolk Law.
- **Build challenge:** one day in person at Suffolk Law in early April, six lanes, with a lane anyone can do without coding.
- **Closed universe:** Tremont's statutes and cases are supplied, so every team works from the same law.
- **AI use is allowed and disclosed.** Every team lists its tools and shares its transcripts.

Details, dates and lanes: [2027/README.md](2027/README.md).

## What's in this repo

| Path | What's there |
|---|---|
| `2027/` | This year's overview, rules, lanes, rubrics, and (on their release dates) the case materials |
| `starter-kits/` | Templates to start a build entry, one per lane |
| `tools/check_submission.py` | Run it on your folder before you submit: `python3 tools/check_submission.py my-entry/` |
| `tools/tabulate.py` | How scores are totaled and ties broken, published so everyone can see exactly how it works |

## When materials appear here

| Material | Date (planned) |
|---|---|
| Rules, lane descriptions, rubrics, starter kits | Before registration opens in January |
| Moot record and the Tremont statute appendix | February 1 |
| Late log excerpt | The morning of the first trial-court rounds |
| Build packet | The day of the build challenge |

## Questions

Open an issue labeled `question`, or email sam.darkwa@su.suffolk.edu. Please don't ask organizers or judges about the case itself outside official channels; answers go to everyone through this repo.

## Branches

Pull requests go to `staging`, the default branch. `main` is the released version: maintainers promote `staging` to `main` with a pull request when a batch of changes is ready. Both branches are protected and need a review and passing checks.

## Contributing

This repo is for organizers and for tools anyone can check. Competitors are welcome to report problems with the tools or unclear rules as issues. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Code is MIT ([LICENSE](LICENSE)). Rules, lane descriptions and case materials are CC BY 4.0 once published ([LICENSE-docs.md](LICENSE-docs.md)). Teams own their builds; the rules will grant LITSA a license to showcase them.
