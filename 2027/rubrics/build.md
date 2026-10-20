# Build scoring (draft)

Two judges score each submission. Judges calibrate together on a sample before judging starts.

| Category | Weight | What judges look for |
|---|---|---|
| Accuracy | 35 | Law and facts are correct and come from the case file. **An invented or misused citation is a heavy penalty.** |
| Issue spotting | 20 | The problems a careful lawyer in your role would see |
| Usefulness | 20 | Whether the person in your lane would actually use it |
| Judgment and risk | 15 | Limits, risks, and when to hand off to a person |
| Presentation | 10 | Clear, organized, easy to follow |

Each category is scored 0 to 10 and weighted to a total out of 100; penalties come off that total. A team's score is the average of its judges' totals. Ties break on accuracy, then issue spotting, then judgment. The exact calculation is [`tools/tabulate.py`](../../tools/tabulate.py), with weights in [`build-weights.toml`](build-weights.toml).

The moot uses a standard moot court rubric plus accuracy in citing the record; it will be published with the rules.
