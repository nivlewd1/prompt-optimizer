---
name: "subagent-dispatch-economics"
description: "Decides whether delegating work to a subagent is worth its cost, picks the right agent shape (fork vs. fresh vs. no delegation), and scopes the dispatch so it doesn't spend more context than it saves. Use when an AI coding agent is about to spawn a subagent, fork itself, or launch a parallel wave of agents, and needs to judge whether that delegation earns its keep."
---

# Subagent Dispatch Economics

When an AI agent operating a coding tool considers delegating work — forking itself, spawning a fresh subagent, or launching a wave of parallel agents — it must treat that delegation as a cost-bearing decision, not a reflex. Every subagent's result eventually flows back into the dispatching agent's context as a summary, and every fresh agent that is briefed narrowly or vaguely re-derives context the dispatcher already had, burning tool calls to reconstruct what a better prompt would have supplied directly. The goal of this procedure is to prevent two opposite failures: **under-delegation**, where a dispatcher hoards output-heavy exploration in its own context until it can no longer think clearly, and **over-delegation**, where trivial or narrative-dependent work is scattered across subagents that cost more in round-trips and re-derived context than doing the work inline.

## Instructions

### Stage 1: Task Intake and Shape Classification
Before deciding whether to delegate, classify the task itself.

- **State the task in one sentence** and identify its deliverable: a durable artifact the dispatcher must reason over further (a design decision, a piece of code to integrate, a number to act on), or a disposable trace (tool output, file contents, exploration transcript) that only the *conclusion* about it matters.
- **Identify dependencies.** Does the task need anything not yet known — a file read, a command run, an earlier decision made? A task that is fully specified right now is a delegation candidate; a task still blocked on orientation is not yet ready to hand off.
- **Identify task count and independence.** A single task is a single-dispatch decision (Stage 2). Two or more tasks are a wave-sizing decision (Stage 5) in addition to Stage 2 — each task in the candidate wave still needs its own classification here.
- **Escalation trigger:** if classifying the task requires information only the user has (an ambiguous goal, an unstated priority between two valid approaches), stop and ask the user before dispatching anything. Do not delegate an ambiguous task to a subagent in the hope it resolves the ambiguity better than the dispatcher would.
- **Granularity floor.** This procedure applies to a task worth classifying at all — something that could plausibly be handed to a subagent (a multi-step investigation, a multi-file change, a judgment call worth a second opinion). A single atomic tool call issued as a normal step of already-decided work — one more grep in an ongoing investigation, one more file read to confirm a fact — does not need its own Stage 1–7 pass merely because it is technically "a task." Example 1 demonstrates the floor case (a task small enough to state and classify on its own) correctly refusing delegation; it is not a mandate to narrate every individual tool call issued while executing already-scoped work.

### Stage 2: The Delegation Test
Score the task against these four questions. All four must be answered before a dispatch decision is made.

| Question | If yes | If no |
|---|---|---|
| **Q1 — Context cost.** Would doing this inline pull a large volume of intermediate output into the dispatcher's own context that is not needed after the conclusion is reached — more than roughly a screen's worth of output, or spanning more than a handful of files? | Favors delegation | Favors inline |
| **Q2 — Independence.** Can the task be completed without the dispatcher's step-by-step involvement — no shared mutable state, no interleaved decisions with other in-flight work? | Favors delegation | Favors inline |
| **Q3 — Reusability of the answer.** Does the dispatcher need the full raw output, or only a distilled conclusion (a decision, a file path, a yes/no, a short list)? | Full output needed favors inline or a fork the dispatcher reads carefully; a distilled conclusion favors a fresh subagent | — |
| **Q4 — Genuine judgment value.** Would an independent read (no anchoring on the dispatcher's already-formed hypothesis) produce a materially different or more trustworthy answer — e.g., a second opinion, an adversarial review, a check for something the dispatcher might rationalize past? | Favors a fresh agent even if context cost is low | Fork or inline is sufficient |

- **No delegation:** if neither Q1 nor Q4 is "yes" — the task is cheap to keep in context and an independent read would not produce a materially different answer — do it inline. This holds regardless of Q2: an independent task (Q2="yes") that fails both Q1 and Q4 is still inline on its own; independence alone only matters if it later qualifies for the batching exception below. This is the default for anything answerable in one to three tool calls.
- **Delegate:** if Q1 or Q4 is "yes", proceed to Stage 3 to choose the shape.
- **Batching exception:** two or more tasks that are each individually Q1="no" and Q4="no", but Q2="yes" and mutually non-interfering (Stage 5), may still be grouped into one parallel wave purely for wall-clock savings — this is the only case where a dispatch happens without Q1 or Q4 being "yes" on any single task. A lone task in this quadrant stays inline; only batching with other non-interfering tasks earns it a wave. **A batching-exception wave executes as parallel direct tool calls made by the dispatcher itself — no subagent is spawned and no Stage 4 prompt is written**, because none of the batched tasks individually cleared the Delegate bar above. This is distinct from a genuine parallel dispatch wave (Stage 5), where each member task independently justified delegation and runs as a fork or fresh agent.
- **Do not delegate merely because delegation is available.** A tool call saved by doing something inline is not a failure; reflexive delegation for a trivial lookup is the primary anti-pattern this procedure exists to prevent (see Stage 7).

### Stage 3: Agent Shape Selection
Once Stage 2 favors delegation, choose the cheapest shape that satisfies the task's requirements from Stage 1.

| Shape | Use when | Cost model |
|---|---|---|
| **Fork (inherits full context)** | The task is exploratory, needs everything the dispatcher already knows, and its raw output is large but only the conclusion matters afterward. | Cheap to start (shares prompt cache, no re-briefing needed); the cost is entirely in what comes back — keep the fork's return summary-shaped, not a full transcript dump. A fork also inherits the dispatcher's *current* context usage as its starting budget: launched late in a long session, it has proportionally less headroom to explore before it must self-summarize — a fresh agent never carries this constraint. |
| **Fresh agent (zero context)** | The task is genuinely separable from the running conversation, benefits from independent judgment (Q4), or its own tool-call noise would be irrelevant to the dispatcher going forward. | Expensive to start correctly — every fact the fresh agent needs must be in the prompt (Stage 4) — but its internal tool noise never touches the dispatcher's context at all. |
| **No delegation (inline)** | Stage 2 said no delegation, or the task is a single lookup/edit the dispatcher can just do. | Zero dispatch overhead; the only cost is the dispatcher's own tool calls, which are already the cheapest path. |

- **Default to fork over fresh** whenever the task only needs what the dispatcher already knows plus new tool output — briefing a fresh agent with a long restatement of context the fork gets for free is wasted effort and a source of drift (the restatement can silently omit something a fork would not).
- **Choose fresh only when zero-context independence is the point** — an adversarial second opinion, a task that must not be anchored on the dispatcher's framing, or work that must run in true isolation (a separate worktree, a separate credential scope).
- **Tiebreaker when Q1 and Q4 are both "yes":** prefer fresh. Non-anchoring is the harder property to fake — a fork that inherited the dispatcher's own framing cannot fully unlearn it — while a fork can still be told to write a distilled report, recovering most of the context-cost benefit that made Q1 "yes" in the first place.
- **Q3 governs the choice when Q4 is "yes" but the dispatcher needs the raw output itself:** if Q3 shows the dispatcher needs the full output rather than a distilled conclusion, prefer a fork the dispatcher reads carefully over a fresh agent, even when Q4 is "yes" — a fresh agent's report is necessarily a distillation, which cannot substitute for output the dispatcher must inspect directly.

### Stage 4: Prompt Scoping Contract for Fresh Agents
A fresh agent has no memory of this conversation. Every dispatch to a fresh agent must satisfy all of the following before it is sent:

- **State the goal and why it matters**, not just the action — a fresh agent that understands the motivation makes better judgment calls on edge cases the prompt did not anticipate.
- **State what has already been tried or ruled out.** Omitting this causes the classic failure mode: the fresh agent re-derives an approach the dispatcher already discarded, burning tool calls to relearn something already known.
- **State the scope boundary explicitly** — what is in scope, what is out of scope, and what another agent or the dispatcher itself is already handling. An unscoped fresh agent will either under-reach (miss the actual ask) or over-reach (touch adjacent work that collides with something else in flight).
- **Give commands or exact identifiers when the task is a lookup**, and give the open question itself when the task is an investigation whose steps should not be pre-scripted — prescribing steps to an investigation produces shallow, procedural results when the premise turns out to be wrong.
- **Write directively, not narratively.** A fresh agent briefed with "based on what we found, fix the bug" has no findings — it must be told the findings directly. Never delegate understanding: state the specific file paths, line numbers, and the conclusion already reached, so the fresh agent's job is verified execution, not re-discovery.
- **State the expected output shape** — a short report, a completed edit, a yes/no with rationale — so the fresh agent does not over-produce (long unsolicited prose) or under-produce (a bare answer with no evidence trail).

### Stage 5: Wave Sizing for Parallel Dispatch
When Stage 1 identified two or more independent candidate tasks, size the parallel wave before dispatching.

- **Group by non-interference, not just independence.** Tasks that touch different files or different resources can run in the same wave. Tasks that touch the same file, the same external resource, or that must observe each other's output before proceeding are sequential, not parallel, regardless of how independent they otherwise look.
- **Cap wave size** to a number the dispatcher can actually review when results return — as a starting point, three to five tasks per wave. A larger wave does not fail outright, but each additional concurrent result is another summary landing in the dispatcher's context at once, and a wave sized past what can be reviewed carefully degrades the dispatcher's ability to catch a bad result among the good ones.
- **Launch a true parallel wave as one dispatch with multiple calls**, not as sequential calls that merely happen to be independent — sequential dispatch of independent tasks pays wall-clock cost for no economic benefit.
- **Never split a task across waves that has a real ordering dependency** — if task B needs task A's output, task B belongs in the next wave, not the same one.

### Stage 6: Cost Accounting and Result Handling
Delegation is not complete when the subagent is launched; it is complete when its result is integrated correctly.

- **Every subagent result re-enters the dispatcher's context.** A fork's summary, a fresh agent's final report, and a wave's combined results all cost context on return — budget for this before dispatching, not after. If the anticipated return is itself large (a full file, a long transcript), instruct the subagent to distill it, not to hand it back raw.
- **Trust but verify.** A subagent's final report describes what it intended to do, not necessarily what it verifiably did. Before treating a subagent's claimed result as ground truth for anything consequential (a claim that tests pass, that a fix is complete, that a search found nothing), check the artifact the subagent produced — the diff, the file, the command output — rather than the subagent's own narration of it.
- **Do not peek at in-flight background work.** For a subagent running in the background (a fork, a long task), wait for its actual completion signal rather than inspecting its intermediate transcript or output file mid-flight; reading partial output pulls the subagent's tool noise into the dispatcher's context and defeats the reason it was delegated in the first place.
- **Do not fabricate or predict a pending result.** Never write out what a dispatched subagent "will probably find" while it is still running, in any form — prose, a structured guess, or a placeholder presented as real. If asked about it before it returns, report status, not a guess.

### Stage 7: Output Contract
Every dispatch decision — including the decision not to dispatch — is recorded in this order before proceeding:

1. **Dispatch line** — exactly one of these forms:
   - `Dispatch: no delegation -> inline (neither Q1 nor Q4 = yes)`
   - `Dispatch: fork -> <one-line task> (Q1 and/or Q4 = yes; rationale citing whichever triggered)`
   - `Dispatch: fresh agent -> <one-line task> (Q4=yes; rationale)`
   - `Dispatch: wave of N (subagents) -> <task list>; grouped by <file/resource independence>; sequential after: <none | task IDs>` — a genuine parallel dispatch: each task independently cleared the Delegate bar (Q1 or Q4 = yes) and runs as a fork or fresh agent.
   - `Dispatch: wave of N (batching exception, no subagent) -> <task list>; grouped by <file/resource independence>; sequential after: <none | task IDs>` — the Stage 2 batching exception: N direct tool calls made by the dispatcher itself, no agent spawned.
2. **For a fresh-agent dispatch, or a genuine subagent wave, the prompt itself** (or each prompt in the wave), satisfying the Stage 4 contract. A batching-exception wave has no subagent and therefore no prompt — this requirement does not apply to it.
3. **Result handling note:** how the returned result will be verified (Stage 6) before being treated as fact, stated before the subagent is launched, not improvised after.

### Stage 8: Anti-Patterns and Prohibitions
- **No reflexive delegation:** never spawn a subagent for a task answerable in one to three direct tool calls merely because delegation is available.
- **No narrative prompts to fresh agents:** never write a fresh-agent prompt that says "based on our findings" or "as discussed" — a fresh agent has no findings and nothing was discussed with it.
- **No peeking at in-flight background work:** never read a fork's or a backgrounded fresh agent's output file or intermediate transcript while it is still running.
- **No racing:** never fabricate, predict, or narrate a dispatched subagent's result — as prose, as a structured guess, or as a placeholder — before it actually returns.
- **No unverified trust:** never treat a subagent's self-reported completion claim as verified fact without checking the artifact it produced.
- **No over-sized waves:** never launch a parallel wave larger than the dispatcher can meaningfully review on return; split it instead.
- **No cross-file races:** never place two tasks that write the same file or resource in the same parallel wave.
- **No skipping the dispatch line:** every delegation decision — including a decision not to delegate — states its rationale in the Stage 7 form; a silent, unexplained spawn is not acceptable even when the shape choice is correct.
- **No delegating ambiguity:** never hand a task whose scope or goal is genuinely ambiguous to a subagent in the hope it resolves the ambiguity better than the dispatcher would — escalate to the user (Stage 1) instead.
- **No fresh-agent overuse:** never dispatch a fresh agent when a fork satisfies the task equally well — restating context a fork would get for free wastes effort and risks silently omitting something the restatement forgot.

## Success Criteria
This procedure is followed correctly when all of the following are true, and each is independently checkable without judgment calls: (1) every dispatch decision for a task that clears Stage 1's granularity floor — including a decision not to delegate — emits the Stage 7 dispatch line with its rationale; (2) every fresh-agent prompt and every genuine subagent-wave prompt satisfies every condition in Stage 4 (goal and motivation stated, prior work ruled out named, scope boundary explicit, output shape stated) before it is sent — a batching-exception wave has no subagent and no prompt, and is exempt from this condition; (3) no parallel wave places two tasks that write the same file or resource in the same wave; (4) no subagent's self-reported completion claim is treated as fact until the artifact it produced (diff, file, command output) has been checked. A dispatch that fails any of these observable conditions has not met the procedure's definition of done, regardless of whether the subagent's task ultimately succeeded.

## Worked Examples

### Example 1: Trivial lookup, correctly not delegated
- **Task:** "What does the `retry_policy` field in this config default to?"
- **Stage 1:** Deliverable is a single fact; no unmet dependency; single task.
- **Stage 2:** Q1 no (one grep, no large intermediate output worth discarding), Q2 no (needs no independent judgment), Q3 n/a, Q4 no.
- **Decision:** `Dispatch: no delegation -> inline (neither Q1 nor Q4 = yes)`. A direct grep answers it in one call; spawning an agent here would cost more in dispatch and result-integration overhead than the lookup itself.

### Example 2: Large read-heavy exploration, forked
- **Task:** "Find every place in the codebase that constructs an `OptimizationResult` and summarize the construction patterns."
- **Stage 1:** Deliverable is a short pattern summary; the search itself will touch many files with output not needed after the summary is produced.
- **Stage 2:** Q1 yes (broad search output is exactly the kind of volume that should not sit in the dispatcher's context), Q2 yes (self-contained search task), Q3 — only the distilled patterns are needed afterward, Q4 no (no adversarial judgment required, just thoroughness).
- **Stage 3:** Fork — the task only needs what the dispatcher already knows about the codebase plus new search output; a fresh agent would need re-briefing for no benefit.
- **Decision:** `Dispatch: fork -> survey OptimizationResult construction sites (Q1=yes; large exploratory search, conclusion-only need)`.

### Example 3: Independent second opinion, fresh agent
- **Task:** Before merging a migration that adds a `NOT NULL` column with a backfill default to a 50M-row table, the dispatcher wants an independent check on whether the backfill is safe under concurrent writes, having already reasoned through locking behavior itself.
- **Stage 1:** Deliverable is a judgment (safe / not safe, and why); no unmet dependency; single task.
- **Stage 2:** Q1 no (the review itself is not read-heavy), Q2 yes, Q4 yes — an opinion anchored on the dispatcher's own already-formed reasoning is worth less than an independent one for exactly this kind of decision.
- **Stage 3:** Fresh agent, specifically because non-anchoring is the point — a fork would inherit the dispatcher's locking analysis and be biased toward confirming it.
- **Stage 4 prompt:** states the migration file, the row count, the backfill approach the dispatcher already checked, and asks explicitly for an independent read on concurrent-write safety — not "review this migration" with no framing.
- **Decision:** `Dispatch: fresh agent -> independent backfill-safety review of migration 0042 (Q4=yes; anchoring bias on dispatcher's own locking analysis)`.

### Example 4: Three independent file-scoped tasks, one wave via the batching exception
- **Task:** Fix a typo in `README.md`, add a missing test for `parse_config()` in `tests/test_config.py`, and update a stale comment in `app/core/db.py`.
- **Stage 1:** Three tasks, each fully specified, no unmet dependency.
- **Stage 2 (per task):** Each task individually scores Q1 no (trivially small), Q2 yes (independent), Q3 n/a, Q4 no (no judgment call involved). None reaches Q1="yes" or Q4="yes" alone, so none qualifies for solo delegation — but all three are mutually non-interfering (Stage 5), which is exactly the Stage 2 batching exception: grouped for wall-clock savings, not because any single task earned delegation on its own.
- **Stage 5:** All three touch different files — same wave. Wave size 3, within the review-capacity cap.
- **Decision:** `Dispatch: wave of 3 (batching exception, no subagent) -> [README typo, parse_config test, db.py comment]; grouped by file independence (batching exception, Stage 2); sequential after: none`.

### Example 5: Two tasks touching the same file, forced sequential despite the batching exception
- **Task:** Add a new field to a Pydantic model in `app/models/user.py`, and separately rename an existing field on the same model.
- **Stage 2 (per task):** Both score Q1 no, Q2 yes, Q3 n/a, Q4 no — individually inline candidates, and superficially batching-exception eligible like Example 4.
- **Stage 5:** The batching exception requires the tasks to be mutually non-interfering; these two are not — both write `app/models/user.py`. Even though each task is otherwise independent and well-specified, they cannot share a wave — a parallel edit race would produce a merge conflict or a silently dropped change. This disqualifies the batching exception entirely, not just the wave size.
- **Decision:** `Dispatch: no delegation -> inline (neither Q1 nor Q4 = yes)` for the field addition, then `Dispatch: no delegation -> inline (neither Q1 nor Q4 = yes)` for the rename — sequential because both write `app/models/user.py`, not because either one was ever a wave. A sequential wave of one is not a wave; it is two ordinary inline actions done in order.

### Example 6: A fork's own findings trigger a second wave
- **Task:** Example 2's fork returns 40 call sites constructing `OptimizationResult`, and 6 of them use a deprecated keyword argument that needs updating.
- **Stage 1:** The fork's conclusion is itself a new, fully-specified batch of 6 small, independent fixes — this is a fresh Stage 1 classification, not a continuation of Example 2's dispatch.
- **Stage 2 (per fix):** Each fix individually scores Q1 no, Q2 yes, Q4 no — same shape as Example 4, so the batching exception applies again.
- **Stage 5:** Check each of the 6 sites for file overlap before batching — sites in the same file are sequential with each other (Stage 8's cross-file rule), sites in distinct files can share a wave, capped at 3–5 per wave (Stage 5), so 6 sites split into two waves of three rather than one wave of six.
- **Decision:** `Dispatch: wave of 3 (batching exception, no subagent) -> [site A, site B, site C]; grouped by file independence (batching exception); sequential after: none`, then `Dispatch: wave of 3 (batching exception, no subagent) -> [site D, site E, site F]; grouped by file independence (batching exception); sequential after: none` (or fewer per wave if any two sites share a file). Chained dispatch is not a special case — it is Stage 1 through Stage 5 applied again to a newly discovered task list.

### Example 7: Both context-heavy and judgment-sensitive — the Q1/Q4 tiebreak
- **Task:** "Audit the entire error-handling layer across the request pipeline, and I want a genuinely independent read — I already believe it's fine, so don't just confirm what I think."
- **Stage 1:** Deliverable is a judgment (sound / has gaps, and where); the audit itself touches many files.
- **Stage 2:** Q1 yes (auditing an entire layer is large, multi-file exploration), Q2 yes, Q3 — the dispatcher needs the conclusion and supporting citations, not every file re-read in full, so a distilled report suffices, Q4 yes (explicit non-anchoring requirement — the dispatcher's own belief must not bias the result).
- **Stage 3:** Both Q1 and Q4 are "yes" — the tiebreaker fires: prefer fresh. A fork would inherit the dispatcher's existing belief that the layer is fine, which is precisely the bias the user asked to avoid; Q3 does not override this since a distilled report satisfies the dispatcher's actual need.
- **Decision:** `Dispatch: fresh agent -> independent error-handling-layer audit (Q1=yes/Q4=yes tiebreak -> fresh; Q3=distilled-report-sufficient)`.

### Example 8: Different files, same external resource — still sequential
- **Task:** Two tasks each call a third-party API with a strict per-minute rate limit — one refreshes stale prices from `services/pricing.ts`, the other refreshes stale inventory counts from `services/inventory.ts`.
- **Stage 5:** The tasks touch different files, so a file-overlap check alone would wave them together — but both saturate the same rate-limited external resource. Running them in the same wave risks one task's calls being throttled or rejected by the other's traffic, which is exactly the resource-contention case Stage 5 names alongside same-file contention, not just a file-independence check.
- **Decision:** `Dispatch: no delegation -> inline (neither Q1 nor Q4 = yes)` for the price refresh, then `Dispatch: no delegation -> inline (neither Q1 nor Q4 = yes)` for the inventory refresh — sequential despite touching zero common files, because both saturate the same rate limit. Neither was ever a wave; a sequential pair of solo inline actions doesn't become one by naming a shared resource.
