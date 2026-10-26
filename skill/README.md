# Claude Code Skills

Eleven free skills for Claude Code. Each one is a single `SKILL.md` that Claude loads when your request matches its description. No account, no signup, no API key, no install step. MIT licensed (see [`LICENSE`](./LICENSE)).

## Install a skill

1. Open the skill's folder below and copy its `SKILL.md`.
2. Put it in `.claude/skills/<skill-name>/SKILL.md` in your project, or in `~/.claude/skills/<skill-name>/SKILL.md` to use it in every project.
3. Ask Claude Code for the kind of work the skill covers. Claude picks it up from the skill's `description`.

## The skills

| Skill | What it does |
|---|---|
| [`agent-prompt-architect`](./agent-prompt-architect/SKILL.md) | Architects the system prompt, context budget, and tool contract of an AI agent as one system. |
| [`ambition-calibrator`](./ambition-calibrator/SKILL.md) | Decides whether a task should be made more ambitious, then rewrites it deeper rather than bigger: goal ladder, raw inputs and methods, borrowed fields, and a judge other than the model. |
| [`context-cartographer`](./context-cartographer/SKILL.md) | Assembles high-signal repository context before non-trivial implementation, debugging, or review work. |
| [`context-drift-auditor`](./context-drift-auditor/SKILL.md) | Audits whether a prompt or agent run has drifted from its original contract across turns, retrieved sources, edits, and decisions. |
| [`empirical-diagnostician`](./empirical-diagnostician/SKILL.md) | Evidence-based debugging: log extraction first, a hypothesis matrix for anything complex, and a root-cause contract before any edit. |
| [`eval-suite-auditor`](./eval-suite-auditor/SKILL.md) | Audits an existing evaluation pipeline (LLM judges, assertions, scorers, gates) for silent failure by probing it, not by reading the code. |
| [`prompt-complexity-triage`](./prompt-complexity-triage/SKILL.md) | Decides how much a prompt needs to change before rewriting it, then applies only the moves for that tier. |
| [`prompt-evaluation-engineer`](./prompt-evaluation-engineer/SKILL.md) | Turns prompts into reproducible evaluation protocols: contracts, test matrices, deterministic checks before rubrics. |
| [`prompt-injection-guard`](./prompt-injection-guard/SKILL.md) | A structured protocol for detecting and responding to prompt injection in LLM applications. |
| [`prompt-optimizer`](./prompt-optimizer/SKILL.md) | The platform's optimization methodology: classify the prompt, assess sophistication, optimize, and preserve technical parameters. |
| [`subagent-dispatch-economics`](./subagent-dispatch-economics/SKILL.md) | Decides whether delegating work to a subagent is worth its cost, and picks the right agent shape. |

## Generate one for your own domain

Most of these skills were produced with the Context Engineer on the hosted platform: describe a goal, get a `SKILL.md` bundle with examples and a helper script. You do not need it to use anything above.

A free account gets 3 basic SOPs and 1 full skill package a month (Claude Code and Ollama targets, default model): [promptoptimizer.xyz](https://promptoptimizer.xyz/about/context-engineer?utm_source=github&utm_medium=readme&utm_campaign=skill-index)
