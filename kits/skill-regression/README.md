# Skill Regression Kit

A method for checking that a change to a skill or prompt did what you meant without breaking something else, when the output has no unit test. This folder holds the method, the fixtures and pass conditions I used on my own `done-means-checkable` skill, and the scorecards from 26 fresh-agent runs.

One model, small numbers, and the pass conditions were written by the person who wrote the change. It shows whether rules fire, not whether outputs are better.

# Skill Regression Kit (v0.1)

Use this when you change a skill or prompt that has no unit tests, and you want to know whether the change did what you meant without breaking something else.

## 0. What you need
- The skill file in two versions (old, new), each at a file path.
- 4 to 8 cases. Include: one the change is meant to fix, one that must stay silent, one where a second skill is installed, one with a trap.
- A model or agent runner that can start a fresh session per case and read files.

## 1. Write the pass conditions first (pass-conditions.md)
For each case:
```
## Case T1: <name> (fixture f1-<name>)
Request (verbatim): "<exactly what the user types>"
Run on: old, new
- D1 (decision): <what the reply must contain or must not contain>
- D2: ...
- A1 (action): <what `git status` / `git diff` must show afterwards>
```
Rules:
- Do not edit a condition after you have seen any result.
- If a condition is wrong, add a line to a CHANGELOG at the bottom: date, which condition, what changed, why. Re-run the affected cells and say so.
- Write conditions about observable text and files, not "good" or "clear".

## 2. Build the fixtures
One folder per case. Each is its own git repo with one clean commit, plus a `.gitignore` for interpreter caches (`__pycache__/`, `.pytest_cache/`), so running a test does not look like a change.

## 3. Run each case on a fresh agent
Prompt template (fill the braces, add nothing else):
```
You are an AI coding assistant working for a user in the directory {FIXTURE_PATH} (a small git repo).
A skill is installed for you at {SKILL_PATH}. Read it fully first. Follow it for any request it applies to, exactly as an installed skill would apply.
Rules: work only inside the directory above. Do not run git commands that change anything. Do not create or edit files unless the skill or the request requires it.
The user's request, verbatim: "{REQUEST}"
Reply exactly as you would in a real session. At the very end add a section headed RUN LOG listing every command you ran and every file you wrote or edited (or "none").
```
Never put the expected outcome, the pass conditions or the other version in the prompt.

## 4. Score decision and action separately
- Decision: read the reply against D1, D2, ... Mark PASS or FAIL per condition.
- Action: run `git status --short` and `git diff` in the fixture. Compare to A1. A reply that says "I did not edit anything" does not count if the diff shows an edit.
- Reset the fixture (`git checkout -- . && git clean -fd`) before the next run on that fixture.

## 5. Baseline before you believe a complaint
Run the complaint's exact request on the OLD version first. If the old version already does the right thing, the gap is wording or documentation, not behaviour. Say that.

## 6. Repeat the cells that vary
Run any cell whose result differs between versions three times per version. Report counts ("old 3 of 3, new 2 of 3"). Do not average and do not call n=3 a rate.

## 7. Control
Run the same cases once with no skill installed. Whatever the skill adds is the difference.

## 8. Scorecard
| Case | old | new | notes |
|---|---|---|---|
| T1 | D1 pass, D2 pass, A1 pass | ... | ... |
Plus a "Not run" list and a "Conditions changed" list. Never leave a blank cell: write `not run`.

## 9. Known limits
One model. Conditions written by the same person who wrote the change. A handful of runs per cell. This tells you whether rules fire, not whether outputs are better.

## Layout of this folder

```
README.md              this file (the kit)
pass-conditions.md     the cases and conditions, written before any run, with a CHANGELOG of two logged corrections
fixtures/              plain files for each case (git repos cannot be nested, so they are created by the script)
init-fixtures.sh       creates ./work/<case> as fresh one-commit git repos; re-run to reset
skills/v1.0 .. v1.3    the four versions of done-means-checkable that were compared
results/               scorecards and the summary (SUMMARY.md first)
```
The `ambition-calibrator` skill used in case T5 is in [`../../skill/ambition-calibrator`](../../skill/ambition-calibrator/SKILL.md).

## Run it

1. `bash init-fixtures.sh`
2. For each case in `pass-conditions.md`, start a fresh agent with the prompt template in section 3, pointing `{SKILL_PATH}` at a version in `skills/` and `{FIXTURE_PATH}` at the matching folder in `work/`.
3. Score decision from the reply and action from `git status` and `git diff` in the fixture. Reset with `bash init-fixtures.sh` between runs on the same fixture.

## What is not here

Raw agent replies were not saved, so `results/` holds scorecards and the summary only. The control run (no skill) in section 7 was not part of these 26 runs. The original version was not run on cases T3, T4 and T5. Results are in [`results/SUMMARY.md`](results/SUMMARY.md).
