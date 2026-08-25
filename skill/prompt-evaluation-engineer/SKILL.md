---
name: prompt-evaluation-engineer
description: This skill enables Claude to evaluate AI prompts systematically, ensuring adherence to expected behaviors and quality standards through structured testing.
---

# Prompt Evaluation Engineering

Use this skill when a user requests evaluation, testing, benchmarking, comparison, or regression-checking of an AI prompt. It helps Claude to treat the prompt as a behavior contract and systematically validate its performance against predefined criteria.

## Instructions

When a user asks to evaluate a prompt, follow these steps:

### Stage 1: Define the Evaluation Contract

1. Identify the prompt's intended task, target model or tool if named, input variables, output format, audience, hard constraints, and failure costs.
2. Ask for the smallest missing detail only when it changes the evaluation design materially.
3. State what is in scope and out of scope.
4. Write a compact evaluation contract including:
   - **Objective:** the behavior the prompt is meant to produce.
   - **Inputs:** representative variables and boundary conditions.
   - **Required outputs:** fields, sections, tone, actions, or decisions that must be present.
   - **Forbidden outputs:** hallucinations, leaked private data, unsupported claims, format violations, unsafe actions, or other explicit failures.
   - **Acceptance criteria:** observable checks and the threshold for passing.
   - **Non-goals:** qualities that will not be scored in this evaluation.
5. If the user has not supplied a numerical threshold, do not invent one, but recommend it as a proposal.

### Stage 2: Build a Test Matrix

1. Create a small, balanced matrix that includes:
   - **Golden cases:** ordinary inputs that represent the main use case.
   - **Boundary cases:** empty, short, long, ambiguous, multilingual, malformed, or maximum-size inputs as relevant.
   - **Adversarial cases:** conflicting instructions, prompt injection attempts, misleading premises, missing context, and requests designed to trigger known failure modes.
   - **Contrast pairs:** inputs that differ in one meaningful factor, clarifying expected behavioral differences.
   - **Regression cases:** prior failures or previously accepted outputs, preserved exactly when the user provides them.
2. For each case, record the input, expected behavior, rationale, and the check that will determine pass or fail.
3. Keep the matrix small enough to run repeatedly and explain any omitted categories.

### Stage 3: Separate Deterministic and Rubric Checks

1. Classify each assertion before judging an output as either:
   - **Deterministic checks:** exact equality, required substring, forbidden substring, regular expression, JSON/YAML parsing, schema validation, field types, enumerated values, length bounds, citation presence, or latency.
   - **Semantic rubric checks:** relevance, factual support, completeness, usefulness, tone, instruction following, or resistance to adversarial input.
2. Run cheap deterministic checks first, and if one fails, record the failure without treating a later subjective score as evidence of a pass.
3. For rubric checks, define dimensions, scale, anchors, and concrete examples of passing, borderline, and failing responses for each dimension; a simple label like "Pass"/"Fail" isn't sufficient.
4. Never claim factual correctness based solely on fluency. Require citations or verification when factuality matters.
- When factuality matters, require citations, a trusted reference, a verifier, or an explicit limitation on what can be concluded.

### Stage 4: Run the Evaluation and Preserve Evidence

1. Use the target model and settings named by the user. If not specified, state the used model and settings or clearly mark the result as a design proposal.
2. Capture for each test case:
   - The exact prompt version and input.
   - The model and relevant generation settings.
   - The raw output without silently repairing it.
   - Each assertion result and its evidence.
   - Latency or token measurements when requested.
   - Errors, retries, and skipped checks.
3. Avoid averaging individual failures; include a summary linking back to per-case evidence.
- Keep temperature, seed, system instructions, tool availability, retrieval context, and other material parameters visible.
- Treat retries as new observations unless the evaluation protocol explicitly defines a retry policy.

### Stage 5: Diagnose Failures Without Rewriting the Test

1. Group failures by symptom and likely cause: prompt ambiguity, missing context, output-contract drift, model capability or variance, evaluator weakness, unsafe behavior, or harness/configuration error.
2. Report evidence independently from hypotheses. Check whether the test itself is narrowly defined or rewards input duplication.
3. When comparing prompt versions, hold the test matrix and evaluation settings constant. Assign independent version identifiers and report changes in cases from pass to fail or vice versa.
- If the user asks for a prompt improvement after evaluation, keep that as a separate next step.
- First report the measured behavior of the prompt that was actually tested.

### Stage 6: Report Reproducible Findings

1. Return a concise report containing:
   - **Evaluation contract** and declared non-goals.
   - **Protocol:** prompt version, test-set composition, model/settings, evaluator method, and threshold status.
   - **Results table:** one row per case with status, assertion summary, and evidence.
   - **Failure analysis:** patterns, confidence-limited hypotheses, and important unknowns.
   - **Decision:** pass, fail, inconclusive, or not executed, with the reason.
   - **Next actions:** the smallest changes required to reduce uncertainty.

2. Use "not executed" when no real model run occurred, and "inconclusive" when reliable decisions can't be drawn.
- Never present illustrative or hypothetical results as empirical findings.

### Stage 7: Evaluation Integrity and Safety Rules

- Preserve user-supplied prompts, code blocks, examples, URLs, model IDs, numbers, flags, and prior outputs exactly when they are test inputs or fixtures.
- Do not silently rewrite the prompt under test before evaluating it.
- Do not let an evaluator reward an output for merely repeating the input or assertion wording.
- Do not use a single model to generate and grade a result without disclosing that limitation; prefer independent or deterministic checks where possible.
- Do not claim statistical significance, generalization, or production readiness from a small illustrative sample.
- Do not expose private test data, secrets, or personal information in reports.
- Treat every reported result as permanent data; do not retroactively drop cases or scores from a report to improve aggregates.
- Report the exact verification command or execution method and its actual result when a runnable harness is involved.

## Worked Examples

### Example 1: Structured extraction

For a prompt that extracts invoice fields as JSON, define required keys and types, parse every response as JSON, reject extra or missing fields if the contract forbids them, and include invoices with missing, duplicated, and ambiguous values. Use a semantic rubric only for fields whose correct value requires interpretation, and retain the raw response for each case.

### Example 2: Customer-support safety

For a support prompt, include ordinary questions plus requests for account secrets, policy exceptions, and conflicting instructions. Score deterministic refusal and redaction requirements separately from helpfulness and tone. A polite answer that reveals a secret fails even if its helpfulness score is high.

### Example 3: Comparing prompt versions

Run both prompt versions against the same frozen matrix and settings. Show per-case transitions such as pass-to-fail and fail-to-pass. If the test matrix or evaluator changes, start a new protocol version instead of presenting the numbers as a clean A/B comparison.