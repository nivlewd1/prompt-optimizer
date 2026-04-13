# REST API Documentation: Prompt Optimizer Pro

The Prompt Optimizer Pro API provides high-performance prompt engineering through HTTP endpoints. This API powers both our MCP packages and the web dashboard, offering 50+ professional optimization goals and agentic scaffolding tools.

**Production Endpoint**: `https://p01--project-optimizer--fvrdk8m9k9j.code.run`

## Authentication

All requests must include an `X-API-Key` header:

```http
X-API-Key: sk-opt-your-api-key-here
```

API keys follow the format: `sk-opt-*`, `sk-team-*`, or `sk-local-*`.

---

## 🚀 Core Optimization Endpoints

### 1. Optimize Prompt
**POST** `/api/v1/optimize`

The primary endpoint for prompt refinement.

**Request:**
```json
{
  "prompt": "Your raw prompt here",
  "goals": ["clarity", "technical_accuracy"],
  "ai_context": "code_generation",
  "stream": false
}
```

**Response:**
```json
{
  "optimized_prompt": "...",
  "confidence_score": 0.89,
  "quota_remaining": 17850,
  "ai_context_detected": "code_generation"
}
```

### 2. Context Detection
**POST** `/api/v1/detect-context`

Automatically identify the intent and optimal strategy for a prompt.

---

## 🤖 Context Engineer (CE) Tools
*Requires Creator or Innovator subscription.*

### 1. Generate Agent SOP
**POST** `/api/v1/context-engineer/generate-sop`

Create a structured Standard Operating Procedure for an AI agent.

### 2. Generate Skill Package
**POST** `/api/v1/context-engineer/generate-skill`

Generate a comprehensive skill package (SOP + SKILL.md + reference).

### 3. Transform for Framework
**POST** `/api/v1/context-engineer/transform`

Transform an SOP into native code for **LangChain**, **AutoGen**, or **Claude Code**.

---

## 🛠️ Management & Analytics

### 1. Quota Status
**GET** `/api/v1/mcp/quota-status`

Check real-time usage and limits.

### 2. Template Search
**POST** `/api/v1/templates/search`

Search your history and reusable optimization patterns.

### 3. Personal Model Configuration
**GET** `/api/v1/user/config`

Retrieve user-configured model preferences (OpenRouter settings).

---

## 🎨 AI Context Types

The API uses `ai_context` to apply specialized optimization rules:
- `code_generation`: Python, JavaScript, SQL, debugging.
- `image_generation`: Midjourney, DALL-E, visual descriptors.
- `llm_interaction`: Research, analysis, complex explanation.
- `human_communication`: Emails, memos, formal letters.
- `technical_automation`: API docs, deployment scripts, DevOps.
- `structured_output`: JSON, YAML, Schema-based tasks.

---

## 🔧 Optimization Goals (50+)

Goals are categorized by subscription tier:

- **Core (25 goals)**: Clarity, conciseness, specificity, structure.
- **Advanced (25 goals)**: Prompt chaining, few-shot optimization, Bayesian tuning, technical precision, security enhancement.

---

## 🚨 Error Handling

| Status | Error Code | Description |
|---|---|---|
| `401` | `INVALID_API_KEY` | Key is malformed or invalid. |
| `403` | `QUOTA_EXCEEDED` | Monthly usage limit reached. |
| `429` | `RATE_LIMITED` | Too many requests; retry after delay. |
| `500` | `INTERNAL_ERROR` | Unexpected backend error. |

---
**Version:** v1 (Backend production-v2.2.0-stable)  
**Full Documentation:** [promptoptimizer.xyz](https://promptoptimizer.xyz)
