# Platform Architecture Overview: Prompt Optimizer

Prompt Optimizer is an ecosystem for prompt engineering, agentic scaffolding and deployment: a cloud backend, a web dashboard, two MCP packages and a set of in-context Claude Code skills.

## The Four-Tier Ecosystem

### 1. Backend (FastAPI)
The central service, built with **FastAPI** for asynchronous request handling.
- **Optimization Engine**: Routes each prompt by complexity to a rules-based pass, an LLM-based pass, or a hybrid of the two.
- **Context Detection**: Detects the AI context (code, image, research, etc.) and picks specialized templates.
- **Billing and Teams**: Stripe billing, team multi-tenancy and template governance (version history, publish states).
- **Bayesian Optimizer**: An experimental parameter-tuning subsystem under operator control. It is not applied to individual requests automatically.
- **AG-UI Service**: Streaming optimization feedback over WebSocket.

### 2. Web Dashboard (Next.js)
- **User Portal**: API key management, quota tracking, and subscription upgrades.
- **Evaluation Framework**: Run quick evaluations, manage datasets, and compare models.
- **Model Personalization**: On Pro, configure your own **OpenRouter** key to choose the model used for your optimizations.
- **Template Library**: Browse, search and manage your saved optimization templates.

### 3. MCP Packages
Connect the platform to your developer tools (Claude Desktop, Cursor, etc.).
- **`mcp-prompt-optimizer` (Cloud)**: Connects to the backend for LLM-based optimization.
- **`mcp-prompt-optimizer-local` (Local)**: Optimizes prompts on your machine with 129 built-in rules. Only your license key is sent to the backend, to validate it and read your quota.

### 4. Claude Code Skills
Ten in-context Claude Code skills. No backend call, no account, no external process. Most were produced with the Context Engineer. See [`skill/README.md`](./skill/README.md) for the index and install steps.

---

## Repository Organization

This public repository contains the documentation, the skills (`skill/`) and an **older snapshot** of the MCP package (`mcp-package/`, v3.1.1). The backend and the web app live in private repositories. The current source of the cloud MCP package is [`nivlewd1/mcp-prompt-optimizer-npm`](https://github.com/nivlewd1/mcp-prompt-optimizer-npm).

In the private backend repository:
- `/app/api`: routers for optimization, analytics, and management.
- `/app/core`: context detection, optimization engines and database access.
- `/app/services`: services such as AG-UI and model management.
- `/app/models`: Pydantic schemas.

### MCP Server Logic
- **Protocol Implementation**: Model Context Protocol over JSON-RPC.
- **Validation**: The server checks your API key before it starts.
- **Local Fallback**: A structured local rule pass applies if the backend is unreachable.

---

## Optimization Pipeline

| Tier | Source | Description |
|---|---|---|
| **Rules** | Backend | A rules-based pass for simple prompts. |
| **Hybrid** | Backend | Rules plus an LLM pass for medium-complexity prompts. |
| **LLM** | Backend | Full LLM optimization for complex prompts. |
| **Local fallback** | npm package | Structured local patterns when the backend is unreachable (confidence 0.35 to 0.55). |

---

## Security & Data Flow

1. **Authentication**: Requests are validated using API keys (`sk-opt-*`, `sk-team-*`, `sk-local-*`).
2. **Encryption**: TLS (1.2 or newer) for data in transit.
3. **Privacy**: Optimizations that produce a result are saved to your own scoped template library (Supabase Postgres, encrypted at rest by the provider). They are not shared across users or used for model training.
4. **Local package**: Prompts are processed on your machine; only your license key is sent to the backend.

---
**Version:** see the backend [`/status`](https://p01--project-optimizer--fvmrdk8m9k9j.code.run/status) endpoint for the current deployed version.
**License:** Commercial for the backend, MCP packages, and web dashboard. The `skill/` directory is MIT-licensed separately — see `skill/LICENSE`.
**Official Homepage:** [promptoptimizer.xyz](https://promptoptimizer.xyz)
