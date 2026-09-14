# Prompt Optimizer: The Universal AI Architect & Scaffolding Platform

🚀 **Enterprise-grade, MCP-native platform** designed to transform AI development workflows through professional prompt engineering, agentic scaffolding, and cloud-powered optimization.

[![NPM Package](https://img.shields.io/npm/v/mcp-prompt-optimizer)](https://www.npmjs.com/package/mcp-prompt-optimizer) [![API Status](https://img.shields.io/badge/API-Production-green)](https://p01--project-optimizer--fvrdk8m9k9j.code.run/health) [![Dashboard](https://img.shields.io/badge/Dashboard-Live-blue)](https://promptoptimizer.xyz) [![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-purple)](https://mcp.so) [![Skills License](https://img.shields.io/badge/skill%2F-MIT-brightgreen)](./skill/LICENSE)

> **License split:** the [`skill/`](./skill/) directory (Claude Code Skills) is free and open-source under MIT — no account, no signup. Everything else in this repo (backend, MCP packages, web dashboard) is Commercial — see the root [`LICENSE`](./LICENSE).

---

## 🌟 The Four-Tier Ecosystem

Prompt Optimizer is more than just a server; it's a complete ecosystem for high-performance AI interaction.

### 1. ☁️ Cloud Pro (v3.7.5)
The flagship MCP server. Routes complex prompts through a sophisticated LLM rewriting pipeline with **Bayesian tuning** and **AG-UI** real-time streaming. Includes team collaboration and shared quotas.

### 2. 🔒 Local Core (v4.1.2)
A privacy-first, 100% offline version. Uses a library of **120+ domain-specific rules** and platform-specific binaries for zero-latency, secure optimization on your own machine.

### 3. 🖥️ Web Dashboard
The command center at [promptoptimizer.xyz](https://promptoptimizer.xyz). Manage API keys, configure **Personal Model Choice** (via OpenRouter), track analytics, and run A/B evaluations.

### 4. ⚡ Claude Code Skills (MIT, zero-friction)
Free Claude Code Skills distilling this platform's methodology into pure in-context instructions. No npm install, no API key, no license key, no external process — copy the `SKILL.md` you want into `.claude/skills/<name>/` and Claude Code loads it directly. Each is MIT-licensed, separate from this repo's Commercial license covering the backend and MCP packages — see [`skill/LICENSE`](./skill/LICENSE).

- **[`skill/prompt-optimizer/SKILL.md`](./skill/prompt-optimizer/SKILL.md)** — this platform's optimization methodology (context classification, sophistication assessment, optimization moves, parameter preservation). A weaker sibling to Cloud Pro and Local Core (no LLM-based optimization tier, no persistent history/quota/templates, no Bayesian tuning), positioned as the zero-account entry point.
- **[`skill/context-cartographer/SKILL.md`](./skill/context-cartographer/SKILL.md)** — assembles high-signal repository context before non-trivial implementation, debugging, or review work.
- **[`skill/empirical-diagnostician/SKILL.md`](./skill/empirical-diagnostician/SKILL.md)** — forces evidence-based debugging: mandatory log extraction, a Fast-Track bypass for unambiguous single-token defects, a hypothesis matrix for anything more complex, and a Root-Cause Contract before any edit. Validated against a fixed behavioral benchmark (6/6 disposable-repo runs, independent pytest oracle, 1.0 on a live LLM-rubric fidelity check).
- **[`skill/prompt-evaluation-engineer/SKILL.md`](./skill/prompt-evaluation-engineer/SKILL.md)** — turns prompts into reproducible evaluation protocols: contracts, balanced test matrices, deterministic checks before semantic rubrics, evidence preservation, and regression-safe comparisons.
- **[`skill/prompt-injection-guard/SKILL.md`](./skill/prompt-injection-guard/SKILL.md)** — detects, classifies, and responds to prompt-injection against an LLM application: input and output inspection, graded severity with a confidence factor, tiered response strategy, fail-mode and per-check latency budget, and outbound tool-argument hardening.
- **[`skill/agent-prompt-architect/SKILL.md`](./skill/agent-prompt-architect/SKILL.md)** — architects the system prompt, context budget, and tool contract of an AI agent as one system: an agent contract, a cache-stable context budget, tool-contract engineering, explicit stop conditions split into prompt-side and harness-enforced, and evaluation-driven iteration.
- **[`skill/prompt-complexity-triage/SKILL.md`](./skill/prompt-complexity-triage/SKILL.md)** — decides *how much* to change a prompt before changing it: five consumer-anchored scoring dimensions plus a non-summed technical-density risk cap, fixed thresholds mapping to four tiers (leave as-is, light touch, structured rewrite, full rebuild), meaning-preservation guardrails with a mandatory pre-output preservation check, and a visible triage line every run so the tier decision is auditable.
- **[`skill/subagent-dispatch-economics/SKILL.md`](./skill/subagent-dispatch-economics/SKILL.md)** — decides whether delegating work to a subagent is worth its cost: a four-question delegation test, a fork-vs-fresh-vs-inline shape selection with an explicit tiebreaker, a prompt-scoping contract for briefing zero-context fresh agents, wave-sizing rules for parallel dispatch, and a visible dispatch line every decision so the delegation call is auditable.

---

## 🚀 Quick Start

### Step 1: Install the MCP Package
```bash
# Install the cloud-connected version (recommended)
npm install -g mcp-prompt-optimizer
```

### Step 2: Get Your API Key
1. Visit [promptoptimizer.xyz/pricing](https://promptoptimizer.xyz/pricing)
2. Choose your tier (Free tier includes 20 optimizations/month, no credit card required).
3. API keys follow the format: `sk-opt-*`, `sk-team-*`, or `sk-local-*`.

### Step 3: Configure Your MCP Client
Add to `~/.claude/claude_desktop_config.json` (Claude Desktop):
```json
{
  "mcpServers": {
    "prompt-optimizer": {
      "command": "npx",
      "args": ["mcp-prompt-optimizer"],
      "env": {
        "OPTIMIZER_API_KEY": "sk-opt-your-key-here"
      }
    }
  }
}
```

---

## 🧠 Intelligent Optimization Pipeline

Prompts are routed through a tiered system to ensure the highest quality based on your subscription and connectivity.

- **Tier 1 — LLM Optimization (70–95% Confidence):** Genuine rewriting and enrichment using advanced models (Gemini, Claude, and GPT families, configurable per your OpenRouter setup).
- **Tier 2 — Backend Rules ( < 25% Confidence):** Rapid rules-based pass for simple prompts or when personal models aren't configured.
- **Tier 3 — Local Fallback (35–55% Confidence):** Structured optimization applied locally if the backend is unreachable.

---

## 🤖 Context Engineer (CE) Suite
*Available on Pro and Enterprise tiers.*

Transform vague goals into production-ready agentic scaffolding directly in your IDE.

- **`generate_agent_sop`**: Generate structured Standard Operating Procedures for AI agents.
- **`generate_skill_package`**: Create a complete skill package (SOP + SKILL.md + reference + examples).
- **`transform_for_framework`**: Convert SOPs into native code for **LangChain**, **AutoGen**, or **Claude Code**.

---

## 🛠️ Available MCP Tools

| Tool | Description |
|---|---|
| `optimize_prompt` | Transform prompts with professional techniques & Bayesian tuning. |
| `detect_ai_context` | Automatically detect intent (Code, Image, Research, etc.). |
| `search_templates` | Browse your history and reusable optimization patterns. |
| `get_quota_status` | Monitor your real-time usage and subscription limits. |
| `get_ce_quota_status` | Check Context Engineer credits and workflow availability. |

---

## 🎨 AI Context Detection
Automatically applies specialized goals for:
- 💻 **Code Generation**: Technical accuracy, parameter preservation, precision.
- 🎨 **Image Generation**: Midjourney/DALL-E syntax, style boosters, camera settings.
- 📊 **Structured Output**: JSON/Schema integrity, YAML, CSV transformations.
- 💬 **Human Communication**: Tone adjustment, clarity, formal/informal shifts.
- 🔍 **Research & Analysis**: Context specificity, token efficiency, actionability.

---

## 🎛️ Personal Model Choice
Don't be locked into one model. Configure your own **OpenRouter** keys in the WebUI to pick from the current Claude, GPT, and Gemini model families — swap models per task without changing your integration.

---

## 💰 Subscription Plans

| Plan | Price | Optimizations/mo | Features |
|---|---|---|---|
| **Free** | $0/mo | 20 | Validate fit, no credit card required |
| **Pro** | $19/mo | 500 | Full model config, Context Engineering |
| **Enterprise** | Custom | Custom | Team features, shared quotas |

---

## 🔒 Security & Privacy
- **Encrypted Transmission**: All data is sent over TLS.
- **Scoped Retention**: Optimizations are saved to your own template library, encrypted at rest — never shared across users or used to train models.
- **Local Option**: Use `mcp-prompt-optimizer-local` for 100% on-device processing.

---

## 📞 Support & Resources
- **Documentation**: [promptoptimizer.xyz/documentation](https://promptoptimizer.xyz/documentation)
- **Dashboard**: [promptoptimizer.xyz/dashboard](https://promptoptimizer.xyz/dashboard)
- **Email**: support@promptoptimizer.help

---
*Transforming AI interactions through professional prompt engineering.*
