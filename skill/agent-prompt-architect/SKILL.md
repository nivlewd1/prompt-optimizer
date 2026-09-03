---
name: "agent-prompt-architect"
description: "Architects the system prompt, context budget, and tool contract of an AI agent as one system. Use when designing a new agent prompt, reviewing an existing agent configuration, or debugging an agent that loops, mis-selects tools, or stops without a clear result."
---

# Agent Prompt Architecture

When a user asks to design, review, or improve the system prompt or tool configuration of an AI agent, the agent must follow this procedure to architect the prompt as part of a complete context system rather than as an isolated text block. The unit of design is the full token state — system instructions, tool definitions, retrieved context, and message history — because an agent that runs tools in a loop consumes all of it as one attention budget. The goal is to produce the smallest set of high-signal tokens that reliably drives the desired behavior, structured so behavior degrades gracefully instead of failing silently.

## Instructions

### Stage 1: Agent Contract and Boundary Definition
Before writing any instructions, define the contract the prompt must honor.

- **Task Scope:** State the agent's task in one to two sentences. The task must be narrower than "be a helpful assistant" and broader than a single canned response.
- **Success Criteria:** Write the observable, verifiable conditions that define a completed task. Prefer conditions that a tool result or a deterministic check can confirm.
- **Non-Goals:** List what the agent must NOT do, touch, or attempt, even when the user asks for it.
- **Escalation Path:** Define the default action when the agent cannot complete the task or detects a condition outside its authority. Escalation must be a named step, not an implicit behavior.
- **Role and Altitude:** Choose the working altitude — a level of abstraction that is specific enough to constrain behavior yet flexible enough for the model to exercise judgment. Avoid both hardcoded if-else logic and vague guidance that assumes shared context.
- **Instrumentation:** State what every run must capture — each tool call and its arguments, the reason behind each material decision, and the condition that triggered any escalation. Split the responsibility: the system prompt makes the model state its reasoning inline (a reasoning field or a short rationale) *before* each tool call; the orchestration harness records the mechanical trace (raw tool responses, token counts, timings) automatically. Do not make the agent call a logging tool for what the harness already sees — that burns turns and tokens. An agent cannot be debugged in production from its final output alone; the run transcript has to exist before a failure needs it.

#### Contract Document Format
```markdown
### Agent Contract
- **Task:** [one sentence]
- **Success Criteria:** [observable conditions]
- **Non-Goals:** [explicit prohibitions]
- **Escalation:** [what to do on failure or out-of-scope requests]
- **Altitude:** [heuristics/principles (high) vs. step-by-step procedure (low)]
- **Instrumentation:** [reasoning the model must state before a tool call; the trace the harness records]
```
Keep the contract visible to the model in the system prompt — it is the reference the agent returns to between tool calls.

### Stage 2: Context Budget and Curation
Treat the context window as a finite resource with diminishing marginal returns. Models lose recall precision as token count rises, so every token must justify its place.

- **Always-Load:** Instructions, tool definitions, and the contract belong in the system prompt. Keep this set minimal — the smallest set that fully outlines expected behavior.
- **Cache-Stable Prefix:** Place the always-load block at the very start of the token payload and keep it byte-identical between turns so the provider's prompt cache hits on it. Nothing volatile — timestamps, turn counters, freshly retrieved data, a changing tool list — may appear before it. Prefix caching is the largest single cost and latency lever for a tool-loop agent, and it is a layout decision, not a runtime one.
- **Just-In-Time:** Repositories, documents, records, and large data sets should be referenced by lightweight identifiers (file paths, stored queries, web links) and loaded through tools only when needed.
- **Progressive Disclosure:** Let the agent discover context incrementally — filenames, sizes, and timestamps hint at relevance; search tools load specifics. Do not dump exhaustive context up front.
- **Provenance Marking:** When retrieved context enters the prompt, wrap it in tagged sections that clearly distinguish facts from instructions and data from directives.
- **Drop Exhausted Context (harness-enforced):** Tool results that have been consumed should be cleared or summarized rather than retained. A prompt cannot prune its own history — specify this as a requirement the orchestration harness applies between turns; raw outputs deep in history rarely need to be seen again.
- **Cost Budget:** Set a cost budget and a latency target per run before choosing a model. A high-frequency agent that fires on every event needs a cheaper model, a tighter context, and a per-run token ceiling; a rare high-stakes agent can spend more. Curating tokens for recall accuracy is not the same as curating them for cost — state both targets so the trade-off is deliberate.

#### Context Component Table

| Component | Default Placement | Rationale |
|---|---|---|
| Contract, role, format rules | Always-load, cache-stable prefix | Stable behavior anchor; keeps the prompt cache warm |
| Tool schemas and descriptions | Always-load, cache-stable prefix | Opens the action space; changing it mid-session busts the cache |
| Repository, system files | Just-in-time via tools | Avoids bloat and staleness |
| Large data sets / logs | Just-in-time, truncated | Token efficiency |
| Retrieved documents | Tagged sections, after the prefix | Prevents instruction ambiguity; volatile, so never in the cached block |
| Message history | Compress as it ages (harness-enforced) | Fights context rot |
| Consumed tool outputs | Clear after use (harness-enforced) | Reclaims attention budget |

### Stage 3: System Prompt Structuring
Write the system prompt as clearly organized sections in simple, direct language.

- **Section the Prompt:** Separate background information, instructions, tool guidance, and output description. Use XML-style tags or Markdown headings so boundary confusion with local content is minimized.
- **Short Sentences, Explicit Verbs:** Prefer direct instruction ("Query the transactions table") over passive or hedged phrasing ("It would be good to consider checking..."). Write for a brilliant new employee who lacks your norms.
- **Order Steps Sequentially:** Numbered steps when order matters; independent steps stay unordered so the model can parallelize.
- **Give One Role:** A single role sentence focuses tone and behavior. Do not layer competing personas.
- **Provide Canonical Examples:** Include three to five diverse, canonical examples that portray expected behavior and edge handling. Do not pad the prompt with every conceivable edge case.
- **Guard Against Example Overfitting:** Use obviously abstract or dummy data in examples (`user_id: "U_1"`, `example.invalid` addresses), never values that look real enough to copy. State explicitly that examples show structure and reasoning, not literal strings to reproduce — models will otherwise paste example identifiers, names, and formatting into live output when the real input differs.
- **Specify the Output Contract:** State required fields, formats, and verbosity. Tell the model what "done" looks like in terms of the artifact it must produce.
- **Pin Determinism Where Output Must Be Stable:** If the agent emits a classification, a score, or any artifact that must match on re-run of the same input, pin the model version and set temperature = 0 (plus a seed where the API supports it) for that step. Name which steps are deterministic and which are free to vary. Reproducibility is a prompt-design decision, not a deployment afterthought.

#### Right Altitude Check
| Failure Mode | Symptom | Correction |
|---|---|---|
| Hardcoded brittle logic | Prompt breaks when inputs vary; long if-else chains | Raise altitude to principles and heuristics |
| Vague high-level guidance | Model guesses intent; inconsistent output | Lower altitude with concrete examples and constraints |
| Assumed shared context | Model invents conventions you never stated | State the convention explicitly |
| Laundry list of edge cases | Token bloat; model still misses novel cases | Replace with a few canonical examples |
| Example overfitting | Model copies mock identifiers, names, or formatting into live output | Use abstract dummy data; state that examples are structural, not literal |

### Stage 4: Tool Contract Engineering
Tools define the contract between the deterministic system and the non-deterministic agent. Design them like an API for an intelligent user who must choose among them.

- **Minimal Viable Set:** Provide the smallest set of tools that covers the task. If a human engineer cannot definitively say which tool to use in a given situation, an agent cannot either.
- **Distinct Purpose per Tool:** Each tool must have one clear purpose with minimal overlap. Consolidate tools that are frequently chained.
- **No Namespacing Overlap:** Name tools so related groups are apparent (service prefix, resource suffix). Ambiguous or overlapping names cause wrong tool selection.
- **Descriptive, Unambiguous Parameters:** Name parameters for what they identify (`user_id`, not `user`). Describe inputs as you would to a new hire.
- **Meaningful Identifiers in Returns:** Return human-readable names and values, not raw UUIDs, when the agent must reason about them.
- **Token-Efficient Responses:** Return filtered, paginated, or truncated results with sensible defaults. Favor "search" tools over "list everything" tools.
- **Actionable Error Messages:** On failure, return messages that say what went wrong and how to fix the call, not opaque error codes.
- **Mark Dangerous Surface:** Document which tools have write or side-effecting capabilities so the agent can be instructed to treat them with care.
- **Declare Sequence Dependencies:** When a tool has an implicit prerequisite (check existence before read, search before fetch, create path before write), state it in the tool's description. Modern APIs issue tool calls in parallel; an undocumented ordering assumption fails the run when two dependent calls fire at once.

#### Tool Selection Matrix
| Signal | Strong Tool Set | Weak Tool Set |
|---|---|---|
| Count | Fewer, consolidated | Many, overlapping |
| Purpose | One clear job each | Wraps raw API endpoints |
| Naming | Namespaced, distinct | Generic, similar |
| Returns | Human-readable, filtered | Full tables, UUIDs |
| Errors | Actionable guidance | Opaque error codes |
| Surface | Side effects explicit | Implicit write access |
| Parallelism | Sequence dependencies documented in schemas | Implicit ordering assumptions |

### Stage 5: Stop Conditions and Escalation
An agent run must terminate on explicit conditions, not on model fatigue or a vague sense of completion.

- **Success Condition:** Restate the success criteria from the contract as a checkable condition. The run ends when the condition verifies true. Where a wrapper application must detect completion, signal it with a dedicated exit tool call or a structured payload, not a plain-text sentence — free-text termination is unreliable to parse.
- **Failure Condition:** Define what counts as unrecoverable failure — repeated tool errors, a contract violation, or an out-of-scope request. End the run and escalate instead of retrying forever. Route the escalation through a named tool or exit state so the framework can intercept it cleanly.
- **Retry Class (harness-enforced):** Separate transient failures (timeouts, 5xx, rate limits) from terminal ones (invalid arguments, permission denied, not found). A prompt cannot implement backoff — specify it as harness logic: retry transient failures with capped exponential backoff and a maximum retry count; escalate terminal failures immediately with no retry. A blanket "retry N times" burns the budget on errors that will never succeed.
- **Budget Condition:** Set a maximum number of tool calls, turns, or a time budget. Terminate when exceeded and report partial progress.
- **Stagnation Detection:** If a step produces no new information or repeats an action without progress, stop and escalate rather than looping.
- **Ask-When-Blocked:** If a missing decision would materially change the outcome, ask the user instead of guessing and proceeding.

#### Stop Condition Table
| Condition | Trigger | Action |
|---|---|---|
| Success | Success criteria verified by evidence | Deliver result via exit tool / structured signal, summarize what was done |
| Retryable error | Transient tool failure (timeout, 5xx, rate limit) | Backoff and retry up to the cap, then treat as Failure |
| Failure | Terminal error (invalid args, permission denied) or contract violation | Stop, escalate through a named tool / exit state, report remaining options |
| Budget | Turn/call/time limit exceeded | Stop, report partial progress |
| Stagnation | No progress across repeated attempts | Stop, escalate with observed state |

### Stage 6: Evaluation-Driven Iteration
Do not ship a prompt you have not measured. Iterate against a fixed evaluation, not vibes.

- **Baseline with the Best Model First:** Prototype the minimal prompt with the most capable model. Add structure only in response to measured failure modes.
- **Build a Fixed Task Set:** Collect dozens of prompts grounded in real workflows, including edge cases and adversarial inputs. Pair each with a verifiable expected outcome.
- **Measure Tool Behavior:** Track tool-call counts, mis-selections, error rates, and token consumption alongside task accuracy. Agents fail through wrong tools as often as wrong answers.
- **Hold Out a Test Set:** Improve on a training set, confirm on held-out tasks you did not tune against.
- **Read Transcripts, Not Just Scores:** Review raw tool-call transcripts and reasoning to find where the agent got confused — the omitted tool call often matters more than the reported one.
- **Iterate on the Highest-Leverage Component:** Tool descriptions and parameter names often move accuracy more than prose in the system prompt. Adjust one variable at a time.

### Stage 7: Anti-Patterns and Prohibitions
- **No prompt-as-programming:** Do not hardcode brittle branching logic into the system prompt.
- **No bloated tool sets:** Do not ship tools that wrap every endpoint or overlap each other.
- **No silent context accumulation:** Do not let consumed tool outputs and old history pile up until context rot degrades behavior.
- **No premature completion:** Never declare success without verifying the success condition against evidence.
- **No infinite retry loops:** Never retry a failing action indefinitely; respect failure and budget conditions.
- **No guessing past authority:** Do not proceed on a material decision the agent should ask about, and never bypass the escalation path.
- **No unmarked retrieved content:** Never inject fetched or retrieved data into the prompt without tagging it as data rather than instruction.
- **No unmeasured claims:** Do not claim a prompt is improved without results from the fixed evaluation.
- **No unobservable runs:** Never ship an agent that cannot emit a trace of its tool calls and decisions. A failure you cannot replay is a failure you cannot fix.
- **No blind retries:** Do not retry a terminal error (invalid arguments, permission denied). Retry only transient failures, with a cap.

## Worked Examples

### Example 1: Support agent system prompt
- **Input:** A team wants an agent that resolves tier-1 support tickets from a help center.
- **Action:** Contract written with task ("resolve tier-1 tickets from the help center"), success criteria ("user question answered from a tagged article, or escalated"), non-goals ("no refunds, no account changes"), escalation ("request a human agent"), and altitude (principles, not per-ticket rules). Context: article catalog loaded just-in-time via a search tool. Prompt sections: background, instructions, tool guidance, output format. Tools kept to three: search_articles, get_article, escalate_to_human.
- **Verification:** Success condition checked after each answer — did the response cite a searched article, and is it outside the refund/account boundary?

### Example 2: Preventing tool mis-selection
- **Input:** An agent with `read_file`, `read_logs`, and `search_logs` tools starts calling `read_logs` on a huge file and stalling the run.
- **Action:** The tool contract is the failure — overlapping purpose and no size guard. Consolidate to `search_logs` (filtered, paginated) and `read_file` (with a max-bytes default), rename to make the boundary explicit, and add an error message that suggests filters when a query matches too much.
- **Verification:** Re-run the task; the agent now calls `search_logs` first and only opens specific slices of files.

### Example 3: Long-running coding agent harness
- **Input:** An agent asked to build an application across many sessions keeps one-shotting the work and declaring victory early.
- **Action:** Split the prompt into an initializer session (scaffold the repository, write a feature list file with pass/fail status per feature, make an initial commit) and coding sessions (read progress notes, pick one feature, implement, verify end-to-end like a human user would, commit, update progress). Add a budget and success condition per session.
- **Verification:** Each session terminates with a committed, tested increment and an updated progress file; no feature is marked done without end-to-end verification.

### Example 4: Retro-fitting a brittle prompt
- **Input:** An existing system prompt hardcodes ten delivery-specific conditions and still mishandles anything slightly novel.
- **Action:** Rewrite to altitude — replace the if-else chain with the contract, two to three canonical examples, and a stop condition that escalates novel cases. Keep the hardened cases as tests, not as prompt text.
- **Verification:** Run the original and new prompts against the same inputs; the new prompt passes the old cases and degrades to a clarifying question or escalation on novel ones instead of a confident wrong answer.
