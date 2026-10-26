# Ambition Calibrator

A Claude Code skill that makes a task deeper rather than bigger. It decides whether a request should be expanded at all. If so, it climbs a goal ladder, asks for the raw inputs and professional methods behind the task, borrows lenses from adjacent fields, and checks the result with a judge other than the model. Based on Felix Rieseberg's article [How to be more ambitious](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/).

## Install

Copy [`SKILL.md`](./SKILL.md) to `.claude/skills/ambition-calibrator/SKILL.md` in your project, or to `~/.claude/skills/ambition-calibrator/SKILL.md` to use it everywhere. No account and no API key.

## Use it

Ask Claude Code something like:

- "go deeper on this"
- "make this more ambitious"
- "build the QBR deck for the board"

Short, clear commands such as "run the tests" or "rename this function" bypass the skill and run as asked. Routine debugging and prompt-wording rewrites are handed to other skills.

When it does expand, it shows the rewritten task and waits for your confirmation before running it.

## Hosted version

The platform's Context Engineering tool generated this file from a written procedure. A free account is enough to try it on your own goal: [promptoptimizer.xyz](https://promptoptimizer.xyz/about/context-engineer?utm_source=github&utm_medium=readme&utm_campaign=ambition-calibrator-24)

The other skills are listed in [`../README.md`](../README.md).
