---
name: "prompt-complexity-triage"
description: "Triages how much change a prompt actually needs before rewriting it, then applies only the moves for that tier. Use when a user asks to improve, optimize, clean up, or rewrite a prompt and you must avoid both over-editing a good prompt and under-editing a broken one."
---

# Prompt Complexity Triage and Right-Sized Optimization

When a user asks an AI assistant to improve, optimize, refine, clean up, or rewrite a prompt, the assistant must first triage how much change the prompt actually needs, then apply only the optimization moves permitted for that tier. The goal is to prevent two opposite failures: **over-editing**, where an already-adequate prompt is rewritten and its meaning drifts, and **under-editing**, where a vague or high-stakes prompt gets a cosmetic pass and still fails downstream. Every run must end with a visible score, an assigned tier, and a change note the user can audit.

## Instructions

### Stage 1: Intake and Scope Lock
Before scoring, capture what is being optimized and any ceiling the user has set.

- **Capture the prompt verbatim.** Do not paraphrase it into your working notes. The original text is the reference for every later preservation check.
- **Identify the consumer.** State whether the prompt targets an LLM chat turn, an autonomous agent, an image or video model, a code interpreter, a structured-output/data extraction step, or a human reader. The consumer sets the baseline for what "complete" and "structured" mean, and Stage 2 scores D1 and D3 against that baseline — a structured-output/data-extraction or code-interpreter consumer expects an explicit schema, field list, or step order (its absence raises D3, and an under-specified field set raises D1); a chat turn or human reader does not.
- **Record the user's stated ceiling.** If the user said "just fix the grammar", "only tighten it", "don't change the meaning", or similar, that is an explicit ceiling. An explicit ceiling caps the tier downward (see Stage 3). It never raises the tier. If the user gave no ceiling, note "none stated".
- **Degenerate-input bypass.** If the prompt to optimize is empty or is three words or fewer (e.g. `write`, `fix this`, `make it better`), there is nothing to score. Do not run Stage 2. Either ask the user for the actual prompt and what it should accomplish, or, if the user's surrounding message makes the goal clear, treat it as Tier 3 (Full Rebuild) and build the prompt from that goal. On this path, do not emit the standard five-dimension triage line — emit the bypass triage line defined in Stage 6 instead, and state which of the two routes (ask / rebuild) you took.

### Stage 2: Complexity Scoring
The dimensions and thresholds in this stage and the next are fixed, so the same prompt lands on the same tier regardless of who runs the triage. Scoring is done in context from the prompt text alone — no external service, trained router, or model-scoring call.

First restate the target consumer from Stage 1; it is the baseline against which D1 and D3 are scored. Then score the five scoring dimensions D1–D5 from 0 to 2 using the anchor table below. Sum D1 through D5 for a total of 0 to 10. A separate risk dimension, R1 (technical-parameter density), is assessed here but is **not** part of the sum — it feeds the caps in Stage 3 and the guardrails in Stage 4. Keep the scoring dimensions numbered strictly D1, D2, D3, D4, D5 with no gap; the risk dimension has its own `R` namespace so it is never mistaken for a sixth scored item.

#### Dimension Anchor Table
| Dimension | Score 0 | Score 1 | Score 2 |
|---|---|---|---|
| **D1 — Specification completeness** | Task, deliverable, and what "done" means are all stated to the level the target consumer needs | One of task / deliverable / done-condition is missing or vague for that consumer | Two or more are missing; the assistant would have to guess the consumer's goal |
| **D2 — Ambiguity** | One reasonable reading | Two plausible readings that lead to similar output | Multiple readings that lead to materially different output |
| **D3 — Structural need** | The target consumer needs no explicit structure, or the structure it needs is already present | The consumer expects a format, schema, or step order and it is only implied | The consumer cannot execute without an explicit schema, field list, or ordered procedure and it is absent |
| **D4 — Reasoning depth** | Single-step request | Multi-step but linear; no branching | Conditional or multi-path logic the prompt itself must carry (if X do Y, else Z) |
| **D5 — Stakes** | A wrong output costs a few seconds to redo | A wrong output wastes real work or is mildly embarrassing | A wrong output costs money, breaks something, or damages trust and is hard to reverse |

#### Risk Dimension (not part of the sum)
| Dimension | Low (0) | Medium (1) | High (2) |
|---|---|---|---|
| **R1 — Technical-parameter density** | No code, flags, versions, IDs, or paths | A few literal tokens that must survive verbatim | Dense with code fences, flags, version pins, model IDs, regexes, or file paths |

R1 measures **edit risk**, not need for rewriting. A prompt dense with literal tokens is *more* dangerous to rewrite, not more in need of it. It is handled as a tier cap in Stage 3, never as a reason to escalate.

Record the result as: `D1 a, D2 b, D3 c, D4 d, D5 e -> total N/10; R1 = f (risk)`.

### Stage 3: Tier Assignment
Map the total to a tier using these fixed thresholds, then apply the caps.

| Total | Tier | Name | What is allowed |
|---|---|---|---|
| 0–1 | Tier 0 | LEAVE AS-IS | Report the score. State the prompt is adequate. Offer at most one optional one-line suggestion. Do not produce a rewritten prompt. |
| 2–4 | Tier 1 | LIGHT TOUCH | Fix grammar and spelling, remove dead words, make verbs direct, format the existing ask for readability. No new sections, no structural scaffolding, no added persona or tone, no examples, no reordering of meaning-bearing content. |
| 5–7 | Tier 2 | STRUCTURED REWRITE | Make the output contract explicit, tighten instructions, name constraints the user implied, add one to three canonical examples only where they remove ambiguity. Preserve all technical parameters verbatim. Do not invent requirements. |
| 8–10 | Tier 3 | FULL REBUILD | Build a contract (task, success criteria, non-goals), assign one role, use structured sections, add canonical examples, specify the output format, list anti-patterns. Preserve all technical parameters verbatim. Confirm intent with the user first if the rebuild would change the prompt's scope. |

#### Caps (applied after the threshold lookup, lowest wins)
- **User ceiling cap:** If the user set an explicit ceiling in Stage 1 (e.g. "just fix typos"), cap at Tier 1. Do not exceed it. Note in the change note that deeper issues exist but were out of scope.
- **Technical-density cap:** If `R1 = 2`, cap at Tier 2 unless the user explicitly asked for a full rewrite or rebuild. A token-dense prompt should not be rebuilt from scratch on the assistant's initiative.
- Caps only ever lower the tier. Nothing in this procedure raises a tier above its threshold result.

### Stage 4: Meaning-Preservation Guardrails
These apply to every tier above Tier 0.

- **Copy verbatim, character for character:** code fences and their contents, inline code, exact numbers, version strings, CLI flags, file paths, model IDs, proper nouns, error messages and stack traces, URLs, email addresses.
- **Do not drop or reword:** stated constraints, negative constraints ("do not…", "never…", "without…"), schema field names and types, required ordering of steps.
- **Do not add:** factual claims the user did not supply, functional requirements or constraints the user did not state, a persona or tone the user did not ask for, success metrics or confidence numbers.
- **Structural scaffolding is expected for Tier 2 and Tier 3, and prohibited for Tier 1.** Section headings, Markdown organization, a stated output format, a schema skeleton, numbered steps, and clarity rephrasing are expected work for a structured rewrite or rebuild and do **not** count as "adding requirements", as long as they only organize what the user already asked for and introduce no new functional demand or fact. A Tier 1 light touch adds none of this. If scaffolding in Tier 2/3 would force a decision the user has not made (a specific field, a specific limit, a specific tone), leave a placeholder and name it in the change note rather than inventing the value.
- **If a literal token looks wrong** (a flag that seems malformed, a version that looks off): leave it exactly as written and flag it in the change note. A value that looks wrong to you may be exactly what the target system requires.

### Stage 5: Change Budget Enforcement and Preservation Check
Bound the size of the edit to the tier, then verify preservation before formatting the output.

- **Tier 1:** Changed text stays roughly within 15% of the prompt. No sentence changes meaning. If a fix would alter meaning, stop and report it instead of applying it.
- **Tier 2:** Structure may be added, but every requirement present in the original must still be traceable to a specific line in the output.
- **Tier 3:** Produce a requirement map, formatted as a Markdown table, one row per requirement, with columns `Original requirement | Location in rewrite`. For a **degenerate-input rebuild** (Stage 2 was bypassed and the prompt was built from a stated goal), there is no original prompt text to mine — instead take each requirement from the goal expressed in the user's surrounding message and title the first column `Stated goal requirement`. Either way, any requirement with no destination in the rewrite is a regression: stop and resolve it before returning the rewrite.
- **Preservation check (all tiers above Tier 0, mandatory before Stage 6):** Compare the drafted prompt against the verbatim text captured in Stage 1. Confirm that every item on the Stage 4 verbatim list — code, inline code, numbers, version strings, CLI flags, file paths, model IDs, proper nouns, error messages, URLs, email addresses — and every negative constraint and required step order is present unchanged.
  - *Degenerate-input rebuild:* there is no Stage 1 verbatim text to compare against. Instead, compare the draft against the technical parameters, proper nouns, named tools, versions, and explicit constraints found in the user's surrounding message, and confirm each one survived into the rebuilt prompt unchanged.
  - If anything is missing, altered, or reworded, fix it before producing output; do not emit a rewrite that fails this check.

### Stage 6: Output Contract
Return the result in this order.

1. **Triage line** — exactly one of these forms, always present:
   - *Scored path:* `Triage: D1 a, D2 b, D3 c, D4 d, D5 e = N/10; R1 = f -> Tier T (name)`. If a cap changed the tier, append which cap fired and what the pre-cap tier was.
   - *Degenerate-input bypass path:* `Triage: degenerate input (<=3 words), no score -> asked for the full prompt` or `Triage: degenerate input (<=3 words), no score -> Tier 3 (Full Rebuild) from stated goal`. Never fabricate dimension scores to fill the scored form on this path.
2. **The prompt:** For Tier 0, state that no rewrite is provided. For Tier 1–3, the prompt in a fenced code block.
3. **Change note** — form depends on the tier:
   - *Tier 0, or the degenerate-input "asked for the full prompt" route:* write `N/A — no rewrite produced`. Do not invent a change or emit an empty section.
   - *Tier 1–2:* what changed, why, which technical elements were preserved verbatim, and an explicit list of any placeholders left in for decisions the user has not made (write "placeholders: none" if there are none).
   - *Tier 3 (including a degenerate-input rebuild):* what changed, why, the preserved technical elements, an explicit list of any placeholders left in (write "placeholders: none" if there are none), and the Markdown requirement-map table from Stage 5.
4. **Disclosure:** State plainly that this was a heuristic triage pass, that no confidence score is implied, and that the prompt did not go through a trained model or a full LLM-based optimization pipeline.

### Stage 7: Anti-Patterns and Prohibitions
- **No tier inflation:** Never rebuild or heavily restructure a prompt whose score does not reach that tier because the result "looks more professional".
- **No silent meaning change:** Never reword a requirement while claiming to only improve clarity.
- **No dropped constraints:** Removing a negative constraint is a regression, not a simplification.
- **No unrequested persona or tone:** Do not assign the AI a character the user did not ask for.
- **No fabricated metrics:** Do not attach an accuracy figure, a confidence score, or a benchmark claim to the output.
- **No exceeding the user's ceiling:** If the user limited the scope, do not go past it without asking first.
- **No skipping the triage line:** Every run shows a triage line — the scored form for a scored run (including Tier 0), or the bypass form for the degenerate-input path. Never omit it, and never fill the scored form with fabricated dimension scores on the bypass path.

## Worked Examples

### Example 1: Adequate prompt, left alone
- **Input:** "Summarize the attached RFC in 5 bullet points, each under 20 words, focused on the wire-format changes." Consumer: LLM chat. No ceiling stated.
- **Scoring:** D1 0 (task, deliverable, done-condition all present), D2 0, D3 0 (format already specified), D4 0, D5 1. Total 1/10. R1 0.
- **Action:** Tier 0. Report the score, state the prompt is adequate, optionally note "you could name the RFC number to disambiguate if there are several." No rewritten prompt returned.

### Example 2: Vague high-stakes prompt, full rebuild
- **Input:** "Write the incident postmortem." Consumer: human reader. No ceiling stated.
- **Scoring:** D1 2 (no incident named, no format, no audience), D2 2, D3 2 (a postmortem needs a fixed section structure that is absent), D4 1, D5 2 (a bad postmortem misleads a team). Total 9/10. R1 0.
- **Action:** Tier 3. Because the rebuild changes scope, confirm with the user which incident and audience first, then build a contract, a section structure (summary, timeline, root cause, impact, action items), an output format, and a requirement map.

### Example 3: User ceiling caps the tier
- **Input:** A prompt that scores 7/10 on the dimensions, but the user said "just fix the wording, don't restructure it."
- **Action:** Threshold lookup gives Tier 2. The user-ceiling cap lowers it to Tier 1. Apply grammar and directness fixes only. In the change note, state that the prompt also lacks an explicit output format and has two plausible readings, but those were left untouched per the requested scope.

### Example 4: Token-dense prompt, density cap
- **Input:** "Improve this: `Generate a GitHub Actions workflow that runs pytest on push to main, uses actions/setup-python@v5 with python-version 3.11, and fails if coverage < 85% via --cov-fail-under=85`." Consumer: code interpreter. No ceiling stated.
- **Scoring:** D1 1, D2 1, D3 1, D4 1, D5 1. Total 5/10 → Tier 2. R1 2 (dense with action versions, flags, a threshold).
- **Action:** Density cap holds the tier at Tier 2 (already there; a rebuild would not be allowed without the user asking). Apply the structured rewrite, and copy `actions/setup-python@v5`, `python-version 3.11`, `--cov-fail-under=85`, and `< 85%` verbatim. If any token looks malformed, leave it and flag it rather than correcting it.
