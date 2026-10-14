# MCP Package Documentation - mcp-prompt-optimizer

## Overview

The **mcp-prompt-optimizer** package connects MCP clients to the Prompt Optimizer backend for prompt optimization (77 optimization goals), a template library, and Context Engineering tools.

## Package Information

**Package**: [`mcp-prompt-optimizer`](https://www.npmjs.com/package/mcp-prompt-optimizer)  
**Version**: Latest (see npm)  
**License**: Commercial Subscription  
**Source**: [nivlewd1/mcp-prompt-optimizer-npm](https://github.com/nivlewd1/mcp-prompt-optimizer-npm). The `mcp-package/` directory in this repository is an older snapshot (v3.1.1) and does not match the commands below.  
**Homepage**: [promptoptimizer.xyz](https://promptoptimizer.xyz)

## Quick Installation

```bash
# Install globally
npm install -g mcp-prompt-optimizer

# Connect your MCP client (writes the client config and your API key)
npx mcp-prompt-optimizer connect

# Check your key and plan
npx mcp-prompt-optimizer validate-key
npx mcp-prompt-optimizer check-status
```

You need an API key from [promptoptimizer.xyz/pricing](https://promptoptimizer.xyz/pricing). The Free plan needs no credit card.

## MCP Client Configuration

`connect` writes this for you. To add it by hand, put the server in your client's MCP configuration and set your API key in `env`:

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

Where the file lives:
- **Claude Desktop**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS), `%APPDATA%\Claude\claude_desktop_config.json` (Windows), `~/.config/Claude/claude_desktop_config.json` (Linux).
- **Cursor**: `~/.cursor/mcp.json`.
- **Other clients** (Windsurf, Cline, etc.): use the MCP settings of that client; the JSON above is the same.

We recommend `npx` with an `args` array, as above, so the client always starts the installed package the same way.

## Available MCP Tools

### `optimize_prompt`
Optimize a prompt with context-aware techniques.

**Parameters:**
- `prompt` (required): The prompt text to optimize
- `goals` (optional): Array of optimization goals (default: `["clarity"]`)
- `ai_context` (optional): Context for optimization (code_generation, human_communication, etc.); auto-detected if omitted

**Example:**
```json
{
  "prompt": "Write me some code for a login system",
  "goals": ["clarity", "technical_accuracy", "specificity", "role_prompting"],
  "ai_context": "code_generation"
}
```

### `list_recent_templates`
List your most recently saved optimization templates, sorted by creation date.

**Parameters:**
- `limit` (optional): Number of templates to return, 1-20 (default: 10)

### `search_templates`
Search your saved template library with AI-aware filtering.

**Parameters:**
- `query` (optional): Search term to filter templates by content or title
- `ai_context` (optional): Filter by AI context type
- `sophistication_level` (optional): Filter by template sophistication level
- `complexity_level` (optional): Filter by template complexity level
- `optimization_strategy` (optional): Filter by optimization strategy used
- `limit` (optional): Number of results, 1-20 (default: 5)
- `page`, `sort_by`, `sort_order` (optional): Pagination and ordering

### `get_template`
Retrieve a specific template by its ID.

**Parameters:**
- `template_id` (required): The ID of the template to retrieve

### `create_template` / `update_template` / `delete_template`
Full CRUD on your saved templates. Your MCP client's tool listing shows the exact parameters.

This is a partial list: the package registers 20+ tools, including `generate_agent_sop`, `generate_skill_package`, `transform_for_framework`, `get_ce_quota_status`, `run_quick_evaluation`, `compile_prompt` and `get_prompt_by_slug`. Your MCP client's tool listing is the authoritative, always-current source.

## Optimization Goals (77)

Goals are passed as strings in the `goals` array. A representative sample:

### **Core Enhancement**
- `clarity` - Crystal-clear communication and understanding
- `conciseness` - Efficient token usage while preserving meaning
- `specificity` - Detailed requirements and reduced ambiguity
- `actionability` - Direct, executable instructions
- `structure` - Logical organization and flow
- `contextual_relevance` - Perfect context alignment
- `linguistic_precision` - Exact language refinement
- `holistic_effectiveness` - Comprehensive optimization

### **Technical Precision**
- `technical_accuracy` - Precise technical terminology and correctness
- `technical_precision` - Exact technical specifications
- `code_review_quality` - Programming-specific review enhancements
- `debugging_assistance` - Error diagnosis and troubleshooting
- `systematic_approach` - Structured, methodical problem-solving

### **AI Model Compatibility**
- `ai_model_compatibility` - Optimized for specific AI models
- `parameter_preservation` - Maintain critical prompt parameters
- `token_efficiency` - Maximize information per token
- `context_specificity` - Efficient use of context limits

### **Communication & Structure**
- `professional_tone` - Business-appropriate language
- `persuasive_enhancement` - Stronger argumentation and framing
- `output_formatting` - Structured response optimization
- `step_by_step_guidance` - Sequential, actionable instructions
- `role_prompting` - Persona and framing enhancement

### **Depth & Analysis**
- `critical_thinking` - Deeper analytical framing
- `comprehensive_analysis` - Broader coverage of a topic
- `example_integration` - Concrete examples woven into the prompt
- `expertise_injection` - Domain-expert framing

This is a subset of the full goal list — see [promptoptimizer.xyz/documentation](https://promptoptimizer.xyz/documentation) for the complete set.

## Subscription Plans

### **Free** - $0/month
- 20 optimizations/month, no credit card required
- Default model
- Context Engineering: 3 basic SOPs and 1 full skill package a month (Claude Code and Ollama targets)

### **Pro** - $19/month
- 500 optimizations/month
- Model choice (OpenRouter)
- Context Engineering: 3 full skill builds a month, advanced steps and the other agent targets

### **Enterprise** - Custom
- Custom optimization volume and Context Engineering allowance
- Team features, shared quotas

## Commands

```bash
# Start the MCP server (your MCP client does this)
mcp-prompt-optimizer

# Connect an MCP client: writes the client config and your API key
mcp-prompt-optimizer connect

# Validate your API key
mcp-prompt-optimizer validate-key

# Show your plan and usage
mcp-prompt-optimizer check-status

# Clear the local cache
mcp-prompt-optimizer clear-cache

# Run diagnostics
mcp-prompt-optimizer diagnose

# Help and version
mcp-prompt-optimizer --help
mcp-prompt-optimizer --version
```

### Environment Variables

- `OPTIMIZER_API_KEY`: your API key (set by `connect` in your client's config)
- `OPTIMIZER_BACKEND_URL`: override the backend URL
- `OPTIMIZER_REQUEST_TIMEOUT`: request timeout
- `OPTIMIZER_DEV_MODE`: enable development behaviour

## Template Management

Optimizations that produce a result are saved to your template library automatically. A result is not saved when it came from a fallback path, has very low confidence, or leaves the prompt unchanged. Use `list_recent_templates`, `search_templates` and `get_template` to work with them.

## Troubleshooting

### Installation Issues

```bash
# Clear the npm cache and reinstall
npm cache clean --force
npm uninstall -g mcp-prompt-optimizer
npm install -g mcp-prompt-optimizer

# Verify installation
npm list -g | grep mcp-prompt-optimizer
```

### Configuration and API Issues

```bash
# Re-run the connect wizard
npx mcp-prompt-optimizer connect

# Check that your key is accepted, and your plan
npx mcp-prompt-optimizer validate-key
npx mcp-prompt-optimizer check-status

# Run diagnostics
npx mcp-prompt-optimizer diagnose

# Check that the API is reachable
curl https://p01--project-optimizer--fvmrdk8m9k9j.code.run/health
```

### Common Error Solutions

#### "Command not found: mcp-prompt-optimizer"
```bash
# Check if the package is installed globally
npm list -g mcp-prompt-optimizer

# If not, install it globally
npm install -g mcp-prompt-optimizer

# Check the npm global path
npm config get prefix
```

#### "Invalid API key" Error
1. Run `npx mcp-prompt-optimizer validate-key`.
2. Check that your key starts with `sk-opt-`, `sk-team-` or `sk-local-`.
3. Check your plan at [promptoptimizer.xyz/dashboard](https://promptoptimizer.xyz/dashboard).

#### MCP Client Not Connecting
1. Verify the JSON syntax of your MCP configuration.
2. Make sure `OPTIMIZER_API_KEY` is set in the server's `env`.
3. Restart your MCP client after configuration changes.
4. Run `npx mcp-prompt-optimizer diagnose`.

## Security

- **Transport**: All requests use HTTPS.
- **API key**: Sent in the `X-API-Key` header and stored in your MCP client's configuration; keep that file private.
- **Data Privacy**: Saved optimizations go to your own template library and are not shared with other users or used to train models.
- **Compliance Posture**: Designed around GDPR/CCPA principles and OWASP guidance; not formally certified (see [SECURITY.md](./SECURITY.md#compliance-posture))

## Support

- 📚 **Documentation**: [promptoptimizer.xyz/documentation](https://promptoptimizer.xyz/documentation)
- 🐛 **GitHub Issues**: [Report bugs and feature requests](https://github.com/nivlewd1/prompt-optimizer/issues)
- 📧 **Email Support**: support@promptoptimizer.xyz

---

**Ready to try it?** [Get started](https://promptoptimizer.xyz/pricing)
