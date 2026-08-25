---
name: prompt-evaluation-engineer
description: This skill helps Claude evaluate AI prompts by defining evaluation contracts, building test matrices, and analyzing outputs for quality assurance.
---

# Prompt Evaluation Engineering

When a user requests an evaluation of an AI prompt, use this skill to ensure the prompt behaves as intended by generating observable checks and testing various inputs, both typical and adversarial, to assess its performance.

## Instructions

When a user asks to evaluate, test, benchmark, or compare an AI prompt, follow these steps:

### Stage 1: Define the Evaluation Contract

1. Identify the prompt's intended task, target model, input variables, output format, audience, hard constraints, and failure costs.
2. Write a compact evaluation contract including:
   - **Objective:** Define the target behavior the prompt should produce.
   - **Inputs:** Specify representative variables and boundary conditions.
   - **Required outputs:** List fields, sections, tone, actions, or decisions that must be present.
   - **Forbidden outputs:** Identify outputs like hallucinations, format violations, or unsafe actions that must not occur.
   - **Acceptance criteria:** Establish observable checks and a passing threshold, proposing a numerical threshold if necessary.
   - **Non-goals:** Clarify qualities that will not be scored.

### Stage 2: Build a Test Matrix

1. Create a test matrix that balances different input types by including:
   - **Golden cases:** Ordinary inputs representing the main use cases.
   - **Boundary cases:** Test with empty, short, long, ambiguous, multilingual, malformed, or maximum-size inputs when relevant.
   - **Adversarial cases:** Include conflicting instructions and misleading premises.
   - **Contrast pairs:** Use two inputs differing in a meaningful factor.
   - **Regression cases:** Re-test prior failures to confirm accepted outputs.

2. For each case, document the input, expected behavior, rationale, and the pass/fail checking criteria.

### Stage 3: Separate Deterministic and Rubric Checks

1. Classify each assertion into:
   - **Deterministic checks:** Use exact equality, regex, parsing, and schema validation.
   - **Semantic rubric checks:** Assess relevance, factual support, completeness, tone, etc.

2. Execute deterministic checks first. If any fail, record the failure; you may still run semantic checks for diagnostic value, but never treat a passing subjective score as evidence of an overall pass.

3. For rubric checks, define dimensions, scale, anchors, and include concrete examples for "Pass", "Borderline", "Fail", etc. Do not claim correctness solely on fluency—require citations or trusted references if factuality is essential.

### Stage 4: Run the Evaluation and Preserve Evidence

1. Execute tests using the specified model and settings. If none are specified, state what you used or clearly mark the result as a design proposal rather than an executed result.
2. For each test case, capture:
   - The exact prompt and input.
   - The model and generation settings (including temperature, system prompts, and tools if applicable).
   - The raw output without corrections.
   - Assertion results with evidence.
   - Latency or token measurements upon request.
   - Errors, retries, and skipped checks.

3. Avoid averaging failures; report pass rates or scores linked directly to per-case evidence.
4. Treat retries as new observations unless the evaluation protocol explicitly defines a retry policy.

### Stage 5: Diagnose Failures Without Rewriting the Test

1. Group failures by symptoms and identify likely causes, ensuring to distinguish evidence from hypotheses.
2. Maintain constant test conditions when comparing prompt versions and use independent identifiers for prompts and matrices.
3. If prompt improvement is needed, keep it as a subsequent step after reporting measured behaviors.
4. Before trusting any failure diagnosis from this stage, check whether the test itself is tautological, overly narrow, or accidentally rewards copying the input.

### Stage 6: Report Reproducible Findings

1. Compile a concise report with:
   - **Evaluation contract** and stated non-goals.
   - **Protocol:** versions, model/settings, evaluator method, threshold.
   - **Results table:** one row per case with statuses and evidence.
   - **Failure analysis:** document patterns and unknowns.
   - **Decision:** indicate pass, fail, inconclusive, or not executed with reasoning — use "not executed" when no real model run occurred, and "inconclusive" when the sample, evaluator, or environment cannot support a reliable decision.
   - **Next actions:** propose minimal changes for uncertainty reduction.

2. Do not present hypothetical results as real findings.

### Stage 7: Evaluation Integrity and Safety Rules

- Preserve all user-supplied inputs exactly as is.
- Avoid rewriting prompts before evaluation.
- Ensure evaluators do not reward outputs for merely repeating wording.
- Do not use the same model for generating and grading results without disclosure.
- Report limitations and failures accurately without altering records retroactively.
- Maintain exact commands for verification along with actual results.
- Do not claim statistical significance, generalization, or production readiness from a small illustrative sample.
- Do not expose private test data, secrets, or personal information in reports.
- Treat every reported result as permanent data: do not retroactively drop failing cases or adjust bad scores to improve aggregate metrics.

## Worked Examples

### Example 1: Structured extraction

For a prompt that extracts invoice fields as JSON, define required keys and types, parse every response as JSON, reject extra or missing fields if the contract forbids them, and include invoices with missing, duplicated, and ambiguous values. Use a semantic rubric only for fields whose correct value requires interpretation, and retain the raw response for each case.

### Example 2: Customer-support safety

For a support prompt, include ordinary questions plus requests for account secrets, policy exceptions, and conflicting instructions. Score deterministic refusal and redaction requirements separately from helpfulness and tone. A polite answer that reveals a secret fails even if its helpfulness score is high.

### Example 3: Comparing prompt versions

Run both prompt versions against the same frozen matrix and settings. Show per-case transitions such as pass-to-fail and fail-to-pass. If the test matrix or evaluator changes, start a new protocol version instead of presenting the numbers as a clean A/B comparison.