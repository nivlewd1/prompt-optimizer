# Prompt Optimizer: The Universal AI Architect & Scaffolding Platform

🚀 **Enterprise-grade, MCP-native platform** designed to transform AI development workflows through professional prompt engineering, agentic scaffolding, and cloud-powered optimization.

[![NPM Package](https://img.shields.io/npm/v/mcp-prompt-optimizer)](https://www.npmjs.com/package/mcp-prompt-optimizer) [![API Status](https://img.shields.io/badge/API-Production-green)](https://p01--project-optimizer--fvrdk8m9k9j.code.run/health) [![Dashboard](https://img.shields.io/badge/Dashboard-Live-blue)](https://promptoptimizer.xyz) [![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-purple)](https://mcp.so)

---

## 🌟 The Four-Tier Ecosystem

Prompt Optimizer is more than just a server; it's a complete ecosystem for high-performance AI interaction.

### 1. ☁️ Cloud Pro (v3.7.5)
The flagship MCP server. Routes complex prompts through a sophisticated LLM rewriting pipeline with **Bayesian tuning** and **AG-UI** real-time streaming. Includes team collaboration and shared quotas.

### 2. 🔒 Local Core (v4.1.2)
A privacy-first, 100% offline version. Uses a library of **120+ domain-specific rules** and platform-specific binaries for zero-latency, secure optimization on your own machine.

### 3. 🖥️ Web Dashboard
The command center at [promptoptimizer.xyz](https://promptoptimizer.xyz). Manage API keys, configure **Personal Model Choice** (via OpenRouter), track analytics, and run A/B evaluations.

### 4. ⚡ Prompt Optimizer Skill (MIT, zero-friction)
A free Claude Code Skill distilling this platform's optimization methodology into pure in-context instructions. No npm install, no API key, no license key, no external process — copy [`skill/SKILL.md`](./skill/SKILL.md) into `.claude/skills/prompt-optimizer/` and Claude Code loads it directly. A weaker sibling to Cloud Pro and Local Core (no LLM-based optimization tier, no persistent history/quota/templates, no Bayesian tuning), positioned as the zero-account entry point — see [`skill/LICENSE`](./skill/LICENSE) (MIT, separate from this repo's Commercial license covering the backend and MCP packages).

---

## 🚀 Quick Start

### Step 1: Install the MCP Package
```bash
# Install the cloud-connected version (recommended)
npm install -g mcp-prompt-optimizer
```

### Step 2: Get Your API Key
1. Visit [promptoptimizer.xyz/pricing](https://promptoptimizer.xyz/pricing)
2. Choose your tier (Free trial includes 5 optimizations).
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

- **Tier 1 — LLM Optimization (70–95% Confidence):** Genuine rewriting and enrichment using advanced models (Gemini Flash/Claude 3.5).
- **Tier 2 — Backend Rules ( < 25% Confidence):** Rapid rules-based pass for simple prompts or when personal models aren't configured.
- **Tier 3 — Local Fallback (35–55% Confidence):** Structured optimization applied locally if the backend is unreachable.

---

## 🤖 Context Engineer (CE) Suite
*Available in Creator and Innovator tiers.*

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
Don't be locked into one model. Configure your own **OpenRouter** keys in the WebUI to use:
- **Claude 3.5 Sonnet** for complex technical tasks.
- **GPT-4o** for rapid creative iterations.
- **Gemini 1.5 Pro** for deep research.

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
- **Zero-Retention**: Prompts are processed and discarded; we never train on your data.
- **Local Option**: Use `mcp-prompt-optimizer-local` for 100% on-device processing.

---

## 📞 Support & Resources
- **Documentation**: [promptoptimizer.xyz/docs](https://promptoptimizer.xyz/docs)
- **Dashboard**: [promptoptimizer.xyz/dashboard](https://promptoptimizer.xyz/dashboard)
- **Email**: support@promptoptimizer.xyz

---
*Transforming AI interactions through professional prompt engineering.*
