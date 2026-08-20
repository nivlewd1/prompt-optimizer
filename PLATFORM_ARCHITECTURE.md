# Platform Architecture Overview: Prompt Optimizer

The Prompt Optimizer is an integrated ecosystem designed for high-performance AI prompt engineering, agentic scaffolding, and deployment. The architecture is modular, ensuring both cloud-powered intelligence and privacy-first local processing.

## 🏗️ The Four-Tier Ecosystem

The platform is divided into four core pillars that work in harmony:

### 1. 🏢 Backend Infrastructure (FastAPI Pro)
The central intelligence and routing hub. Built with **FastAPI** for high-performance asynchronous processing.
- **Optimization Engine**: Implements a three-tier optimization pipeline (LLM-based, rules-based, and local fallback).
- **Intelligent Routing**: Automatically detects AI context (Code, Image, Research, etc.) and routes to specialized templates.
- **Enterprise Features**: Handles Stripe billing, team multi-tenancy, and template governance.
- **Bayesian Optimizer**: Fine-tunes optimization parameters based on performance metrics.
- **AG-UI Service**: Powers real-time, streaming optimization feedback.

### 2. 🌐 Frontend & User Interface (Next.js Dashboard)
The command center for users and administrators.
- **User Portal**: API key management, quota tracking, and subscription upgrades.
- **Evaluation Framework**: Run A/B tests on prompts and analyze confidence scores.
- **Model Personalization**: Configure **OpenRouter** keys to choose specific LLMs for optimization tasks.
- **Template Library**: Browse, search, and manage a team-wide library of optimized patterns.

### 3. 🔌 Universal Integration (MCP Packages)
Connects the platform directly to your developer tools (Claude Desktop, Cursor, etc.).
- **`mcp-prompt-optimizer` (Cloud)**: Connects to the FastAPI backend for the highest-sophistication optimization.
- **`mcp-prompt-optimizer-local` (Local)**: A standalone version for privacy-first users, featuring 120+ offline rules and native platform binaries.

### 4. ⚡ Zero-Friction Skills (Claude Code)
Three pure in-context Claude Code Skills. No backend call, no account, no external process. All three were generated via this platform's own Context Engineer system (`generate_skill_package(format="claude_skill")`, which internally calls `transform_sop_to_claude_skill()`).

- **[`skill/prompt-optimizer/SKILL.md`](./skill/prompt-optimizer/SKILL.md)**: distills the platform's optimization methodology (context classification, sophistication assessment, optimization moves, parameter preservation) into direct instructions for Claude.
- **[`skill/context-cartographer/SKILL.md`](./skill/context-cartographer/SKILL.md)**: assembles high-signal repository context before non-trivial implementation, debugging, or review work.
- **[`skill/empirical-diagnostician/SKILL.md`](./skill/empirical-diagnostician/SKILL.md)**: forces evidence-based debugging via mandatory log extraction, a Fast-Track bypass for unambiguous defects, a hypothesis matrix for anything more complex, and a Root-Cause Contract before any edit. Validated against a fixed behavioral benchmark: 6/6 disposable-repo runs, independent pytest oracle, 1.0 on a live LLM-rubric fidelity check.

---

## 📁 Repository Organization

The platform's code is distributed across specialized modules to ensure modularity and security:

### **FastAPI Backend (`/app`)**
- `/api`: Specialized routers for optimization, analytics, and management.
- `/core`: The core logic for context detection, Bayesian optimization, and database interactions.
- `/services`: High-level services like AG-UI and dynamic model management.
- `/models`: Pydantic schemas and database models.

### **Next.js Frontend (`/src`)**
- `/pages`: Dashboard, blog, documentation, and payment interfaces.
- `/components`: Specialized UI elements like the **Hybrid Optimizer** and **Evaluation Panel**.
- `/services`: Client-side logic for interacting with the backend API and Supabase.

### **MCP Server Logic**
- **Protocol Implementation**: Standardized JSON-RPC 2.0 communication for MCP compliance.
- **Validation Engine**: Pre-flight checks for API keys and subscription quotas.
- **Resilient Fallback**: Structured local rule engine that activates if the backend is unreachable.

---

## 🎯 Optimization Methodology

The platform utilizes a **Confidence-Based Pipeline** to ensure quality:

| Tier | Source | Confidence | Description |
|---|---|---|---|
| **Tier 1** | Backend LLM | 70% – 95% | Deep rewriting using professional engineering principles. |
| **Tier 2** | Backend Rules | < 25% | Rapid structural enhancement for simple prompts. |
| **Tier 3** | Local Fallback | 35% – 55% | Offline structural patterns applied via the NPM package. |

---

## 🔐 Security & Data Flow

1. **Authentication**: All requests are validated using tier-specific API keys (`sk-opt-*`, `sk-team-*`, `sk-local-*`).
2. **Encryption**: 100% TLS/SSL encryption for data in transit.
3. **Privacy**: Prompts are saved to your own scoped template library, encrypted at rest — never shared across users or used for model training.
4. **Local Sovereignty**: The `local` package ensures that sensitive data never leaves the user's machine.

---
**Version:** production-v2.3.0
**License:** Commercial / Enterprise for the backend, MCP packages, and web dashboard. The `skill/` directory (Prompt Optimizer Skill) is MIT-licensed separately — see `skill/LICENSE`.
**Official Homepage:** [promptoptimizer.xyz](https://promptoptimizer.xyz)
