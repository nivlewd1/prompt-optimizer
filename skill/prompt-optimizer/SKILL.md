---
name: prompt-optimizer
description: This skill helps Claude optimize user prompts for clarity, technical accuracy, and effectiveness before sending them to an AI system.
---

# Optimize User Prompts for AI Systems

Use this skill whenever a user requests assistance in improving, optimizing, refining, or rewriting a prompt intended for an AI system, such as an LLM, image generator, or human collaborator. The goal is to ensure the prompt is clear, technically accurate, and effective.

## Instructions

When a user asks to optimize a prompt, follow these steps:

1. **Classify the AI Context**  
   Read the prompt and identify its primary context using these signals (not exhaustive — use judgment on prompts that don't cleanly match):
   - **Code Generation** — mentions a programming language, function/class/algorithm names, code fences, error messages, stack traces, "debug", "implement", "refactor", "write a function that...".
   - **Image Generation** — mentions aspect ratios (16:9, 1:1), rendering terms (photorealistic, 3D render, octane, unreal engine), generator flags (`--ar`, `--v`, `--style`), or "create/generate an image/photo/illustration/logo of...".
   - **Structured Output** — asks for JSON, YAML, CSV, a schema, or a specific machine-readable format as the deliverable.
   - **Human Communication** — asks for an email, letter, memo, message, or explicitly names a tone (formal/informal/professional), a greeting, or a recipient ("write an email to my manager about...").
   - **Research & Analysis** — asks to analyze, summarize, compare, or investigate a topic, with an expectation of citations, structure, or actionable findings.
   - **Creative Enhancement** — asks for a story, narrative, poem, or other fictional/creative work; mentions genre, characters, plot, or "write a story about...".

   If a prompt matches multiple contexts, prioritize the primary context and retain relevant details from the secondary context.

2. **Assess Sophistication Level**  
   Evaluate how much the user knows and the existing structure of the prompt:
   - **Simple** — short, single-sentence ask, no constraints, no examples, vague verbs ("make this better", "write me a story").
   - **Intermediate** — some structure or constraints present (a rough format, a length, one or two specifics), but missing depth (no examples, no edge cases, no success criteria).
   - **Advanced** — clear constraints, explicit format, some examples or edge cases already named, but missing a persona/role framing or explicit failure modes to avoid.
   - **Expert** — already has role/persona framing, explicit constraints, examples, and anti-patterns to avoid. At this level, optimization means tightening and removing ambiguity, not adding structure the user hasn't asked for.

   Match the amount of new structure you add to the gap between the current level and the next level up. Don't turn a Simple prompt into an Expert one in a single pass if the user's own words suggest they want something short — ask, or default to Intermediate-level structure, when unsure.

3. **Apply Optimization Moves**  
   For the identified context, formulate the optimization using:
   - **Persona**: Define who the AI should act as.
   - **Instruction**: Specify what to produce.
   - **Principles**: Establish guardrails and quality standards.
   - **Anti-patterns**: Define what to avoid.  
   Use your judgment on how to construct these elements narratively rather than relying on fixed templates.

   **Code Generation** (mirrors this platform's `debugging_request` and `code_review_request` techniques):
   For a bare debugging request ("my code doesn't work, fix it"): persona is "an expert software engineer specializing in root cause analysis"; instruction is to think through potential causes step by step before answering; principle is to request the missing information a debugger actually needs (exact error message, relevant code snippet, expected vs. actual behavior); anti-pattern is don't guess at a fix without that information — ask for it first.
   For a code review request specifically: persona is "a senior software engineer conducting a thorough code review"; principles are identify bugs/security issues/performance problems, suggest specific fixes with code examples, acknowledge what's already good, and prioritize by severity; anti-pattern is never give vague feedback like "looks good" with nothing concrete underneath it.

   **Creative Enhancement** (mirrors this platform's `creative_story_comprehensive` technique):
   For a bare request ("write me a story"): persona is "a bestselling author and creative writing coach"; instruction is to build out genre, setting, and character arcs rather than just producing prose blind; principles cover narrative structure (plot, pacing, point of view) and literary elements (theme, dialogue, conflict). The goal is a **framework** the user can then fill in or hand off, not a finished short story guessed from three words.

   **Image Generation:** add explicit style/medium language (photorealistic vs. illustration vs. 3D render), composition detail (framing, lighting, camera angle if relevant), and — if the target tool supports them — the platform-specific flags (aspect ratio, style weight) the user's phrasing implies but didn't write out.

   **Human Communication:** add explicit tone (formal/informal), the relationship to the recipient if inferable, and a concrete structure (greeting, body, sign-off) — without inventing content the user didn't ask for.

   **Structured Output / Research & Analysis:** make the exact schema or report structure explicit rather than implied; state what "done" looks like (a specific set of fields, a specific comparison axis) so the downstream AI can't quietly under-deliver.

4. **Preserve Technical Parameters**  
   Before finalizing, scan the original prompt for anything in this list and copy it into the optimized version exactly, character for character:
   - Code fences and their contents (```...```) and inline code (`...`)
   - Exact numbers, versions, flags, and file paths (e.g. `--ar 16:9`, `v2.3.0`, `/api/v1/optimize`)
   - Model IDs and proper nouns (e.g. `gpt-4o-mini`, `claude-sonnet-5`)
   - Exact error messages and stack traces, verbatim
   - URLs and email addresses

   Never "improve" these by rephrasing, reformatting, or correcting what looks like a typo — a flag or path that looks wrong to you may be exactly what the target system requires. If something here is ambiguous, leave it untouched and flag the ambiguity in your closing note rather than guessing.

5. **Output the Results**  
   Generate the optimized output in the following format:
   - A line naming the classified context and sophistication level.
   - The optimized prompt clearly delimited in a code block or under a specified heading.
   - A brief note explaining what changed, why, and any preserved technical elements.
   - State plainly that this is a heuristic pass — do not claim a confidence score, and do not imply the prompt went through a trained model or this platform's full LLM-based optimization pipeline.

## Best Practices

- Always classify the context accurately to optimize effectively.
- Assess the means of sophistication carefully to match user expectations and knowledge.
- Keep focus on clarity and technicality while avoiding unnecessary complexity.
- When preserving technical parameters, be vigilant to ensure nothing is altered.

## Example Usage

When you assess a raw prompt:
```
User request: "Can you fix my code?"
Output: 
Classified context: Code Generation, Sophistication Level: Simple
```

Final optimized prompt:
```
You are an expert software engineer specializing in root cause analysis. 
Please provide the exact error message and the relevant code snippet. 
Explain the potential causes step-by-step before suggesting solutions.
```
Note: Adjusted clarity, added a persona and instructions, and preserved the technical parameters verbatim. This is a heuristic pass, not a run through the full optimization pipeline.