---
name: prompt-evaluation-engineer
description: This skill helps Claude evaluate, benchmark, and report on AI prompts by establishing a structured evaluation framework.
---

# Prompt Evaluation Engineering

When a user requests to evaluate, test, benchmark, compare, or regression-check an AI prompt, use this skill to treat the prompt as a behavior contract. This skill assists in converting intended behaviors into observable checks without rewriting the prompt itself.

## Instructions

When a user asks to evaluate a prompt, follow these steps:

### Stage 1: Define the Evaluation Contract

- Help the user by identifying the intended task, target model or tool, input variables, output format, audience, hard constraints, and failure costs.
- Generate a compact evaluation contract with the following fields:
  - **Objective:** the behavior the prompt is meant to produce.
  - **Inputs:** representative variables and boundary conditions.
  - **Required outputs:** fields, sections, tone, actions, or decisions that must be present.
  - **Forbidden outputs:** include hallucinations, leaked private data, unsupported claims, format violations, unsafe actions, or other explicit failures.
  - **Acceptance criteria:** observable checks and the threshold for passing (recommend a threshold as a proposal if the user has not supplied one).
  - **Non-goals:** qualities that will not be scored in this evaluation.
- Ask for the smallest missing detail only when it changes the evaluation design materially.

### Stage 2: Build a Test Matrix

- Create a small, balanced test matrix including:
  - **Golden cases:** ordinary inputs representing the main use case.
  - **Boundary cases:** empty, short, long, ambiguous, multilingual, malformed, or maximum-size inputs as relevant.
  - **Adversarial cases:** conflicting instructions, prompt injection attempts, missing context, or requests designed to trigger known failure modes.
  - **Contrast pairs:** two inputs differing in one meaningful factor.
  - **Regression cases:** prior failures or previously accepted outputs, preserved exactly.
- For each case, record the input, expected behavior, rationale, and the check that determines pass or fail.
- Keep the matrix small enough to run repeatedly, and explain any omitted category.

### Stage 3: Separate Deterministic and Rubric Checks

- Classify each assertion as either:
  - **Deterministic checks:** exact equality, required substring, forbidden substring, regular expressions, JSON/YAML parsing, schema validation, field types, enumerated values, length bounds, citation presence, or latency.
  - **Semantic rubric checks:** relevance, factual support, completeness, usefulness, tone, instruction following, or resistance to adversarial input.
- Run deterministic checks first. If one fails, record the failure and do not treat a later subjective score as evidence of passing. Define dimensions and anchors for rubric checks.
- Do not hide a subjective judgment behind an unexplained aggregate score.
- Never claim that an output is factually correct merely because it is fluent.
- When factuality matters, require citations, a trusted reference, a verifier, or an explicit limitation on what can be concluded.

### Stage 4: Run the Evaluation and Preserve Evidence

- Use the target model and settings named by the user. If not provided, state the model and settings used or mark the result as a design proposal.
- For each test case, capture:
  - The exact prompt version and input,
  - The model and relevant generation settings,
  - The raw output without alterations,
  - Each assertion result and its evidence,
  - Latency or token measurements when requested,
  - Errors, retries, and skipped checks.
- Include pass rates or scores in a summary, linking back to per-case evidence.
- Keep temperature, seed, system instructions, tool availability, retrieval context, and other material parameters visible.
- Treat retries as new observations unless the evaluation protocol explicitly defines a retry policy.

### Stage 5: Diagnose Failures Without Rewriting the Test

- Group failures by symptom and likely cause: prompt ambiguity, output-contract drift, or evaluator weakness.
- Hold the test matrix and evaluation settings constant when comparing prompt versions.
- Record changes in case results and do not alter acceptance criteria after observing results without versioning the protocol.
- Check whether the test itself is tautological, overly narrow, or accidentally rewards copying the input.
- Report which cases changed from pass to fail, which improved, and which were unaffected.
- Do not delete difficult cases, loosen assertions, or change the test set after seeing results without recording the protocol change and labeling the comparison invalid.
- First report the measured behavior of the prompt that was actually tested.

### Stage 6: Report Reproducible Findings

- Return a concise report containing:
  1. **Evaluation contract** and declared non-goals.
  2. **Protocol:** prompt version, test-set composition, model/settings, evaluator method, and threshold status.
  3. **Results table:** one row per case with status, assertion summary, and evidence.
  4. **Failure analysis:** patterns, confidence-limited hypotheses, and important unknowns.
  5. **Decision:** pass, fail, inconclusive, or not executed, with the reason.
  6. **Next actions:** suggestions for the smallest changes to reduce uncertainty.
- Never present illustrative or hypothetical results as empirical findings.

### Stage 7: Evaluation Integrity and Safety Rules

- Preserve user-supplied prompts, code blocks, examples, and prior outputs as they are.
- Do not quietly rewrite the prompt under test.
- Avoid rewarding outputs merely for repeating input.
- Use independent checks; do not rely on a single model for generation and grading without disclosing this.
- Do not claim statistical significance from small samples.
- Maintain privacy and integrity in reporting findings.
- Report the exact verification command and its results when applicable.
- Do not expose private test data, secrets, or personal information in reports.
- Do not delete failures, skip adversarial cases, or alter acceptance criteria after observing results without versioning the protocol.

## Worked Examples

### Example 1: Structured extraction

For a prompt that extracts invoice fields as JSON, define required keys and types, parse every response as JSON, reject extra or missing fields if the contract forbids them, and include invoices with missing, duplicated, and ambiguous values. Use a semantic rubric only for fields whose correct value requires interpretation and retain the raw response for each case.

### Example 2: Customer-support safety

For a support prompt, include ordinary questions plus requests for account secrets, policy exceptions, and conflicting instructions. Score deterministic refusal and redaction requirements separately from helpfulness and tone. A polite answer that reveals a secret fails even if its helpfulness score is high.

### Example 3: Comparing prompt versions

Run both prompt versions against the same frozen matrix and settings. Show per-case transitions such as pass-to-fail and fail-to-pass. If the test matrix or evaluator changes, start a new protocol version instead of presenting the numbers as a clean A/B comparison.