# Done Means Checkable

A Claude Code skill for work that has no built-in test: an analysis, a summary, a plan, a rewrite, a design. Before it does the work, the assistant writes acceptance criteria a stranger could mark pass or fail. After the work it runs the best judge that is not the model, shows the output unedited, and lists what stayed unverified. On runs with a gate ("show me before you change anything") it keeps a record of what it decided separate from what it did.

It works on its own and pairs with [`ambition-calibrator`](../ambition-calibrator/SKILL.md), which decides how deep a task should go.

## Install

Copy [`SKILL.md`](./SKILL.md) to `.claude/skills/done-means-checkable/SKILL.md` in your project, or to `~/.claude/skills/done-means-checkable/SKILL.md` to use it everywhere. No account and no API key.

## Use it

Ask Claude Code something like:

- "Is this summary right?"
- "Summarize these contracts for the board, and make sure it's right."
- "Verify this figure."

Single-step edits and "run the tests" (a check you named) bypass the skill and run as asked. A ceiling word ("just", "only", "quick") with no check requested also bypasses it, with a one-line `Check: bypassed (reason)` notice. A ceiling word with a check requested ("quickly check whether this summary matches the CSV") does not skip the check: it shrinks it to the smallest relevant one.

## What was tested

Fresh-agent dry runs with pass conditions written beforehand, one model, small numbers. A control run with no skill reached the same correct answers on the cases tried, so the measurable effect is the visible trail (written criteria, pasted judge output, an `Unverified` list), not better answers. It has not been measured whether work done this way is better.

### v1.3 changes, and what was re-run

Prompted by two comments on the Reddit post. Added: at least one must-not criterion per run (and the reviewer gets it as a "must not contain" list), a `Self-check vs judge:` line in the handoff, and a rule that a ceiling shrinks a requested check instead of cancelling it. 26 fresh-agent runs across the original and three revisions (one run per case unless stated). Observed on v1.3: the "quickly check" case came back with 2 criteria, one judge and a short report (earlier revisions wrote 4); "run the tests" and a plain rename stayed silent; with `ambition-calibrator` installed its `Ambition check:` line was printed; the `Self-check vs judge:` line appeared in every run where it applies.

What did not improve: on "draft a quick friendly email" the `Check: bypassed` notice printed in 3 of 3 runs on the original and 2 of 3 on v1.3. In a summary case the agent stated a derived total (a sum not in the source) after showing the arithmetic; the pre-written pass condition counted that as a miss, and the skill does not yet say how to treat derived figures. The `must-not` check on the final version was not re-run on that summary case.

## Hosted version

The platform's Context Engineering tool generates skills like this from a written procedure. A free account is enough to try it on your own goal: [promptoptimizer.xyz](https://promptoptimizer.xyz/about/context-engineer?utm_source=github&utm_medium=readme&utm_campaign=done-means-checkable-25)

The other skills are listed in [`../README.md`](../README.md).
