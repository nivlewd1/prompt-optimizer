# MCP Package Documentation

## Overview

The `mcp-prompt-optimizer` NPM package provides Model Context Protocol (MCP) integration for the Prompt Optimizer service. This allows seamless access to prompt optimization capabilities directly within MCP-compatible clients like Claude Desktop, Cursor, and Windsurf.

## Package Information

- **NPM Package**: [`mcp-prompt-optimizer`](https://www.npmjs.com/package/mcp-prompt-optimizer)
- **Version**: 1.0.1
- **Author**: Prompt Optimizer Team
- **License**: Commercial License

## Installation

### Global Installation (Recommended)

```bash
npm install -g mcp-prompt-optimizer
```

### Local Installation

```bash
npm install mcp-prompt-optimizer
```

## Configuration

### Initial Setup

```bash
mcp-prompt-optimizer --setup
```

This will prompt you to enter your API key and configure the connection to the backend service.

### Manual Configuration

Configuration is stored at:
- **Windows**: `%USERPROFILE%\.prompt-optimizer\config.json`
- **macOS/Linux**: `~/.prompt-optimizer/config.json`

```json
{
  "apiKey": "sk-opt-your-key-here",
  "backendUrl": "https://p01--project-optimizer--fvrdk8m9k9j.code.run",
  "updatedAt": "2025-06-05T12:00:00.000Z"
}
```

## MCP Client Integration

### Claude Desktop

Add to `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "prompt-optimizer": {
      "command": "npx",
      "args": ["mcp-prompt-optimizer"]
    }
  }
}
```

### Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "prompt-optimizer": {
      "command": "npx",
      "args": ["mcp-prompt-optimizer"]
    }
  }
}
```

### Windsurf

Configure through Windsurf settings or add to configuration file:

```json
{
  "mcpServers": {
    "prompt-optimizer": {
      "command": "npx",
      "args": ["mcp-prompt-optimizer"]
    }
  }
}
```

## Available Tools

### optimize_prompt

Optimizes a given prompt based on specified goals.

**Parameters**:
- `prompt` (required): The prompt text to optimize
- `goals` (optional): Array of optimization goals
- `stream` (optional): Whether to stream the response (default: false)

**Example Usage**:

```
Please use the optimize_prompt tool to improve this prompt:
"Write me some code"

Use goals: ["clarity", "specificity", "technical_accuracy"]
```

**Response**:
```json
{
  "optimized_prompt": "Create a well-documented code solution with specific requirements...",
  "confidence_score": 0.87,
  "optimization_goals": ["clarity", "specificity", "technical_accuracy"],
  "quota_remaining": 195,
  "template_saved": true
}
```

## Optimization Goals

- **clarity** - Make the prompt clearer and more understandable
- **conciseness** - Remove unnecessary words while preserving meaning
- **technical_accuracy** - Improve technical precision and correctness
- **contextual_relevance** - Better alignment with context and purpose
- **specificity** - Add specific details and reduce ambiguity
- **actionability** - Make the prompt more actionable and directive
- **structure** - Improve organization and logical flow
- **technical_precision** - Enhance exactness of technical terms
- **linguistic_precision** - Refine language for exact meaning
- **holistic_effectiveness** - Overall optimization for best results

## Template Management

All optimizations are automatically saved as templates with rich metadata:

```json
{
  "saved_at_utc": "2025-06-05T12:00:00.000Z",
  "optimization_tier": "LLM",
  "confidence_score": 0.95,
  "original_prompt": "Your original prompt",
  "optimized_prompt": "The improved version",
  "optimization_goals": ["clarity", "technical_accuracy"],
  "context_snapshot": {
    "domain": "General",
    "target_audience": "Default"
  },
  "request_id": "unique-request-identifier",
  "request_metadata": {
    "api_request_type": "POST_non_streaming",
    "user_id": "your-user-id"
  },
  "model_optimized_with": "openai/gpt-4o-mini"
}
```

## Commands

```bash
# Start the MCP server (usually called by MCP client)
mcp-prompt-optimizer

# Configure API key
mcp-prompt-optimizer --setup

# Show help
mcp-prompt-optimizer --help

# Show version
mcp-prompt-optimizer --version

# Test package functionality
npm test
```

## Environment Variables

Override configuration with environment variables:

- `PROMPT_OPTIMIZER_API_KEY`: Override stored API key
- `PROMPT_OPTIMIZER_BACKEND_URL`: Override backend URL
- `NODE_ENV`: Set to 'development' for debug logging

```bash
PROMPT_OPTIMIZER_API_KEY=sk-opt-your-key mcp-prompt-optimizer
```

## Troubleshooting

### API Key Issues

```bash
# Reconfigure your API key
mcp-prompt-optimizer --setup
```

### Connection Issues

1. Verify internet connection
2. Check API key validity at [dashboard](https://promptoptimizer-blog.vercel.app/dashboard)
3. Ensure subscription is active
4. Test backend: `curl https://p01--project-optimizer--fvrdk8m9k9j.code.run/health`

### MCP Client Issues

1. Verify Node.js installation: `node --version`
2. Check global package: `npm list -g mcp-prompt-optimizer`
3. Restart MCP client after configuration changes
4. Validate JSON configuration syntax

## Security

- API keys stored locally and encrypted
- All communication uses HTTPS
- No prompt data stored permanently (except user-controlled templates)
- Full audit trail available in dashboard
- Enterprise security standards compliance

## Support

- 📚 [Documentation](https://promptoptimizer-blog.vercel.app/docs)
- 🎫 [Support Portal](https://promptoptimizer-blog.vercel.app/support)
- 🐛 [GitHub Issues](https://github.com/nivlewd1/prompt-optimizer/issues)
- 💬 [Discord Community](https://discord.gg/prompt-optimizer)

---

**Note**: This package connects to a production backend service. The optimization algorithms and core processing logic are proprietary and not included in this open-source repository.