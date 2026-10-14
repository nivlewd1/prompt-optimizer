# REST API Documentation: Prompt Optimizer Pro

The Prompt Optimizer API provides prompt optimization and Context Engineering over HTTP. It powers the MCP packages and the web dashboard, and accepts 77 optimization goals.

**Production endpoint**: `https://p01--project-optimizer--fvmrdk8m9k9j.code.run`

The live OpenAPI schema is served at `/openapi.json`. Where this page and the schema differ, the schema is correct.

## Authentication

Send your API key in the `X-API-Key` header:

```http
X-API-Key: sk-opt-your-api-key-here
```

API keys follow the format: `sk-opt-*`, `sk-team-*`, or `sk-local-*`.

---

## Core Optimization Endpoints

### 1. Optimize Prompt
**POST** `/api/v1/optimize`

The primary endpoint for prompt refinement. Only `prompt` is required. Other accepted fields include `goals`, `ai_context`, `model`, `stream`, `context` and `output_format`.

**Request:**
```json
{
  "prompt": "Your raw prompt here",
  "goals": ["clarity", "technical_accuracy"],
  "ai_context": "code_generation",
  "stream": false
}
```

**Response** (abridged; see the schema for every field):
```json
{
  "original_prompt": "...",
  "optimized_prompt": "...",
  "confidence_score": 0.89,
  "status": "...",
  "metadata": {}
}
```

### 2. Context Detection
**POST** `/api/v1/mcp/detect-context`

Identify the intent of a prompt. (`/api/v1/templates/detect-context` is also available.)

---

## Context Engineer (CE) Tools

Free accounts get a small monthly allowance (3 basic SOPs and 1 full skill package, for the Claude Code and Ollama targets on the default model). Pro adds 3 full skill builds a month, advanced steps and the other agent targets. Enterprise allowances are custom. A request over an allowance is refused with a `403` (see Error Handling).

### 1. Generate Agent SOP
**POST** `/api/v1/context-engineer/sop`

Create a structured Standard Operating Procedure for an AI agent.

### 2. Generate Skill Package
**POST** `/api/v1/context-engineer/skill-package`

Generate a skill package (SOP + SKILL.md + reference). The asynchronous agent workflow is `POST /api/v1/context-engineer/generate-skill-package`, polled with `GET /api/v1/context-engineer/sessions/{session_id}`.

### 3. Transform for Framework
**POST** `/api/v1/context-engineer/transform`

Transform an SOP into a framework-specific agent configuration: `claude_skill`, `langchain_tool` or `autogen_agent`.

---

## Management

### 1. Quota Status
**GET** `/api/v1/mcp/quota-status`

Check usage and limits.

### 2. Template Search
**GET** `/api/v1/mcp/templates`

Search your saved templates. Query parameters: `query`, `ai_context`, `sophistication_level`, `complexity_level`, `optimization_strategy`, `sort_by`, `sort_order`, `page`, `per_page`.

### 3. Personal Model Settings
**GET** `/api/v1/user/settings`

Retrieve your model preferences, including whether you have set an OpenRouter key.

---

## AI Context Types

The API uses `ai_context` to apply specialized optimization rules. Primary values:
- `code_generation`: Python, JavaScript, SQL, debugging.
- `image_generation`: Midjourney, DALL-E, visual descriptors.
- `llm_interaction`: Research, analysis, complex explanation.
- `human_communication`: Emails, memos, formal letters.
- `technical_automation`: API docs, deployment scripts, DevOps.
- `api_automation`, `data_analysis`
- `structured_output`: JSON, YAML, Schema-based tasks.

---

## Optimization Goals (77)

Passed as strings in the `goals` array, for example `clarity`, `technical_precision`, `role_prompting`. See [MCP_PACKAGE.md](./MCP_PACKAGE.md#optimization-goals-77) for a representative sample, or [promptoptimizer.xyz/documentation](https://promptoptimizer.xyz/documentation) for the complete set.

---

## Error Handling

| Status | Error | Description |
|---|---|---|
| `401` | `Authentication required` | Missing or invalid API key or token. |
| `403` | `TIER_LIMIT_REACHED`, `FEATURE_NOT_AVAILABLE`, `CE_QUOTA_EXCEEDED`, `MODEL_NOT_AVAILABLE` | Your plan does not include this feature or model, or you used this period's allowance for it. |
| `429` | `quota_exceeded` (`QUOTA_LIMIT_REACHED`) | Monthly optimization quota used up. |
| `503` | `QUOTA_CHECK_UNAVAILABLE`, `WORKFLOW_UNAVAILABLE` | Temporary; retry shortly. |
| `500` | | Unexpected backend error. |

---
**Version:** v1 (Backend production-v2.3.0)  
**Full Documentation:** [promptoptimizer.xyz](https://promptoptimizer.xyz)
