# MCP Package Documentation

## Overview

The Prompt Optimizer provides **two complementary NPM packages** for Model Context Protocol (MCP) integration, offering both cloud-powered and local privacy-first optimization capabilities. These packages provide seamless access to prompt optimization directly within MCP-compatible clients like Claude Desktop, Cursor, and Windsurf.

## Package Information

### Cloud Package - [`mcp-prompt-optimizer`](https://www.npmjs.com/package/mcp-prompt-optimizer)
- **Version**: Latest
- **License**: Commercial Subscription
- **Features**: Cloud optimization, team collaboration, advanced analytics
- **Requires**: Active subscription and API key

### Local Package - [`mcp-prompt-optimizer-local`](https://www.npmjs.com/package/mcp-prompt-optimizer-local)
- **Version**: Latest  
- **License**: Freemium (Basic free, Pro $19.99 one-time)
- **Features**: Privacy-first local processing, binary optimization
- **Requires**: Local license (Basic or Pro)

## Installation

### Cloud Package Installation

```bash
# Global installation (recommended)
npm install -g mcp-prompt-optimizer

# Local installation
npm install mcp-prompt-optimizer
```

### Local Package Installation

```bash
# Global installation (recommended)
npm install -g mcp-prompt-optimizer-local

# Local installation
npm install mcp-prompt-optimizer-local
```

## Configuration

### Cloud Package Setup

```bash
# Initial setup with API key
mcp-prompt-optimizer --setup

# Test connection
mcp-prompt-optimizer --test
```

Configuration is stored at:
- **Windows**: `%USERPROFILE%\.prompt-optimizer\config.json`
- **macOS/Linux**: `~/.prompt-optimizer/config.json`

```json
{
  "apiKey": "sk-opt-your-key-here",
  "backendUrl": "https://p01--project-optimizer--fvrdk8m9k9j.code.run",
  "teamId": "team_123",
  "updatedAt": "2025-07-11T12:00:00.000Z"
}
```

### Local Package Setup

```bash
# Generate Basic license (free, 5 daily optimizations)
mcp-prompt-optimizer-local --license

# Upgrade to Pro license ($19.99, unlimited)
mcp-prompt-optimizer-local --upgrade

# Check license status
mcp-prompt-optimizer-local --license-status
```

Configuration is stored at:
- **Windows**: `%USERPROFILE%\.prompt-optimizer-local\config.json`
- **macOS/Linux**: `~/.prompt-optimizer-local/config.json`

```json
{
  "licenseKey": "sk-local-pro-your-key",
  "licenseType": "pro",
  "dailyQuota": "unlimited",
  "offlineMode": false,
  "binaryPath": "/path/to/binaries"
}
```

## MCP Client Integration

### ✅ CORRECT Configuration Examples

#### **Claude Desktop** (`~/.claude/claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "prompt-optimizer": {
      "command": "npx",
      "args": ["mcp-prompt-optimizer"]
    },
    "prompt-optimizer-local": {
      "command": "npx",
      "args": ["mcp-prompt-optimizer-local"]
    }
  }
}
```

#### **Cursor** (`~/.cursor/mcp.json`)

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

#### **Windsurf**

```json
{
  "mcpServers": {
    "prompt-optimizer-local": {
      "command": "npx",
      "args": ["mcp-prompt-optimizer-local"]
    }
  }
}
```

### ❌ WRONG Configuration (DO NOT USE)

```json
{
  "mcpServers": {
    "prompt-optimizer": {
      "command": "mcp-prompt-optimizer-local"
    }
  }
}
```

**The above configuration is INCORRECT and will not work!**

## Available Tools

### Cloud Package Tools (`mcp-prompt-optimizer`)

#### `optimize_prompt`
Cloud-powered optimization with team collaboration features and 50+ goals.

**Parameters**:
- `prompt` (required): The prompt text to optimize
- `goals` (optional): Array of optimization goals (50+ available)
- `ai_context` (optional): Context for optimization (code_generation, human_communication, etc.)
- `stream` (optional): Whether to stream the response (default: false)

**Example Usage**:
```
Use the optimize_prompt tool to improve this prompt:
"Write me some code for a login system"

Goals: ["clarity", "technical_accuracy", "specificity", "security_enhancement"]
```

#### `list_saved_templates`
Browse team-shared optimization templates with metadata.

#### `search_templates`
Find relevant templates by keywords, goals, or content.

**Parameters**:
- `query` (optional): Search keywords
- `goals` (optional): Filter by optimization goals
- `limit` (optional): Number of results (default: 10)

#### `get_template`
Retrieve specific template details and analytics.

#### `get_template_stats`
Analytics for template usage and effectiveness metrics.

#### `use_template_as_base`
Start optimization from a proven template foundation.

### Local Package Tools (`mcp-prompt-optimizer-local`)

#### `optimize_prompt`
Privacy-first local optimization with binary processing.

**Parameters**:
- `prompt` (required): The prompt text to optimize
- `goals` (optional): Array of optimization goals (25 Basic, 50+ Pro)
- `local_only` (optional): Force local processing (default: true)

**Example Usage**:
```
Use the optimize_prompt tool to improve this prompt locally:
"Help me write a database query"

Goals: ["database_optimization", "technical_precision"]
```

#### `check_license`
Verify local license status and remaining quota.

#### `upgrade_license`
Upgrade from Basic to Pro license ($19.99 one-time).

## 50+ Optimization Goals

### **Core Enhancement** (Available in all tiers)
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

### **Technical Precision** (Pro/Creator/Innovator)
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

### **AI Model Compatibility** (Pro/Creator/Innovator)
- `ai_model_compatibility` - Optimized for specific AI models
- `parameter_preservation` - Maintain critical prompt parameters
- `token_efficiency` - Maximize information per token
- `context_window_optimization` - Efficient use of context limits
- `model_specific_formatting` - Tailored for GPT/Claude/other models
- `streaming_optimization` - Enhanced for real-time responses
- `multimodal_enhancement` - Image + text optimization
- `cross_platform_compatibility` - Universal MCP client support

### **Domain-Specific Enhancement** (Pro/Creator/Innovator)
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

### **Advanced Techniques** (Pro/Creator/Innovator)
- `prompt_chaining` - Multi-step prompt sequences
- `few_shot_optimization` - Example-based learning enhancement
- `chain_of_thought` - Step-by-step reasoning optimization
- `role_play_enhancement` - Character and persona development
- `constraint_satisfaction` - Working within specific limitations
- `output_formatting` - Structured response optimization
- `error_handling` - Robust failure mode management
- `edge_case_coverage` - Comprehensive scenario handling

### **Emerging Capabilities** (Innovator)
- `real_time_adaptation` - Dynamic optimization based on usage
- `collaborative_enhancement` - Team-optimized prompts
- `enterprise_compliance` - Regulatory and compliance alignment
- `multilingual_optimization` - Cross-language enhancement
- `accessibility_enhancement` - Inclusive design principles
- `sustainability_focus` - Environmental and ethical considerations

### **Specialized Applications** (Pro/Creator/Innovator)
- `data_analysis` - Statistical and analytical enhancements
- `project_management` - Planning and coordination optimization
- `customer_service` - Support and communication enhancement
- `content_moderation` - Safety and appropriateness focus
- `knowledge_extraction` - Information retrieval optimization
- `decision_support` - Choice and evaluation assistance

## Template Management

### Cloud Package Templates
All cloud optimizations are automatically saved as templates with rich metadata:

```json
{
  "id": "template_abc123",
  "saved_at_utc": "2025-07-11T12:00:00.000Z",
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

### Local Package Templates
Local optimizations can be saved locally with privacy protection:

```json
{
  "id": "local_template_xyz789",
  "saved_at_utc": "2025-07-11T12:00:00.000Z",
  "license_type": "pro",
  "confidence_score": 0.89,
  "original_prompt": "Your original prompt",
  "optimized_prompt": "The improved version",
  "optimization_goals": ["clarity", "database_optimization"],
  "local_metadata": {
    "binary_version": "1.2.3",
    "optimization_time_ms": 850,
    "privacy_mode": true
  }
}
```

## Commands

### Cloud Package Commands

```bash
# Start the MCP server (usually called by MCP client)
mcp-prompt-optimizer

# Configure API key
mcp-prompt-optimizer --setup

# Test functionality
mcp-prompt-optimizer --test

# Show help
mcp-prompt-optimizer --help

# Show version
mcp-prompt-optimizer --version

# Test MCP connectivity
mcp-prompt-optimizer --test-mcp
```

### Local Package Commands

```bash
# Start the MCP server (usually called by MCP client)
mcp-prompt-optimizer-local

# Generate Basic license (free)
mcp-prompt-optimizer-local --license

# Upgrade to Pro license
mcp-prompt-optimizer-local --upgrade

# Check license status
mcp-prompt-optimizer-local --license-status

# Update optimization binaries
mcp-prompt-optimizer-local --update-binaries

# Test local optimization
mcp-prompt-optimizer-local --test

# Show help
mcp-prompt-optimizer-local --help

# Show version
mcp-prompt-optimizer-local --version
```

## Environment Variables

### Cloud Package Environment Variables

Override configuration with environment variables:

- `PROMPT_OPTIMIZER_API_KEY`: Override stored API key
- `PROMPT_OPTIMIZER_BACKEND_URL`: Override backend URL
- `PROMPT_OPTIMIZER_TEAM_ID`: Override team ID
- `NODE_ENV`: Set to 'development' for debug logging

```bash
PROMPT_OPTIMIZER_API_KEY=sk-opt-your-key mcp-prompt-optimizer
```

### Local Package Environment Variables

- `PROMPT_OPTIMIZER_LOCAL_LICENSE`: Override stored license
- `PROMPT_OPTIMIZER_LOCAL_BINARY_PATH`: Override binary path
- `PROMPT_OPTIMIZER_LOCAL_OFFLINE_MODE`: Enable offline mode
- `NODE_ENV`: Set to 'development' for debug logging

```bash
PROMPT_OPTIMIZER_LOCAL_LICENSE=sk-local-pro-your-key mcp-prompt-optimizer-local
```

## Troubleshooting

### Cloud Package Issues

#### API Key Problems
```bash
# Reconfigure your API key
mcp-prompt-optimizer --setup

# Verify API key format
echo $PROMPT_OPTIMIZER_API_KEY | grep "^sk-opt-"

# Test API connectivity
curl -H "X-API-Key: $PROMPT_OPTIMIZER_API_KEY" \
     https://p01--project-optimizer--fvrdk8m9k9j.code.run/health
```

#### Connection Issues
1. Verify internet connection
2. Check API key validity at [dashboard](https://promptoptimizer-blog.vercel.app/dashboard)
3. Ensure subscription is active
4. Test backend: `curl https://p01--project-optimizer--fvrdk8m9k9j.code.run/health`

### Local Package Issues

#### License Problems
```bash
# Check license status
mcp-prompt-optimizer-local --license-status

# Regenerate Basic license
mcp-prompt-optimizer-local --license --force

# Upgrade to Pro
mcp-prompt-optimizer-local --upgrade
```

#### Binary Issues
```bash
# Update binaries
mcp-prompt-optimizer-local --update-binaries

# Check platform compatibility
mcp-prompt-optimizer-local --check-platform

# Force binary reinstall
mcp-prompt-optimizer-local --reinstall-binaries
```

### MCP Client Issues

#### Configuration Problems
```bash
# ❌ Common WRONG configurations:
# {"command": "mcp-prompt-optimizer-local"}
# {"command": "mcp-prompt-optimizer"}

# ✅ CORRECT configurations:
# {"command": "npx", "args": ["mcp-prompt-optimizer"]}
# {"command": "npx", "args": ["mcp-prompt-optimizer-local"]}

# Validate JSON configuration
node -e "console.log(JSON.parse(require('fs').readFileSync('~/.claude/claude_desktop_config.json')))"

# Test MCP connectivity
npx mcp-prompt-optimizer --test-mcp
npx mcp-prompt-optimizer-local --test-mcp
```

#### Installation Problems
1. Verify Node.js installation: `node --version`
2. Check global packages: `npm list -g | grep mcp-prompt-optimizer`
3. Restart MCP client after configuration changes
4. Clear npm cache if needed: `npm cache clean --force`

## Security

### Cloud Package Security
- API keys stored locally and encrypted
- All communication uses HTTPS/TLS
- No prompt data stored permanently (except user-controlled templates)
- Full audit trail available in dashboard
- Enterprise security standards compliance
- Multi-tenant security isolation

### Local Package Security
- Complete privacy: no data transmission during optimization
- Local license validation with secure offline operation
- Encrypted configuration files
- Signed and verified binary executables
- Local storage only - no cloud data storage
- Open-source security audit availability

## Performance

### Cloud Package Performance
- Sub-50ms average response times
- Global CDN for optimal latency
- Auto-scaling based on demand
- Real-time streaming optimization
- Team collaboration features
- Advanced analytics and insights

### Local Package Performance
- Binary optimization for speed
- Platform-specific compiled optimizers
- Python fallback for compatibility
- Offline operation capabilities
- Local caching for license validation
- No network latency dependencies

## Licensing Comparison

| Feature | Local Basic (Free) | Local Pro ($19.99) | Cloud Explorer ($2.99/mo) | Cloud Creator ($25.99/mo) | Cloud Innovator ($69.99/mo) |
|---------|-------------------|-------------------|---------------------------|--------------------------|----------------------------|
| **Daily/Monthly Optimizations** | 5/day | Unlimited | 5,000/month | 18,000/month | 75,000/month |
| **Optimization Goals** | 25 core | 50+ complete | 25 core | 50+ complete | 50+ complete |
| **Privacy** | Complete | Complete | Standard | Standard | Standard |
| **Team Features** | ❌ | ❌ | ❌ | ✅ 2 members | ✅ 5 members |
| **API Keys** | ❌ | ❌ | 1 | 3 | 10 |
| **Template Analytics** | ❌ | Basic | Basic | Advanced | Enterprise |
| **Support** | Community | Community | Standard | Priority | Premium |

## Support

- 📚 **Documentation**: [promptoptimizer-blog.vercel.app/docs](https://promptoptimizer-blog.vercel.app/docs)
- 🎫 **Support Portal**: [promptoptimizer-blog.vercel.app/support](https://promptoptimizer-blog.vercel.app/support)
- 🐛 **GitHub Issues**: [Report bugs and feature requests](https://github.com/nivlewd1/prompt-optimizer/issues)
- 💬 **Discord Community**: [Join our community](https://discord.gg/prompt-optimizer)
- 📧 **Email Support**: promptoptimizer.help@gmail.com

---

**Note**: Both packages connect to sophisticated backend services. The optimization algorithms and core processing logic are proprietary and not included in this open-source repository. Choose the package that best fits your privacy requirements and collaboration needs.