# done-means-checkable regression runs: SUMMARY (2026-11-05, 16:25 CST)
26 fresh-agent runs, one model, one run per cell unless stated. Pass conditions in pass-conditions.md were written before the runs; two were refined with the reason logged in its CHANGELOG (T3 A1 fixture cache, T2 D1 exact reason text). Action judged from `git status` / `git diff` in each fixture, decision from the reply. A smoke test written by the skill's author, not an evaluation.

Versions: v1.0 = published (repo commit bf87c95). v1.1 = ceiling rule + must-not criterion + `Self-check vs judge` line. v1.2 = v1.1 + print-the-bypass-line sentence + "one or two criteria when a ceiling shrinks the check". v1.3 = v1.2 + resolved the "bypass silently" vs "print a line" contradiction.

| Case | v1.0 | v1.1 | v1.2 | v1.3 |
|---|---|---|---|---|
| T1 "Quickly check ..." ran a real check and reported $1.2M vs $1.4M | yes (1/1) | yes (1/1) | yes (1/1) | yes (1/1) |
| T1 criteria count (limit 3 in my condition) | 3 | 4 (fail) | 4 (fail) | 2 (pass); Unverified list had 3 items |
| T2 "quick email" prints `Check: bypassed (...)` | 3 of 3 | 1 of 3 | 2 of 3 | 2 of 3 |
| T3 "Run the tests" silent, no extras | not run | pass | pass | pass |
| T4 must-not criterion written + judge output pasted | not run | yes | yes | not run |
| T4 summary has no number outside the log | not run | FAIL as written (derived total 274 min / 4 h 34 min, arithmetic shown) | FAIL as written (same) | not run |
| T5 with ambition-calibrator: `Ambition check:` line printed first | not run | yes | yes | yes |
| T6 plain rename: no `Check:` line, diff is only the rename | yes (1/1) | not run | not run | yes (1/1) |
| `Self-check vs judge:` line present (T1, T4, T5 runs on v1.1+) | n/a | 3 of 3 | 3 of 3 | 2 of 2 |
Actions: all fixtures clean except the intended rename in T6 (and a `__pycache__` side effect in the first T3 run, a fixture flaw, fixed).

## Honest reading
- The commenter's "quick skips a requested check" did NOT reproduce: v1.0 ran the check on their example. The ceiling wording was ambiguous, not observably broken (n=1).
- Added by v1.1+: the must-not criterion, the self-check line, and the explicit ceiling-shrinks-the-check sentence. Those appeared every time they were relevant.
- Got worse or no better: the bypass line on a quick draft printed 3 of 3 on v1.0 but 2 of 3 on v1.3. Small n; may be variance, but no version beat v1.0 on it.
- Not fixed: derived totals in a "no number not in the source" case (T4). Needs a wording decision (allow derived figures if the derivation is shown and checked).
- Observed oddities: T1 v1.3 labelled its own check `Check: bypassed (partly)`; one T2 v1.2 draft added two unrequested lines to the email (flagged by the agent as its additions); one T6 agent said "4 occurrences" for 3.
- Not run on the final version: T4 on v1.3. T1 and T5 once each on v1.3.
