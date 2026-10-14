# Eval Suite Auditor

A Claude Code skill for auditing an eval suite you already have, rather than writing a new one. It looks for the failures that still print a green result: a judge that never ran, a partial judge failure averaged into a pass, thresholds that disagree, and a decision margin smaller than the judge's own noise.

## Install

Copy [`SKILL.md`](./SKILL.md) to `.claude/skills/eval-suite-auditor/SKILL.md` in your project, or to `~/.claude/skills/eval-suite-auditor/SKILL.md` to use it everywhere. No account and no API key.

## Use it

Ask Claude Code something like:

- "audit my eval suite"
- "can I trust this judge score?"
- "why did this eval pass when the judge errored?"

It then:

1. maps every entry point that produces a score, the judge it uses, what it returns when the judge is down, and what acts on the result;
2. probes 14 failure classes, each with a positive control, so a probe that cannot tell a working path from a broken one is caught;
3. fixes probe-first, only if you ask;
4. checks calibration honestly (a single rater's failed comparison is reported as inconclusive, not as proof);
5. reports a table: severity, the exact probe and its result, and the exposure in real data, followed by what it verified, what it did not probe, and the decisions that are yours.

## Hosted version

The platform's evaluation view marks a run "not fully judged" when a judge fails, instead of showing a score from the checks that survived. A free account is enough to try it: [promptoptimizer.xyz](https://promptoptimizer.xyz/about/context-engineer?utm_source=github&utm_medium=readme&utm_campaign=eval-suite-auditor)

MIT licensed, see [`LICENSE`](./LICENSE). The other skills are listed in [`../README.md`](../README.md).
