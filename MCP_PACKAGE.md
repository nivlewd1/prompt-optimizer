# MCP Package Documentation - mcp-prompt-optimizer

## Overview

The **mcp-prompt-optimizer** package provides seamless Model Context Protocol (MCP) integration for professional prompt optimization. Transform your prompts with 50+ specialized optimization goals, enterprise-grade analytics, and team collaboration features.

## Package Information

**Package**: [`mcp-prompt-optimizer`](https://www.npmjs.com/package/mcp-prompt-optimizer)  
**Version**: Latest  
**License**: Commercial Subscription  
**Repository**: [GitHub](https://github.com/nivlewd1/prompt-optimizer)  
**Homepage**: [promptoptimizer-blog.vercel.app](https://promptoptimizer-blog.vercel.app)

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
Transform your prompts with professional optimization techniques using 50+ specialized goals.

**Parameters:**
- `prompt` (required): The prompt text to optimize
- `goals` (optional): Array of optimization goals
- `ai_context` (optional): Context for optimization (code_generation, human_communication, etc.)
- `stream` (optional): Whether to stream the response (default: false)

**Example:**
```json
{
  "prompt": "Write me some code for a login system",
  "goals": ["clarity", "technical_accuracy", "specificity", "security_enhancement"],
  "ai_context": "code_generation"
}
```

### `list_saved_templates`
Browse your saved optimization templates with metadata and analytics.

**Parameters:**
- `category` (optional): Filter by template category
- `limit` (optional): Number of results (default: 20)

### `search_templates`
Find relevant templates by keywords, goals, or content.

**Parameters:**
- `query` (required): Search keywords
- `category` (optional): Filter by template category
- `limit` (optional): Number of results (default: 10)

### `get_template`
Retrieve specific template details and usage analytics.

**Parameters:**
- `template_id` (required): Template identifier
- `include_metadata` (optional): Include enhanced metadata (default: true)

### `get_template_stats`
Get comprehensive analytics for template usage and effectiveness.

**Parameters:**
- `detailed` (optional): Include detailed analytics (default: false)

### `use_template_as_base`
Start optimization from a proven template foundation with optional modifications.

**Parameters:**
- `template_id` (required): Template to use as base
- `modifications` (optional): Additional requirements
- `new_goals` (optional): Override template goals

## Optimization Goals (50+)

### **Core Enhancement** (10 goals)
- `clarity` - Crystal-clear communication and understanding
- `conciseness` - Efficient token usage while preserving meaning
- `specificity` - Detailed requirements and reduced ambiguity
- `actionability` - Direct, executable instructions
- `structure` - Logical organization and flow
- `contextual_relevance` - Perfect context alignment
- `linguistic_precision` - Exact language refinement
- `holistic_effectiveness` - Comprehensive optimization
- `goal_synergy` - Intelligent combination of multiple goals
- `workflow_optimization` - Enhanced for development workflows

### **Technical Precision** (12 goals)
- `technical_accuracy` - Precise technical terminology and correctness
- `technical_precision` - Exact technical specifications
- `code_optimization` - Programming-specific enhancements
- `api_documentation` - REST/GraphQL API specifications
- `database_optimization` - SQL and database query enhancement
- `system_design` - Architecture and infrastructure focus
- `security_enhancement` - Cybersecurity and safety improvements
- `performance_optimization` - Speed and efficiency focus
- `debugging_enhancement` - Error diagnosis and troubleshooting
- `testing_optimization` - Quality assurance and testing improvements
- `deployment_optimization` - CI/CD and production deployment focus
- `monitoring_enhancement` - Observability and logging improvements

### **AI Model Compatibility** (8 goals)
- `ai_model_compatibility` - Optimized for specific AI models
- `parameter_preservation` - Maintain critical prompt parameters
- `token_efficiency` - Maximize information per token
- `context_window_optimization` - Efficient use of context limits
- `model_specific_formatting` - Tailored for GPT/Claude/other models
- `streaming_optimization` - Enhanced for real-time responses
- `multimodal_enhancement` - Image + text optimization
- `cross_platform_compatibility` - Universal MCP client support

### **Domain-Specific Enhancement** (10 goals)
- `business_communication` - Professional business language
- `academic_writing` - Scholarly and research-focused
- `creative_writing` - Enhanced creativity and storytelling
- `legal_precision` - Legal terminology and accuracy
- `medical_accuracy` - Healthcare and medical precision
- `scientific_research` - Research methodology and scientific writing
- `financial_analysis` - Economic and financial terminology
- `educational_content` - Teaching and learning optimization
- `marketing_copy` - Persuasive and engaging content
- `technical_documentation` - User manuals and technical guides

### **Advanced Techniques** (8 goals)
- `prompt_chaining` - Multi-step prompt sequences
- `few_shot_optimization` - Example-based learning enhancement
- `chain_of_thought` - Step-by-step reasoning optimization
- `role_play_enhancement` - Character and persona development
- `constraint_satisfaction` - Working within specific limitations
- `output_formatting` - Structured response optimization
- `error_handling` - Robust failure mode management
- `edge_case_coverage` - Comprehensive scenario handling

### **Emerging Capabilities** (6 goals)
- `real_time_adaptation` - Dynamic optimization based on usage
- `collaborative_enhancement` - Team-optimized prompts
- `enterprise_compliance` - Regulatory and compliance alignment
- `multilingual_optimization` - Cross-language enhancement
- `accessibility_enhancement` - Inclusive design principles
- `sustainability_focus` - Environmental and ethical considerations

### **Specialized Applications** (6 goals)
- `data_analysis` - Statistical and analytical enhancements
- `project_management` - Planning and coordination optimization
- `customer_service` - Support and communication enhancement
- `content_moderation` - Safety and appropriateness focus
- `knowledge_extraction` - Information retrieval optimization
- `decision_support` - Choice and evaluation assistance

## Subscription Plans

### **Explorer** - $2.99/month
- 5,000 optimizations/month
- 1 API key
- Web dashboard access
- Core optimization goals (25 goals)
- Template history

### **Creator** - $25.99/month
- 18,000 optimizations/month
- Up to 3 API keys
- 2 team members
- All optimization goals (50+ goals)
- Template analytics
- Priority processing

### **Innovator** - $69.99/month
- 75,000 optimizations/month
- Up to 10 API keys
- 5 team members
- Advanced analytics dashboard
- Priority support
- Custom optimization models

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
# https://promptoptimizer-blog.vercel.app/dashboard
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
- **Data Privacy**: User prompts processed securely, not stored permanently
- **Compliance**: SOC 2, GDPR, and enterprise security standards
- **Zero Trust**: Multi-layered security architecture

## Performance

- **Sub-50ms Response Times**: Optimized for real-time workflows
- **Global CDN**: Minimal latency worldwide
- **Auto-scaling**: Handles demand spikes seamlessly
- **Streaming Support**: Real-time optimization updates
- **99.9% Uptime**: Enterprise-grade reliability
- **Smart Caching**: Intelligent template and result caching

## Support

- 📚 **Documentation**: [promptoptimizer-blog.vercel.app/docs](https://promptoptimizer-blog.vercel.app/docs)
- 🎫 **Support Portal**: [promptoptimizer-blog.vercel.app/support](https://promptoptimizer-blog.vercel.app/support)
- 🐛 **GitHub Issues**: [Report bugs and feature requests](https://github.com/nivlewd1/prompt-optimizer/issues)
- 📧 **Email Support**: promptoptimizer.help@gmail.com

### Response Time SLA
- **Explorer**: Standard support (12-24 hours)
- **Creator**: Priority support (6-12 hours)
- **Innovator**: Premium support (2-6 hours)
- **Enterprise**: Dedicated support with custom SLA

---

**Ready to transform your prompts?** [Get started today!](https://promptoptimizer-blog.vercel.app/pricing)