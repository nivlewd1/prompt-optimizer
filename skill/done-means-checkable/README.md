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

Single-step edits, "run the tests" (a check you named), and anything with a ceiling word ("just", "only", "quick") bypass the skill and run as asked.

## What was tested

Fresh-agent dry runs with pass conditions written beforehand, one model, small numbers. A control run with no skill reached the same correct answers on the cases tried, so the measurable effect is the visible trail (written criteria, pasted judge output, an `Unverified` list), not better answers. It has not been measured whether work done this way is better.

## Hosted version

The platform's Context Engineering tool generates skills like this from a written procedure. A free account is enough to try it on your own goal: [promptoptimizer.xyz](https://promptoptimizer.xyz/about/context-engineer?utm_source=github&utm_medium=readme&utm_campaign=done-means-checkable-25)

The other skills are listed in [`../README.md`](../README.md).
