---
name: "advisor"
description: "Decides which Claude model tier does which job when Fable 5.2 is available, and sets the handoff rules between them. Use when a task could run under native /advisor or with Fable as main model delegating to cheaper models. Not for deciding whether to delegate at all (see subagent-dispatch-economics)."
---

# advisor

Chooses between native /advisor (a cheaper model works, Fable 5.2 advises) and Fable 5.2 as main model delegating down to cheaper models, then assigns each job to a tier and enforces the handoff rules.

## Instructions

### Steps
1. **Confirm delegation is decided.** Whether to delegate, and fork vs. fresh agent, belongs to `subagent-dispatch-economics`. This skill starts after that decision. Do not restate it. If the answer is "don't delegate", stop here and do the task in the main session.
2. **Choose the mode.**
   - **Mode A, native `/advisor`:** one cheaper main model can do the whole task and only the decisions need a stronger model. The advisor has no tools and cannot delegate or orchestrate. Its call timing is model-driven; there is no setting to cap or force calls, so ask in your instructions if you want more or fewer.
   - **Mode B, Fable 5.2 as main:** the work must be split across models. Fable plans, judges and writes the final copy. It delegates lower-level jobs to fresh subagents with a per-spawn model override.
3. **In Mode B, assign tiers:**
   | Job | Model |
   |---|---|
   | Plan, make the calls, write the final copy | Fable 5.2 (main) |
   | Collect sources, read-only lookups | Haiku |
   | Fact-check each claim against its saved source (web page, file or input record) | Sonnet |
   | Cold-read judge of the final draft (no project context) | Haiku or another cheap model, a fresh agent: never the writer, never the agent that collected |
4. **Spawn cheap jobs as fresh agents.** A forked subagent inherits the parent model and ignores the model override.
5. **Apply the handoff rules** (below) to every subagent.
6. **Gate on the checker.** Collector output is not trusted until a checker tier that did not produce it passes it. The orchestrator's own drafts go through the checker too.
7. **Keep the run log.** One row per subagent: job, model, tokens (as the harness reports them; write "not available" if it doesn't), verdict, output file.

### Handoff Rules
- Every subagent writes its full result to a file. The file has no length limit.
- The message a subagent returns to the orchestrator is 200 words or fewer and names the file.
- The 200-word cap applies only to that return message, not to the result file and not to the orchestrator's final copy.
- Checker verdicts: PASS, FIX, UNSUPPORTED, NO SOURCE.

### Never
- Present the Sonnet + Opus advisor benchmark (+2.7 points, 11.9% lower cost, Anthropic blog, April 2026, older models) as a Fable 5.2 result.
- Let the writer judge its own draft.
- Use a forked subagent for a job meant for a cheaper model.

### Requirements
- Native /advisor is experimental and requires the Anthropic API, Claude Platform on AWS, or Claude Models on Google Cloud (Anthropic managed). Fable 5.2 requires Claude Code v2.1.321 or later. On some plans Fable usage, including as advisor, bills to usage credits.
