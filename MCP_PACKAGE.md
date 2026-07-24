# MCP Package Documentation - mcp-prompt-optimizer

## Overview

The **mcp-prompt-optimizer** package provides seamless Model Context Protocol (MCP) integration for professional prompt optimization. Transform your prompts with 70+ specialized optimization goals, template analytics, and team collaboration features.

## Package Information

**Package**: [`mcp-prompt-optimizer`](https://www.npmjs.com/package/mcp-prompt-optimizer)  
**Version**: Latest  
**License**: Commercial Subscription  
**Repository**: [GitHub](https://github.com/nivlewd1/prompt-optimizer)  
**Homepage**: [promptoptimizer.xyz](https://promptoptimizer.xyz)

## Quick Installation

```bash
# Install globally (recommended)
npm install -g mcp-prompt-optimizer

# Configure API key
mcp-prompt-optimizer --setup

# Test installation
mcp-prompt-optimizer --test
```

## MCP Client Configuration

### ✅ CORRECT Configuration

**For ALL MCP clients (Claude Desktop, Cursor, Windsurf, Cline, etc.):**

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

### Client-Specific Examples

#### **Claude Desktop** (`~/.claude/claude_desktop_config.json`)

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

#### **Cursor** (Settings → Extensions → MCP)

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

#### **Windsurf** (MCP Settings)

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

#### **Cline** (VS Code Extension)

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

### ❌ INCORRECT Configuration

```json
{
  "mcpServers": {
    "prompt-optimizer": {
      "command": "mcp-prompt-optimizer"
    }
  }
}
```

**Never use the package name directly as the command! Always use `npx` with the `args` array.**

## Available MCP Tools

### `optimize_prompt`
Transform your prompts with professional optimization techniques using 70+ specialized goals.

**Parameters:**
- `prompt` (required): The prompt text to optimize
- `goals` (optional): Array of optimization goals
- `ai_context` (optional): Context for optimization (code_generation, human_communication, etc.)
- `stream` (optional): Whether to stream the response (default: false)

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
Search your saved template library with AI-aware filtering and sophisticated template matching.

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
Full CRUD on your saved templates — see the tool's own inputSchema (returned via your MCP client's tool-listing) for exact parameters, since these accept the full template shape (title, prompts, goals, confidence score, tags, etc.).

This is a partial list — the package registers 20+ tools, including `generate_agent_sop`, `generate_skill_package`, `transform_for_framework`, `get_ce_quota_status`, `compile_prompt`, and `get_prompt_by_slug`. Your MCP client's tool listing is the authoritative, always-current source.

## Optimization Goals (77 and counting)

Goals are passed as strings in the `goals` array. A representative sample across the real categories:

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

This is a subset of the full goal list — see [promptoptimizer.xyz/documentation](https://promptoptimizer.xyz/documentation) for the complete, current set.

## Subscription Plans

### **Free** - $0/month
- 20 optimizations/month
- Validate fit, no credit card required

### **Pro** - $19/month
- 500 optimizations/month
- Full model configuration (OpenRouter)
- Context Engineering tools

### **Enterprise** - Custom
- Custom optimization volume
- Team features, shared quotas

## Commands

### Available Commands

```bash
# Start MCP server (called by MCP client)
mcp-prompt-optimizer

# Initial setup and API key configuration
mcp-prompt-optimizer --setup

# Test functionality and connectivity
mcp-prompt-optimizer --test

# Test MCP protocol connectivity
mcp-prompt-optimizer --test-mcp

# Show subscription and usage status
mcp-prompt-optimizer --status

# Display help information
mcp-prompt-optimizer --help

# Show version information
mcp-prompt-optimizer --version
```

### Environment Variables

Override configuration with environment variables:

- `PROMPT_OPTIMIZER_API_KEY`: Override stored API key
- `PROMPT_OPTIMIZER_BACKEND_URL`: Override backend URL
- `PROMPT_OPTIMIZER_TEAM_ID`: Override team ID
- `NODE_ENV`: Set to 'development' for debug logging

```bash
# Example usage with environment variable
PROMPT_OPTIMIZER_API_KEY=sk-opt-your-key mcp-prompt-optimizer
```

## Configuration

Configuration is stored at:
- **Windows**: `%USERPROFILE%\\.prompt-optimizer\\config.json`
- **macOS/Linux**: `~/.prompt-optimizer/config.json`

**Example config.json:**
```json
{
  "apiKey": "sk-opt-your-key-here",
  "backendUrl": "https://p01--project-optimizer--fvrdk8m9k9j.code.run",
  "teamId": "team_123",
  "updatedAt": "2025-08-13T12:00:00.000Z"
}
```

## Template Management

All optimizations are automatically saved as templates with rich metadata:

```json
{
  "id": "template_abc123",
  "saved_at_utc": "2025-08-13T12:00:00.000Z",
  "optimization_tier": "LLM",
  "confidence_score": 0.95,
  "original_prompt": "Your original prompt",
  "optimized_prompt": "The improved version",
  "optimization_goals": ["clarity", "technical_accuracy"],
  "context_snapshot": {
    "domain": "Software Development",
    "target_audience": "Developers"
  },
  "request_id": "unique-request-identifier",
  "request_metadata": {
    "api_request_type": "POST_non_streaming",
    "user_id": "your-user-id",
    "team_id": "team_123"
  },
  "model_optimized_with": "openai/gpt-4o-mini",
  "usage_analytics": {
    "times_used": 15,
    "average_confidence": 0.87
  }
}
```

## Troubleshooting

### Installation Issues

```bash
# Clear npm cache
npm cache clean --force

# Reinstall package
npm uninstall -g mcp-prompt-optimizer
npm install -g mcp-prompt-optimizer

# Verify installation
npm list -g | grep mcp-prompt-optimizer
```

### Configuration Issues

```bash
# Validate MCP configuration JSON
node -e "console.log(JSON.parse(require('fs').readFileSync('~/.claude/claude_desktop_config.json')))"

# Test MCP connectivity
npx mcp-prompt-optimizer --test-mcp

# Reconfigure API key
mcp-prompt-optimizer --setup
```

### API Issues

```bash
# Verify API key format
echo $PROMPT_OPTIMIZER_API_KEY | grep "^sk-opt-"

# Test API connectivity
curl -H "X-API-Key: $PROMPT_OPTIMIZER_API_KEY" \
     https://p01--project-optimizer--fvrdk8m9k9j.code.run/api/v1/health

# Check subscription status
mcp-prompt-optimizer --status
```

### Common Error Solutions

#### "Command not found: mcp-prompt-optimizer"
```bash
# Check if package is installed globally
npm list -g mcp-prompt-optimizer

# If not installed, install globally
npm install -g mcp-prompt-optimizer

# Check npm global path
npm config get prefix
```

#### "Invalid API key" Error
```bash
# Reconfigure API key
mcp-prompt-optimizer --setup

# Verify key format (should start with sk-opt-)
echo $PROMPT_OPTIMIZER_API_KEY

# Check subscription status at dashboard
# https://promptoptimizer.xyz/dashboard
```

#### MCP Client Not Connecting
1. Verify JSON syntax in MCP configuration
2. Ensure using `npx` with `args` array format
3. Restart MCP client after configuration changes
4. Test with: `npx mcp-prompt-optimizer --test-mcp`

## Security

- **Enterprise Security**: Production-grade encryption and authentication
- **API Key Protection**: Secure local storage with encryption
- **Audit Trails**: Complete optimization history and usage tracking
- **Data Privacy**: Optimizations are saved to your own template library (see Template Management below) — never shared with other users or used to train models
- **Compliance Posture**: Designed around GDPR/CCPA principles and OWASP guidance; not formally certified (see [SECURITY.md](./SECURITY.md#compliance-posture))
- **Zero Trust**: Multi-layered security architecture

## Performance

- **Sub-50ms Response Times**: Optimized for real-time workflows
- **Global CDN**: Minimal latency worldwide
- **Auto-scaling**: Handles demand spikes seamlessly
- **Streaming Support**: Real-time optimization updates
- **99.9% Uptime**: Enterprise-grade reliability
- **Smart Caching**: Intelligent template and result caching

## Support

- 📚 **Documentation**: [promptoptimizer.xyz/documentation](https://promptoptimizer.xyz/documentation)
- 🐛 **GitHub Issues**: [Report bugs and feature requests](https://github.com/nivlewd1/prompt-optimizer/issues)
- 📧 **Email Support**: support@promptoptimizer.help

---

**Ready to transform your prompts?** [Get started today!](https://promptoptimizer.xyz/pricing)