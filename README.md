# Prompt Optimizer - Enterprise AI Platform
**Enterprise-Grade MCP-Native Prompt Engineering Platform**
Transform your AI development workflow with our comprehensive platform featuring cloud-powered optimization, professional prompt engineering, and seamless integration with all major MCP clients.
[![NPM Package](https://img.shields.io/npm/v/mcp-prompt-optimizer)](https://www.npmjs.com/package/mcp-prompt-optimizer) [![API Status](https://img.shields.io/badge/API-Production-green)](https://p01--project-optimizer--fvrdk8m9k9j.code.run/health) [![Dashboard](https://img.shields.io/badge/Dashboard-Live-blue)](https://promptoptimizer-blog.vercel.app) [![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-purple)](https://mcp.so)
---
## 🚀 **Quick Start Guide**
### Step 1: Install the MCP Package
```bash
# Install globally (recommended)
npm install -g mcp-prompt-optimizer
```
### Step 2: Get Your API Key
⚠️ **Important:** An API key is REQUIRED for all operations.
1.  Visit [https://promptoptimizer-blog.vercel.app/pricing](https://promptoptimizer-blog.vercel.app/pricing)
2.  Choose your tier:
    *   **FREE Tier**: 5 daily optimizations (`sk-local-*`)
    *   **Paid Tiers**: Extended limits and features (`sk-opt-*`, `sk-team-*`)
### Step 3: Configure Your MCP Client
**✅ CORRECT Configuration for all MCP clients:**
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
### Step 4: Start Optimizing
Use the available tools in your MCP client:
- `optimize_prompt` - Transform your prompts with professional context-aware techniques
- `list_saved_templates` - Browse your optimization history
- `search_templates` - Find relevant optimization patterns
- `detect_ai_context` - Automatically detect prompt intent
---
## 💰 **Cloud Subscription Plans**
All plans include the same sophisticated AI optimization quality.
### **Explorer** - $2.99/month
*Perfect for individual developers*
- ✅ **5,000 optimizations/month** - Generous personal quota
- ✅ **1 API key** - Individual use
- ✅ **Full AI usage** - Context detection, template management, insights
- ✅ **Personal model configuration** - Via WebUI
- ✅ **Community support**
### **Creator** - $25.99/month ⭐ Popular
*Best for teams and creators*
- ✅ **18,000 optimizations/month** - Team-level quota
- ✅ **Up to 3 API keys** - Team collaboration
- ✅ **2 team members** - Shared access and templates
- ✅ **Priority processing** - Faster response times
- ✅ **Priority support** - Email support
### **Innovator** - $69.99/month
*Enterprise-grade for large teams*
- ✅ **75,000 optimizations/month** - Enterprise capacity
- ✅ **Up to 10 API keys** - Large team management
- ✅ **5 team members** - Full collaboration features
- ✅ **Advanced analytics dashboard** - Comprehensive insights
- ✅ **Dedicated support channel**
### **Free Trial**
- ✅ **5 optimizations** - Full feature access for testing (`sk-local-*`)
---
## 🧠 **AI Context Detection & Enhancement**
The server automatically detects your prompt type and applies specialized optimization goals:
### 🎨 **Image Generation Context**
*Detected patterns: `--ar`, `--v`, `midjourney`, `dall-e`, `photorealistic`*
*   **Input Example:** "A beautiful landscape --ar 16:9 --v 6"
*   **Enhanced Goals:**
    *   `parameter_preservation` - Protects technical flags like `--ar`
    *   `keyword_density` - Optimizes for visual descriptor limit
    *   `technical_precision` - Ensures correct model syntax
### 🤖 **LLM Interaction Context**
*Detected patterns: `analyze`, `explain`, `evaluate`, `summary`, `research`*
*   **Input Example:** "Analyze the pros and cons of this research paper"
*   **Enhanced Goals:**
    *   `context_specificity` - Improves role and task definition
    *   `token_efficiency` - Maximizes information per token
    *   `actionability` - Ensures clear, executable instructions
### 💻 **Code Generation Context**
*Detected patterns: `def`, `function`, `class`, `import`, `return`, `python`, `javascript`*
*   **Input Example:** `def fibonacci(n): return n if n <= 1 else...`
*   **Enhanced Goals:**
    *   `technical_accuracy` - Enforces correct syntax and logic
    *   `parameter_preservation` - Protects variable names and structure
    *   `precision` - Reduces ambiguity in logic requirements
### ⚙️ **Technical Automation Context**
*Detected patterns: `automate`, `script`, `api`, `deploy`*
*   **Input Example:** "Create a script to automate deployment"
*   **Enhanced Goals:**
    *   `technical_accuracy` - Ensures functional correctness
    *   `parameter_preservation` - Maintains critical system commands
    *   `structure` - Enforces logical step-by-step flow
### 💬 **Human Communication Context** (Default)
All other prompts receive standard optimization for **clarity**, **tone**, and **readability**.
---
## 🌍 **Local Version: MCP Prompt Optimizer Local**
For users requiring 100% local processing and privacy, we offer a cross-platform local edition.
### **Quick Start (Local)**
```bash
# 1. Get your Local API Key (Free or Pro)
# Visit https://promptoptimizer-blog.vercel.app/local-license
# 2. Set your API Key
export OPTIMIZER_API_KEY="sk-local-basic-your-key-here"
# 3. Install Globally
npm install -g mcp-prompt-optimizer-local
```
### **Local Tiers**
- **FREE Tier (`sk-local-basic-*`)**: 5 daily optimizations
- **PRO Tier (`sk-local-pro-*`)**: Unlimited optimizations
*Note: The Local version performs all processing on your machine using advanced local intelligence engines.*
---
## 🔧 **MCP Tools Available**
### `optimize_prompt`
Professional AI optimization with auto-save and insights.
```json
{
  "prompt": "Your prompt text",
  "goals": ["clarity", "specificity"],
  "ai_context": "llm_interaction" // Optional: Auto-detected
}
```
### `detect_ai_context`
Detects the AI context for a given prompt using backend analysis.
### `create_template` / `update_template`
Manage your optimization templates programmatically.
### `search_templates`
Search your library with AI-aware filtering.
### `get_quota_status`
Check your current subscription and quota usage.
### `get_optimization_insights`
Get advanced Bayesian analysis (if enabled).
---
## 🎛️ **Advanced Model Configuration**
Want to use your own AI models? Configure them in the [WebUI Dashboard](https://promptoptimizer-blog.vercel.app/dashboard) and the MCP server will automatically use them!
1.  **Configure in WebUI**: Add your OpenRouter API Key and select models (e.g., Claude 3.5 Sonnet, GPT-4o).
2.  **Use NPM Package**: No config changes needed! The server fetches your preferences.
**Benefits:**
*   ✅ **Cost Control**: Pay for your own OpenRouter usage.
*   ✅ **Privacy**: Data goes through your own account.
*   ✅ **Consistency**: Same models across WebUI and MCP.
---
## 📞 **Support & Resources**
- 📚 **Documentation**: [promptoptimizer-blog.vercel.app/docs](https://promptoptimizer-blog.vercel.app/docs)
- 📊 **Dashboard**: [promptoptimizer-blog.vercel.app/dashboard](https://promptoptimizer-blog.vercel.app/dashboard)
- 🐛 **Issues**: [GitHub Issues](https://github.com/nivlewd1/prompt-optimizer/issues)
- 📧 **Support**: support@promptoptimizer.help
---
**Made with ❤️ by the Prompt Optimizer Team**  
*Transforming AI interactions through professional prompt engineering*
[![NPM Package](https://img.shields.io/npm/v/mcp-prompt-optimizer)](https://www.npmjs.com/package/mcp-prompt-optimizer) [![Get Started](https://img.shields.io/badge/Get%20Started-Free%20Trial-green)](https://promptoptimizer-blog.vercel.app/pricing)
