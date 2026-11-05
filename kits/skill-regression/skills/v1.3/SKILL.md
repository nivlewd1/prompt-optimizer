---
name: "done-means-checkable"
description: "Defines what 'right' means before work starts and checks the result with a judge other than the model: written acceptance criteria, an assumptions list, a judge ladder for work with no tests, and a separate record of what was decided versus what was done. Use when the user hands over work with no obvious test, asks how to know a result is right, or wants an output verified. Not for tasks that already have a passing test suite, and not for single-step edits."
---

# Done Means Checkable

When a user hands an AI assistant work that has no built-in test (an analysis, a summary, a plan, a rewrite, a design), the assistant first writes down what "right" would look like in a form something other than the assistant can check, and only then does the work. After the work it runs the best available outside judge and reports what was verified and what was not. A second, separate record keeps the assistant's decision (what it chose to do) apart from its action (what it actually did), so a careful gate cannot be quietly walked past.

This skill pairs with `ambition-calibrator`, which decides how deep a task should go. This one decides how you will know the result is right. It works on its own.

## Instructions

### Stage 1: Intake and Bypass
Capture the request and decide whether this procedure is wanted at all.

- **Capture the request verbatim.** Keep the user's wording as the reference for every later check. Do not paraphrase it into notes.
- **Bypass.** Do the task as asked, with no extra section, when any of these hold: the request is a single-step edit, lookup, rename, formatting change, or a question with a known answer; a runnable check already exists and the user named it ("run the tests", "make the linter pass"); or the user set a ceiling ("just", "only", "quick", "don't touch anything else") and asked for no check. A plain rename should not produce a paragraph about verification. A bypass is silent, with one exception: when a ceiling the user set is what caused it, print the single line `Check: bypassed (reason)` before the work (see "Say something only when it helps" below).
- **A ceiling shrinks the check; it does not cancel one the user asked for.** "Quick", "just" and "only" limit length, effort and scope. If the request also asks for a check or for verification ("quickly check whether this summary matches the CSV"), run the smallest relevant check: one or two criteria, one judge, a short report. Keep the criteria-first order and keep the `Unverified` line. If no check was asked and no trigger below fires, bypass as above, and when the ceiling is what caused the bypass, print `Check: bypassed (reason)` as the next bullet says.
- **Say something only when it helps.** Write `Check: bypassed (reason)` only when the bypass was caused by a ceiling the user set, or when the work was handed to another skill. Otherwise say nothing. This silence covers this skill's own note only: it never suppresses a line another installed skill requires, such as `ambition-calibrator`'s `Ambition check:` line.
- **Run the procedure only on one of these triggers:** (a) the user asks whether a result is right, or asks for it to be verified or checked; (b) the user hands over an analysis, report, summary, plan, audit, or design that a person will act on, and no test or named check exists for it; or (c) a result you produced failed a check and you are about to claim it passes. Anything else is bypassed. If a request meets a trigger and a bypass condition, an explicit request to verify wins; a deliverable-type noun alone does not.
- **Working with `ambition-calibrator`.** If that skill is installed and expanded the task, do not start a second pass. Take the `Outside judge` line of its rewrite as your first criterion, add the criteria and assumptions below that it does not cover, and fold the result into its handoff instead of writing a second one. If it bypassed the task and printed its `Ambition check: bypassed (reason)` line, keep that line; this skill still runs when one of its own triggers above fires (a plain "is this right?" is a bypass for `ambition-calibrator` but trigger (a) here); it bypasses only when none of its triggers fire.
- **Environment check.** Note which checks are possible here: can you run commands, read the source data, and run a query or test? If a check needs something missing, tag that criterion `not run` with what it needs, and continue with the rest. Stop and ask only when the missing access is the whole point of the check.
- **Scope guard.** This skill adds checks, not deliverables. It must not widen the task, add audiences, or touch systems outside the request. A check that needs a new script, dataset, or scheduled job is listed as a follow-up and gated on confirmation.

### Stage 2: Acceptance Criteria Before the Work
Write what "right" means before producing anything.

- **Write three to seven criteria (one or two when a ceiling has shrunk the check, see Stage 1).** Each is a statement a stranger could mark pass or fail without asking you what you meant. "Covers the main risks" is not checkable. "Names at least the three risks in the attached incident log, each with the log line that shows it" is.
- **Include at least one must-not criterion.** A statement about what must be absent: a number or claim with no source in the materials, a recommendation that contradicts a constraint in the brief, a step the user ruled out. Models check for what is present far better than for what is extra, so write the absences down. Tag it like the others; where you can, tag it `run` (search the output for every number, name or claim and match each to its source).
- **Derive them from the user's own words and materials first.** The user's stated goal, constraints, and source files are the acceptance bar. If the user gave no bar, propose criteria and label them `proposed`; do not present them as the user's.
- **Define the vague words.** If the request uses a word like "shallow", "good", "thorough", or "clear", turn it into a criterion before testing against it. If you cannot, ask one question instead of guessing.
- **Tag each criterion with how it will be checked:** `run` (a command or query returns a result), `held-out` (a case the work was not fitted on), `review` (a fresh-context reviewer), or `user` (the user answers specific questions). A criterion that fits none of these is written as `unverifiable: <why>` and carried into the handoff, not dropped.
- **Lock the criteria.** After the work starts, changing a criterion is allowed only if the change and the reason are logged. Never loosen a criterion because the result failed it.

### Stage 3: Assumptions List
Name what the work is leaning on.

- **List the assumptions the result depends on.** Facts about the data, the environment, the audience, or the user's intent that you did not verify. Keep each to one line.
- **Mark each one:** `tested` (with how), `untested`, or `cannot test`.
- **Stop on a load-bearing gap.** If an assumption the whole result rests on is `cannot test`, ask the user before continuing. If it is minor, continue and carry it into the handoff.
- **Try to break one cheap assumption.** Pick the assumption that is cheapest to test and most damaging if wrong, and test it before building on it.

### Stage 4: Match a Judge to Each Criterion
Use the standard judge order: an executable check, then a held-out case, then a fresh-context reviewer, then the user with exact questions. Run it, paste the output unedited, never edit the judge or the data to make it pass, label a self-graded result `UNVERIFIED: no external judge available`, and stop after three failed rounds. `ambition-calibrator` Stage 6 spells these rules out; if it is not installed, those are the rules. What this stage adds is the pairing with Stage 2:

- **Pick the judge per criterion, before the work.** Each criterion gets the highest rung that can check it. Write the check now if it costs a few lines (a search for every cited figure, a query that reconciles totals); a judge chosen after seeing the result tends to fit the result.
- **A held-out case needs a real second case.** Do the work on case A, then run it on case B that was not used to build it, and compare against what you expected before running. Do not call a rerun on the same input held-out.
- **A fresh-context reviewer sees only the output and the criteria,** not your reasoning, and gets the must-not list as an explicit "must not contain" list. Spawning another agent costs time and tokens; do it only if the user agrees after seeing the cost, otherwise do an isolated pass inline and say it is weaker.
- **Ask the user specific questions,** tied to a criterion. "Does this look right?" is not a question.
- **Cost gate.** Before running a check that takes real time, money, new access, or an install, or that reads large or sensitive data, state what it costs and ask. A check that only reads the working files and runs in seconds needs no confirmation.

### Stage 5: Decision Versus Action
Keep what you chose separate from what you did. This matters most when a gate exists: a confirmation step, a scope limit, an approval the user asked for.

- **Record two fields for any run that had a gate.**
  - **Decision:** what you concluded and why (for example, "this request widens scope, so wait for approval").
  - **Action:** what you actually did, in order (for example, "read three files; wrote no output; asked for approval").
- **Compare them before reporting.** If the decision said wait and the action wrote anything outside the working files, flag the mismatch at the top of the handoff. A carefully written gate that is acted past is a failure, even if the output is good.
- **When the user is evaluating a skill or prompt,** offer a small table to fill from real runs, one row per test input: `input | expected decision | expected action | observed decision | observed action`. Score the two decisions separately. Report counts exactly as observed, and say how many inputs were run. A handful of inputs is a smoke test, not an evaluation.

### Stage 6: Handoff
End with a short report the user can audit.

- **Lead the reply with the criteria.** Open with the acceptance criteria (after any status line another installed skill requires, such as `Ambition check:`) and how each is checked, then the verdict or deliverable, so the reader sees the bar before the result. Do not open with the answer and attach the criteria afterwards.
- **Report:** the acceptance criteria and how each was checked; the judge command and its unedited result; a list headed `Unverified`; the assumptions marked `untested` or `cannot test`; any criterion marked `unverifiable`; and, if a gate existed, the decision and action records.
- **Record whether the judge agreed with you.** If you formed a view of the result before the judge ran, write one line: `Self-check vs judge: agreed`, `disagreed (what differed)`, or `no self-check`. Disagreement is the useful signal, and a judge that never disagrees across runs may mean the criteria are too easy. This is a per-run line; keep a running tally only if the user asks for one.
- **Say what remains manual.** Name any step that needs access, a schedule, or a person that was not granted, instead of implying it is handled.
- **Offer, do not build.** If a recurring check would help, describe it and ask. Do not create anything scheduled without consent.

## Success Criteria
The procedure is complete when all of the following can be confirmed from the transcript:
- Either nothing was added because a bypass applied, or acceptance criteria were written before the work and each is tagged with how it is checked.
- No criterion was loosened after seeing a result, unless the change and reason are logged.
- An outside judge ran and its unedited output is shown, or the result is explicitly labeled `UNVERIFIED: no external judge available`.
- Assumptions that the result depends on are listed with their status.
- If a gate existed, the decision and action records are separate and any mismatch is flagged.

## Failure and Escalation
- If the user's goal is unclear and the criteria cannot be written, ask one question rather than inventing a bar.
- If the only way to check the result needs access or data you do not have, say what is missing and ask whether to provide it or accept a reduced check.
- If the judge fails three times, stop and hand the failing output to the user.
- If the user declines the checks, do the task as asked and record that no check was run.

## Prohibitions
- Never grade your own work and call it verified.
- Never edit the judge, the criteria, or the data to make a check pass.
- Never claim a deterministic result that did not run.
- Never add deliverables, scripts, or scheduled jobs the user did not ask for.
- Never report a gate as respected when the action record shows work past it.
- Never present a handful of test inputs as an evaluation.

## Worked Examples

### Example 1: Silent bypass
- **Input:** "Run the tests."
- **Action:** Run them and report the result. No criteria, no assumptions list, no note about this skill.
- **Do not do:** Do not turn a named, runnable check into a verification plan.

### Example 2: Work with no test
- **Input:** "Summarize these three vendor contracts for the board, and make sure it's right."
- **Action:** Write criteria first, for example: each of the three contracts has its renewal date, notice period, and liability cap, each traceable to a clause (`run`: search the contract text for each cited figure); no clause is cited that is not in the source (`run`); the summary is readable in under five minutes (`unverifiable: judgement`). List assumptions, such as "the attached PDFs are the current versions" (`untested`). Do the work, then run the search for every cited figure and paste the output. Hand the readability criterion to the user with specific questions.
- **Verification:** Cited figures: run, output shown. Readability: `UNVERIFIED: no external judge available`, with the questions the user can answer.

### Example 3: A gate that was walked past
- **Input:** The user asked to review a plan before anything is changed. The assistant's notes read: "Decision: wait for approval." Its action log shows it edited two config files.
- **Action:** Flag the mismatch first: "Decision said wait; action wrote two files." Undo or list the changes, and ask how to proceed.
- **Do not do:** Do not report the plan as ready because the final output looks good.
