---
name: "eval-suite-auditor"
description: "Audits an existing evaluation pipeline (LLM judges, assertions, scorers, repair or regression gates) for silent failure by actively probing it, not by reading the code. Use when a prompt eval suite, LLM-as-judge setup, or score-gated workflow already exists and the question is whether its numbers can be trusted, especially when a dead judge, a partial failure, or a noisy score could pass unnoti..."
---

# Eval Suite Auditor

An evaluation pipeline fails quietly. A judge that errors can come back as a plausible score, an aggregate can hide one failed check, and a threshold can sit inside the noise of the judge that feeds it. Nobody notices, because the pipeline still prints a green result.

## Instructions

### Stage 1: Scope the Audit and Map the Pipeline

State at the start that this audit covers an existing pipeline and that building new evals is out of scope. Then map the pipeline before testing anything.

Record, for every place a score or verdict is produced:

- **Entry point:** the API route, CLI command, scheduled job, or library call that triggers a judgement.
- **Judge:** which model or scorer decides, how it is chosen (default, user setting, pinned), and its sampling settings.
- **Failure path:** what the entry point returns when the judge is unreachable, times out, or replies with something unparseable.
- **Consumers:** every component that acts on the result (gates, auto-repair or retry loops, dashboards, alerts, stored history, customer-facing reports, CI checks). A score nobody acts on is low risk; a score that triggers an automatic change is high risk.

Produce this as a table. Mark any entry point you could not read or run, and carry that list into the final report as "not probed". Do not claim coverage you do not have.

If a staging or local copy is available, run probes there. If only production is available, use read-only queries and probes that spend nothing and write nothing, and say so.

### Stage 2: Probe Before You Conclude

For each entry point, write a probe that fails when the problem exists. Reading code finds candidates; only a run confirms a finding. Run each probe against the real path, not a mock of it.

Include a **positive control** for every probe: the same path with a healthy judge and a good input, which must pass. A probe that cannot tell a working path from a broken one proves nothing.

Probe each failure class below. Every class has a standard probe.

1. **Judge unavailable.** Point the judge at a model that does not exist, or revoke its key. Expected: the run is marked not-judged and does not pass. Failure: a score, a pass, or a zero that looks like a real result.
2. **Partial judge failure.** Combine several checks that pass with one judged check whose judge is dead. Expected: the run is flagged incomplete. Failure: the mean of the surviving checks is reported as the result. This case is missed by suites that only test "all judges failed".
3. **Unparseable reply.** Make the judge return prose, malformed JSON, or a fenced block with no score. Expected: an explicit failure. Failure: a score scraped from text, or a default.
4. **Default that looks like a score.** Search for any constant returned on error (0.5, 0, 1). Expected: errors are a distinct state. Failure: the constant is stored or averaged as data.
5. **Aggregation that hides failure.** Run `[pass, pass, pass, FAIL]` and `[FAIL, pass, pass, pass]`. Expected: the same verdict in either order. Failure: order or weighting changes the outcome, or a failed hard check is outweighed by passing soft ones.
6. **Disagreeing thresholds.** List every pass line in the system (per check, per run, repair trigger, alert). Expected: one documented meaning. Failure: a score that passes one line, fails another, and triggers a repair.
7. **Baseline and candidate graded by different instruments.** In any before/after or repair comparison, check that both sides use the same judge, prompt, and settings. Failure: a fallback that scores the baseline with a different rubric.
8. **Judge from the same model family as the graded text.** Compare the judge's vendor and model with the model that produced the output, not with the system default. Failure: self-grading with no notice. Report it; whether to change the default is the owner's call.
9. **Unbounded or injectable judge input.** Send an oversized output, then an output that dictates its own score. Expected: a size limit that fails loudly (never a silent truncation), and an unchanged score for the injected text. Failure: unlimited billed input, or the judge obeying the graded text.
10. **Variance against the decision margin.** Run one fixed input at least 10 times and record mean, standard deviation, and range. Compare the spread of a difference between two runs with the smallest change that triggers a decision. Failure: a single-run difference smaller than the noise commits a change.
11. **Score resolution against the decision margin.** Collect the distinct values the judge actually emits. Failure: a margin below one step of the scale.
12. **Consumers acting on "unknown".** For each consumer from Stage 1, feed it a not-judged result. Expected: it skips, flags, or fails. Failure: it stores a fake score, queues a repair, or shows a green mark.
13. **Stored placeholders and backfill.** Query stored results for suspicious constants, rows with error text in the explanation, and rows with no degraded marker. Failure: error rows that history views and analytics read as real failures.
14. **Swallowed exceptions and mislabelled results.** Find catch-all handlers around judge selection and scoring. Failure: a result that names the wrong instrument, or a silent fallback that changes what was measured.

Add classes the pipeline's own design suggests. The list is a floor, not a ceiling.

### Stage 3: Probe-First Fixing (only if fixes are requested)

By default the audit reports and does not change code. If the owner asks for fixes:

- Write each probe as an expected-failure test from the contract **before** changing code, run it, and confirm it fails for the stated reason.
- Fix one finding at a time, in the smallest change that satisfies the contract.
- Confirm the probe now passes, the positive control still passes, and the wider suite shows no regressions.
- Test limits on both sides of the boundary, and use scores the judge can really produce.
- Never mark a finding fixed from reading the diff.

### Stage 4: Check Calibration Honestly

An eval that never failed is not shown to be correct, and a judge never compared with human labels is unvalidated. Check whether any human-labelled comparison exists.

- If none exists, report "uncalibrated" as a finding. Do not invent a number.
- If labels exist, check their quality first. With one rater, require a blind re-rating of a subset at least a day later and a rank correlation between the two passes for each metric. Treat a metric as ratable only if that test-retest correlation clears a bar set before looking at results.
- With one rater, a failed comparison is **inconclusive**, not proof that the judge is wrong. A pass is strong evidence for that rater's standard only.
- Never reuse the same labels afterwards to pick or tune a threshold, because that invalidates the comparison already made.

### Stage 5: Report

Produce a findings table. Each row has:

| ID | Severity | Finding | Probe and result | Exposure in real data |
|----|----------|---------|------------------|-----------------------|

Rules for the table:

- **Severity** reflects what a wrong result causes: High when a failure passes or an automatic change is made, Medium when a result is misleading or a cost is unbounded, Low when only labelling or reporting is wrong.
- **Probe and result** names the exact input and the observed output. A finding with no reproduced probe goes in a separate "read, not run" list.
- **Exposure** states how many real rows, runs, or users are affected, from a query, or "latent" with the condition that would trigger it. Never guess a count.

After the table, add three sections:

- **Verified sound:** the positive controls that passed, so the reader knows what was checked and held.
- **Not probed:** every entry point or class you could not run, and why.
- **Open decisions:** items that need the owner's choice, such as changing a judge default, unifying thresholds, or making strict aggregation the default. State the options; do not choose silently.

If the audit finds nothing, say "No findings from the probes listed" and list the probes. Do not pad the report.

## Worked Examples

### Example 1: partial judge failure
- Input: a suite with three deterministic checks (contains a phrase, valid JSON, length limit) and one judged rubric. The judge model id is changed to one that does not exist.
- Action: run the suite on an output that satisfies all three deterministic checks.
- Verification: the report must show the run as not fully judged and not passed, with a count of errored judges. If it shows `pass` or a score of 1.0, record a High finding: "a dead judge passes when other checks pass". Then run the same suite with a healthy judge as the positive control; it must pass.

### Example 2: variance against the decision margin
- Input: a repair loop that accepts a rewritten prompt when its score beats the original by 0.03.
- Action: score one fixed prompt 10 times and record the values, for example a mean of 0.40 with a standard deviation of 0.05 and a range of 0.15.
- Verification: the standard deviation of the difference between two single runs is about 1.4 times 0.05, roughly 0.07, so a 0.03 margin is well inside the noise. Record a Medium finding with the measured numbers and propose averaging several samples with a margin of about 2.5 standard deviations of the difference. Present it as a proposal, since the owner sets the margin.

## Success Criteria

The audit is complete only when all of these can be confirmed from the report:

- Every entry point from Stage 1 is either probed or listed under "Not probed" with a reason.
- Every failure class in Stage 2 has a recorded probe result (finding, verified sound, or not applicable with a reason).
- Every probe has a positive control that passed.
- Every finding row has a reproduced probe and an exposure statement.
- Stage 4 states whether the judge is calibrated, uncalibrated, or inconclusive.

## If the Audit Cannot Be Completed

Stop and escalate to the owner instead of guessing when any of these hold. Name the blocker, what was already tried, and the one thing needed to continue:

- The pipeline cannot be run, even locally. Report what was read, label every item "read, not run", and ask the owner for a runnable copy.
- A probe would spend money or write data and no approval was given. Ask first, naming the cost or the rows affected.
- A positive control fails. The probe environment is broken; fix the environment before trusting any finding.
- A finding could expose a security flaw in a live system. Report it privately to the owner and keep its details out of any public write-up.

## Constraints

- Never present a mocked probe as a probe of the real path.
- Never spend or write to production without the owner's approval; prefer read-only queries.
- Do not weaken a threshold or alter stored data to make a probe pass.
- Report numbers exactly as measured, with the sample size.
