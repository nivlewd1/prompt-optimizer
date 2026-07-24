---
name: prompt-optimizer
description: This skill helps Claude optimize user prompts for clarity, technical accuracy, and effectiveness before sending them to an AI system.
---

# Optimize User Prompts for AI Systems

Use this skill whenever a user requests assistance in improving, optimizing, refining, or rewriting a prompt intended for an AI system, such as an LLM, image generator, or human collaborator. The goal is to ensure the prompt is clear, technically accurate, and effective.

## Instructions

When a user asks to optimize a prompt, follow these steps:

1. **Classify the AI Context**  
   Read the prompt and identify its primary context using the following signals:
   - Code Generation
   - Image Generation
   - Structured Output
   - Human Communication
   - Research & Analysis
   - Creative Enhancement  
   If a prompt matches multiple contexts, prioritize the primary context and retain relevant details from the secondary context.

2. **Assess Sophistication Level**  
   Evaluate how much the user knows and the existing structure of the prompt:
   - Simple
   - Intermediate
   - Advanced
   - Expert  
   Adjust the level of new structure added based on the gap between the current level and the next level up.

3. **Apply Optimization Moves**  
   For the identified context, formulate the optimization using:
   - **Persona**: Define who the AI should act as.
   - **Instruction**: Specify what to produce.
   - **Principles**: Establish guardrails and quality standards.
   - **Anti-patterns**: Define what to avoid.  
   Use your judgment on how to construct these elements narratively rather than relying on fixed templates.

4. **Preserve Technical Parameters**  
   Before finalizing, scan the original prompt for any technical elements and copy them verbatim into the optimized version:
   - Code fences and content
   - Exact numbers, versions, flags, and paths
   - Model IDs and proper nouns
   - Exact error messages and stack traces
   - URLs and email addresses  
   Never alter or rephrase these elements; highlight any ambiguity in your closing note.

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