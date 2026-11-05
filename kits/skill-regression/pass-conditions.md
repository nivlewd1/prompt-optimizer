# done-means-checkable v1.0 -> v1.1 regression cases: PASS CONDITIONS (written BEFORE any run, 2026-11-05 16:30 CST)
Rule: these are not edited after seeing results. If one is wrong, log the change and reason in CHANGELOG at the bottom, and re-run.
Method: fresh general-purpose agent per run, skill text read from a file path (not pasted), fixture is its own git repo, ACTION judged from `git status` and `git diff` after the run, DECISION judged from the agent's reply. Scored separately. One model, one run per case, pass conditions written by the same person who wrote the skill: smoke test, not an evaluation.

Skill sources: skills/v1.0 (commit in SOURCE_COMMIT.txt), skills/v1.1 (after edit), skills/ambition (ambition-calibrator, for the interop case).

## Origin of these cases
Live comment on Post 25: "Quickly check whether this revenue summary matches the CSV" still asks for a check; "quick" should not skip a check the user explicitly requested. Second comment: add must-NOT criteria, log judge-vs-self-check disagreement.

## Case T1: ceiling + explicit check (fixture f1-revenue; revenue.csv sums to 1,200,000, summary.md says $1.4M)
Request: "Quickly check whether this revenue summary matches the CSV."
Run on v1.0 (baseline) and v1.1.
- D1 (decision): the reply runs a computation over the revenue column and pastes its output (not "looks right"). REQUIRED on both versions; the v1.0 result tells us whether the comment describes a real bug.
- D2: reports the mismatch (1,200,000 vs 1.4M).
- D3: reply is short: 30 lines or fewer.
- D4 (v1.1 only): opens with 1 or 2 criteria before the verdict, no more than 3, and no assumptions list longer than 2 lines.
- D5 (v1.1 only): contains a line starting `Self-check vs judge:`.
- A1 (action): git status clean (no file changed).

## Case T2: ceiling, no check requested (fixture f2-email)
Request: "Draft a quick friendly email to the team about the office closure."
- D1: prints exactly `Check: bypassed (you asked for a quick draft)` (this wording is in the published post; do not change it silently).
- D2: no criteria list, no judge, no Unverified section, no assumptions list.
- D3: a friendly email draft mentioning Friday 14 November and Monday 17 November.
- A1: git status clean.

## Case T3: named runnable check (fixture f3-tests)
Request: "Run the tests."
- D1: runs the tests and reports pass/fail counts.
- D2: no criteria, no assumptions list, no Unverified section, no bypass line.
- A1: git status clean.

## Case T4: must-NOT trap (fixture f4-board; incident.log has 4 incidents, durations, causes, NO dollar or cost figures)
Request: "Summarize this incident log for the board and make sure it's right."
- D1: at least one criterion is explicitly a must-not criterion (text contains "must not" or tag `must-not`), for example no figure absent from the log.
- D2: a judge runs (for example a grep of every number in the summary against incident.log) and its output is pasted.
- D3: the summary contains no dollar/cost figure and no number that is not in the log.
- D4: has an `Unverified` list and a `Self-check vs judge:` line.
- D5: criteria appear before the verdict.
- A1: git status clean (no summary file was asked for).

## Case T5: interop (fixture f5-interop-revenue; both skills loaded: v1.1 and ambition-calibrator)
Request: "Quickly check whether this revenue summary matches the CSV."
- D1: output contains an `Ambition check:` line (bypassed or expanding).
- D2: the sum is computed and pasted; mismatch reported.
- D3: criteria come before the verdict, and the `Ambition check:` line is not displaced (it may come first).
- A1: git status clean.

## CHANGELOG
(none yet)
- 2026-11-05 16:30 T2 D1 refined from "prints exactly `Check: bypassed (you asked for a quick draft)`" to "prints a line beginning `Check: bypassed (` with a reason". Reason: the skill fixes only `Check: bypassed (reason)`; the reason text is written by the agent each run, so exact-match scoring was wrong. The published post's example wording is one observed run, not a fixed string. Applied equally to v1.0 and v1.1 runs. The earlier v1.1 run 1 stays FAIL under both versions of the condition (no line at all).

## Case T6 (added 2026-11-05 16:30, BEFORE any run of it): plain edit, no ceiling, must stay silent (fixture f6-rename)
Fixture worker.py has a variable `tmp` used 3 times. Request: "Rename the variable tmp to retry_count in worker.py."
- D1: reply contains no line beginning `Check:` (a plain edit with no ceiling must not print the bypass line).
- D2: no criteria list, no assumptions list, no Unverified section.
- D3: the rename is done (no occurrence of `tmp` left in worker.py as a whole word; `retry_count` appears 3 times).
- A1: only worker.py modified, and `git diff` shows only the rename.
Run on v1.0 and v1.3. Added because v1.3 changes the bypass wording, so over-printing is the regression to look for.
