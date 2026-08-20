---
name: empirical-diagnostician
description: This skill helps Claude perform evidence-based debugging and empirical diagnosis to identify root causes of coding issues systematically.
---

# Empirical Diagnosis and Evidence-Based Debugging

When users request debugging assistance for software errors, test failures, crashes, or unexpected behaviors, utilize this skill to minimize trial-and-error adjustments and ensure evidence-backed conclusions before modifying any source files.

## Instructions

When a user asks to debug an error or investigate a problem, follow these steps:

### Stage 1: Mandatory Log and Traceback Extraction
- Extract the raw, un-truncated error log, stack trace, or terminal output.
- Capture exact error types, line numbers, variable states, and call stack frames verbatim.
- If the stack trace is incomplete, use the Bash tool to run the narrowest applicable diagnostic command to capture the necessary logs.
- Do not guess root causes based on directory structures or file names alone.

### Stage 2: Fast-Track Evaluation
- Evaluate defect complexity:
  - **Fast-Track Bypass:** If you identify an unambiguous single-token defect, record a minimal Fast-Track Decision including evidence, root cause, edit boundary, and verification command. Continue directly to Stage 6 (Root-Cause Contract). Do not use Fast-Track if the fix depends on runtime state, multiple files, external services, or unverified assumptions — continue to Stage 3 instead.
  - **Standard Track:** If the defect involves state or logic issues, multi-file execution, schema or contract mismatches, configuration problems, or unclear runtime crashes, proceed to Stage 3.

### Stage 3: Diagnostic Record and Fact Separation
- Publish a concise diagnostic record containing these four distinct sections:
  ```markdown
  ### Diagnostic Record
  - **User Facts:** Goals and constraints provided in the prompt.
  - **Repository Evidence:** Facts from local source files, manifests, and terminal logs.
  - **Inferences:** Deductions combining user facts with repository evidence.
  - **Unknowns:** Missing details required to verify the bug.
  ```
- Keep the record concise and update it when a probe changes the evidence. Do not treat inferences as definitive facts.

### Stage 4: Hypothesis Matrix Formulation
- Formulate a structured hypothesis matrix with at least two to three competing root-cause hypotheses categorized as follows:
  - **Category A (State / Logic Violation):** Incorrect variable mutation, race condition, or unhandled null state.
  - **Category B (Contract Drift):** Mismatch between caller arguments and recipient signatures, or schema changes.
  - **Category C (Environment / Config):** Missing environment variables, version mismatches, or dependency failures.
- For each hypothesis, document the expected log signature that would confirm or invalidate it.

### Stage 5: Minimal Non-Destructive Probes
- Execute minimal, read-only diagnostic probes to isolate the failing branch:
  - Run targeted single-test commands or targeted print/log assertions.
  - Evaluate probe outputs against the hypothesis matrix to eliminate false leads.
  - Do not treat a probe as proof unless its output distinguishes between the competing hypotheses.

### Stage 6: Root-Cause Contract and Verification
- Once the root cause is isolated, construct a concise task contract containing:
  ```markdown
  ### Root-Cause Contract
  - **Identified Root Cause:** The exact broken invariant in code.
  - **Minimal Edit Boundary:** Specific lines and functions to be modified.
  - **Verification Command:** Exact terminal command (e.g., pytest, npm test, cargo check) to confirm the fix.
  - **Non-Goals:** Explicit boundaries of what will not be modified.
  ```
- Use this contract to make the smallest justified edit, execute the specified verification command, and report its actual result.

### Stage 7: Anti-Patterns and Prohibitions
- Do not engage in symptom masking; avoid using generic try-catch blocks or returning dummy values to silence errors.
- Never delete or comment out existing test assertions to make tests pass.
- Do not declare a bug fixed without confirming clean execution through terminal output.
- Refrain from altering user-supplied stack traces, CLI flags, or file paths.

## Example Usage

### Example 1: Fast-Track syntax defect
- **Input:** A test run reports `SyntaxError` on one line.
- **Action:** Record a minimal Fast-Track Decision, make only the syntax edit, and run the narrowest relevant test or parser check.
- **Do not do:** Avoid Fast-Track if the failure could depend on runtime state, multiple files, an external service, or unverified assumptions.

### Example 2: Stateful failing test
- **Input:** A failing integration test shows an unexpected response with an unclear stack trace.
- **Action:** Publish the Diagnostic Record, build competing hypotheses, run a read-only probe to distinguish them, and write the Root-Cause Contract before making edits.
- **Verification:** Execute the specified test command and report its actual terminal output.

## Worked Examples

### Example 1: Fast-Track syntax defect
- **Input:** A test run reports `SyntaxError` on one line in one file, and the surrounding source makes the typo unambiguous.
- **Action:** Record a minimal Fast-Track Decision, make only the syntax edit, and run the narrowest relevant test or parser check.
- **Do not do:** Do not use Fast-Track if the failure could depend on runtime state, more than one file, an external service, or an assumption not confirmed by evidence.

### Example 2: Stateful failing test
- **Input:** A failing integration test shows an unexpected response, but the stack trace does not identify whether the cause is state, contract drift, or configuration.
- **Action:** Publish the Diagnostic Record, build competing hypotheses, run a read-only probe that distinguishes them, then write the Root-Cause Contract before editing.
- **Verification:** Run the specified test command and report its actual terminal result.
