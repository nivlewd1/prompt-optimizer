# Prompt Optimizer: The Universal AI Architect & Scaffolding Platform

An MCP server, a web dashboard, a local rules-based package and a set of free Claude Code skills for prompt optimization and agentic scaffolding.

[![NPM Package](https://img.shields.io/npm/v/mcp-prompt-optimizer)](https://www.npmjs.com/package/mcp-prompt-optimizer) [![API Status](https://img.shields.io/badge/API-Production-green)](https://p01--project-optimizer--fvmrdk8m9k9j.code.run/health) [![Dashboard](https://img.shields.io/badge/Dashboard-Live-blue)](https://promptoptimizer.xyz) [![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-purple)](https://mcp.so) [![Skills License](https://img.shields.io/badge/skill%2F-MIT-brightgreen)](./skill/LICENSE)

> **License split:** the [`skill/`](./skill/) directory (Claude Code Skills) is free and open-source under MIT — no account, no signup. Everything else in this repo (backend, MCP packages, web dashboard) is Commercial — see the root [`LICENSE`](./LICENSE).

---

## 🌟 The Four-Tier Ecosystem

Prompt Optimizer has four parts: a cloud MCP server, a local package, a web dashboard, and Claude Code skills.

### 1. ☁️ Cloud Pro (v3.8.6)
The cloud MCP server. Optimizes prompts through an LLM rewriting pipeline with context detection, a template library with version history, and streaming (AG-UI). Pro is a single-user plan; shared quotas and team features are Enterprise.

### 2. 🔒 Local Core (v4.1.10)
A rules-based version that optimizes prompts on your own machine using 129 built-in rules, with no prompt text sent to the backend. The free tier needs no key and makes no network calls; a Basic or Pro license key is validated against the backend.

### 3. 🖥️ Web Dashboard
The command center at [promptoptimizer.xyz](https://promptoptimizer.xyz). Manage API keys, configure **Personal Model Choice** (via OpenRouter), track analytics, and run evaluations (quick evaluate, datasets, cross-model comparison).

### 4. ⚡ Claude Code Skills (MIT, zero-friction)
Free Claude Code Skills distilling this platform's methodology into pure in-context instructions. No npm install, no API key, no license key, no external process — copy the `SKILL.md` you want into `.claude/skills/<name>/` and Claude Code loads it directly. Each is MIT-licensed, separate from this repo's Commercial license covering the backend and MCP packages — see [`skill/LICENSE`](./skill/LICENSE). Install steps and a one-line summary of each skill: [`skill/README.md`](./skill/README.md).

- **[`skill/prompt-optimizer/SKILL.md`](./skill/prompt-optimizer/SKILL.md)** — this platform's optimization methodology (context classification, sophistication assessment, optimization moves, parameter preservation). A weaker sibling to Cloud Pro and Local Core (no LLM-based optimization tier, no persistent history/quota/templates), positioned as the zero-account entry point.
- **[`skill/context-cartographer/SKILL.md`](./skill/context-cartographer/SKILL.md)** — assembles high-signal repository context before non-trivial implementation, debugging, or review work.
- **[`skill/empirical-diagnostician/SKILL.md`](./skill/empirical-diagnostician/SKILL.md)** — forces evidence-based debugging: mandatory log extraction, a Fast-Track bypass for unambiguous single-token defects, a hypothesis matrix for anything more complex, and a Root-Cause Contract before any edit. Validated against a fixed behavioral benchmark (6/6 disposable-repo runs, independent pytest oracle).
- **[`skill/prompt-evaluation-engineer/SKILL.md`](./skill/prompt-evaluation-engineer/SKILL.md)** — turns prompts into reproducible evaluation protocols: contracts, balanced test matrices, deterministic checks before semantic rubrics, evidence preservation, and regression-safe comparisons.
- **[`skill/prompt-injection-guard/SKILL.md`](./skill/prompt-injection-guard/SKILL.md)** — detects, classifies, and responds to prompt-injection against an LLM application: input and output inspection, graded severity with a confidence factor, tiered response strategy, fail-mode and per-check latency budget, and outbound tool-argument hardening.
- **[`skill/agent-prompt-architect/SKILL.md`](./skill/agent-prompt-architect/SKILL.md)** — architects the system prompt, context budget, and tool contract of an AI agent as one system: an agent contract, a cache-stable context budget, tool-contract engineering, explicit stop conditions split into prompt-side and harness-enforced, and evaluation-driven iteration.
- **[`skill/prompt-complexity-triage/SKILL.md`](./skill/prompt-complexity-triage/SKILL.md)** — decides *how much* to change a prompt before changing it: five consumer-anchored scoring dimensions plus a non-summed technical-density risk cap, fixed thresholds mapping to four tiers (leave as-is, light touch, structured rewrite, full rebuild), meaning-preservation guardrails with a mandatory pre-output preservation check, and a visible triage line every run so the tier decision is auditable.
- **[`skill/subagent-dispatch-economics/SKILL.md`](./skill/subagent-dispatch-economics/SKILL.md)** — decides whether delegating work to a subagent is worth its cost: a four-question delegation test, a fork-vs-fresh-vs-inline shape selection with an explicit tiebreaker, a prompt-scoping contract for briefing zero-context fresh agents, wave-sizing rules for parallel dispatch, and a visible dispatch line every decision so the delegation call is auditable.
- **[`skill/context-drift-auditor/SKILL.md`](./skill/context-drift-auditor/SKILL.md)** — audits whether a long-running prompt or agent run has drifted from its original contract across turns, retrieved sources, edits, and version changes: a versioned context ledger, a unified drift-and-resolution table, field-scoped authority rules, a reconstructed context packet, per-item dispositions (including quarantining untrusted retrieved content), and a gate decision (proceed, ask first, revalidate, or stop) before the next side-effecting action.
- **[`skill/eval-suite-auditor/SKILL.md`](./skill/eval-suite-auditor/SKILL.md)** — audits an existing evaluation pipeline (LLM judges, assertions, repair or regression gates) for silent failure by probing it: maps every score entry point and its consumers, probes 14 failure classes (dead or partial judge, unparseable replies, hidden aggregation failures, conflicting thresholds, judge noise against the decision margin, stored placeholder rows) with a positive control each, checks calibration honestly, and reports verified findings with real-data exposure.
- **[`skill/ambition-calibrator/SKILL.md`](./skill/ambition-calibrator/SKILL.md)** — decides whether a task request should be made more ambitious, then rewrites it deeper rather than bigger: a bypass for small or ceilinged tasks, a goal ladder (Altitude), the raw inputs and professional methods a top practitioner would use (Depth), lenses from adjacent fields that each run a concrete check (Range), a confirmation gate before anything widens scope or cost, and an outside judge whose unedited output is shown, or an explicit UNVERIFIED label when none exists. Based on Felix Rieseberg's post "How to be more ambitious".

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
Run `npx mcp-prompt-optimizer connect` to have the package write this into your MCP client's config, or add it yourself. Claude Desktop reads `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS), `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/.config/Claude/claude_desktop_config.json` (Linux):
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

The backend routes each prompt by complexity: a rules-based pass for simple prompts, LLM optimization for complex ones, and a hybrid tier in between. If the backend is unreachable, the npm package applies a structured local fallback (confidence 0.35 to 0.55).

---

## 🤖 Context Engineer (CE) Suite
*Free accounts get a small monthly allowance: 3 basic SOPs and 1 full skill package, for the Claude Code and Ollama targets on the default model. Pro adds 3 full skill builds a month, advanced steps and the other agent targets. Enterprise allowances are custom.*

Transform vague goals into production-ready agentic scaffolding directly in your IDE.

- **`generate_agent_sop`**: Generate structured Standard Operating Procedures for AI agents.
- **`generate_skill_package`**: Create a complete skill package (SOP + SKILL.md + reference + examples).
- **`transform_for_framework`**: Convert SOPs into native code for **LangChain**, **AutoGen**, or **Claude Code**.

---

## 🛠️ Available MCP Tools

| Tool | Description |
|---|---|
| `optimize_prompt` | Optimize a prompt with context-aware techniques. |
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
- 🧠 **LLM Interaction**: Research, analysis, and complex-explanation prompts. (Also detected: API automation, technical automation, data analysis.)

---

## 🎛️ Personal Model Choice
Don't be locked into one model. On Pro, configure your own **OpenRouter** key in the dashboard and choose the model used for your optimizations. Free accounts use the default model.

---

## 💰 Subscription Plans

| Plan | Price | Optimizations/mo | Features |
|---|---|---|---|
| **Free** | $0/mo | 20 | No credit card required; default model; 3 basic SOPs and 1 full skill package a month |
| **Pro** | $19/mo | 500 | Model choice, 3 full skill builds a month, advanced Context Engineering steps |
| **Enterprise** | Custom | Custom | Custom allowances; team features and shared quotas |

---

## 🔒 Security & Privacy
- **Encrypted Transmission**: All traffic uses HTTPS (TLS 1.2 or newer, with HSTS).
- **Scoped Retention**: Optimizations that produce a result are saved to your own template library, stored in Supabase Postgres (encrypted at rest by the provider). They are not shared across users or used to train models.
- **Local Option**: `mcp-prompt-optimizer-local` processes prompts on your machine. The free tier needs no key and makes no network calls; with a license key, only the key is checked with the backend.

---

## 📞 Support & Resources
- **Documentation**: [promptoptimizer.xyz/documentation](https://promptoptimizer.xyz/documentation)
- **Dashboard**: [promptoptimizer.xyz/dashboard](https://promptoptimizer.xyz/dashboard)
- **Email**: support@promptoptimizer.xyz

---
*Transforming AI interactions through professional prompt engineering.*
