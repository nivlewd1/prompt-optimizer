# Prompt Optimizer

A comprehensive prompt optimization platform offering both MCP (Model Context Protocol) integration and a REST API service for improving AI prompts across various optimization goals.

## 🚀 Components

This repository contains documentation and resources for:

1. **[MCP Server Package](#mcp-server-package)** - NPM package for Claude Desktop, Cursor, Windsurf integration
2. **[REST API Service](#rest-api-service)** - FastAPI backend for direct integration
3. **[Web Dashboard](#web-dashboard)** - Browser-based interface and management

---

## 📦 MCP Server Package

**Published on NPM**: [`mcp-prompt-optimizer`](https://www.npmjs.com/package/mcp-prompt-optimizer)

### Quick Start

```bash
# Install globally
npm install -g mcp-prompt-optimizer

# Setup your API key
mcp-prompt-optimizer --setup
```

### Features

- 🤖 **Universal MCP Support** - Works with Claude Desktop, Cursor, Windsurf, and any MCP-compatible client
- 🔐 **Secure API Key Authentication** - Uses your personal API key for secure access
- 🎯 **Advanced Optimization Goals** - Support for clarity, conciseness, technical accuracy, and more
- 📊 **Real-time Quota Tracking** - See your usage and remaining quota
- 💾 **Automatic Template Saving** - All optimizations saved with rich metadata for future reference
- 🚀 **Easy Setup** - Simple configuration process
- ⚡ **Production Backend** - Powered by enterprise-grade FastAPI deployment

### MCP Client Configuration

#### Claude Desktop

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

#### Cursor

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

#### Windsurf

Add via Windsurf settings:

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

### Usage Example

Once configured, use the `optimize_prompt` tool in your MCP client:

```
Please optimize this prompt using the optimize_prompt tool:
"Write me some code for a login system"

Use goals: ["clarity", "specificity", "technical_accuracy"]
```

Result:
```
Create a secure user authentication system with the following specifications:

## Requirements:
- Implement login functionality with username/email and password
- Include proper input validation and sanitization  
- Add password hashing using bcrypt or similar
- Implement session management
- Include error handling for invalid credentials
- Add rate limiting to prevent brute force attacks

## Deliverables:
- Backend authentication logic
- Frontend login form
- Database schema for user accounts
- Security best practices implementation

Confidence Score: 0.87
Quota Remaining: 195/200
```

---

## 🔗 REST API Service

**Production Endpoint**: `https://p01--project-optimizer--fvrdk8m9k9j.code.run`

### API Authentication

All API requests require an API key in the header:

```bash
X-API-Key: sk-opt-your-api-key-here
```

### Core Endpoint

**POST** `/api/v1/optimize`

```bash
curl -X POST "https://p01--project-optimizer--fvrdk8m9k9j.code.run/api/v1/optimize" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk-opt-your-api-key" \
  -d '{
    "prompt": "Write me some code",
    "goals": ["clarity", "specificity"]
  }'
```

### Response Format

```json
{
  "optimized_prompt": "Create a well-documented code solution with the following specifications...",
  "confidence_score": 0.87,
  "optimization_applied": ["clarity", "specificity"],
  "quota_remaining": 195,
  "template_saved": true,
  "request_id": "req_abc123"
}
```

### Available Endpoints

- `GET /health` - Service health check
- `POST /api/v1/validate-key` - Validate API key
- `POST /api/v1/optimize` - Optimize prompt
- `GET /api/v1/quota` - Check usage quota
- `GET /api/v1/templates` - List saved templates

---

## 🎯 Optimization Goals

Choose from these optimization strategies:

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

---

## 🌐 Web Dashboard

**Access**: [https://promptoptimizer-blog.vercel.app/dashboard](https://promptoptimizer-blog.vercel.app/dashboard)

### Features

- 🔑 **API Key Management** - Generate and manage your API keys
- 📊 **Usage Analytics** - Track your optimization usage and quotas
- 📝 **Template History** - View and export your optimization history
- 💳 **Subscription Management** - Manage your plan and billing
- 📈 **Performance Insights** - Analyze optimization patterns and effectiveness

---

## 💰 Subscription Tiers

- **Explorer** ($5.99/month): 20 optimizations via Web UI only
- **Creator** ($12.99/month): 200 optimizations + 1 API key + Template history
- **Innovator** ($24.99/month): 450 optimizations + up to 10 API keys + Advanced analytics

---

## 🏗️ Backend Infrastructure

### Technology Stack

- **FastAPI Backend** - High-performance Python API server with async processing
- **Northflank Hosting** - Enterprise cloud deployment platform with 99.9% uptime
- **Supabase Database** - PostgreSQL database with real-time features and automatic backups
- **Stripe Integration** - Secure payment processing and subscription management
- **Template Storage System** - Automatic optimization history with rich metadata
- **Advanced Analytics** - Usage tracking, performance monitoring, and optimization insights

### Architecture Features

- **Real-time Quota Tracking** - Live usage monitoring and limits
- **Template Persistence** - Automatic saving with comprehensive metadata
- **Rate Limiting** - Intelligent throttling to prevent abuse
- **Security Monitoring** - Advanced threat detection and prevention
- **Performance Optimization** - Sub-second response times for most requests
- **Scalable Design** - Microservices architecture for horizontal scaling

### Security & Compliance

- 🔒 **API Key Authentication** - Secure `sk-opt-` format keys
- 🌐 **HTTPS Encryption** - All communication encrypted in transit
- 🗄️ **Data Encryption** - Template data encrypted at rest
- 📋 **Audit Trails** - Complete history of API usage
- 🛡️ **Enterprise Security** - SOC 2 Type II compliance standards
- 🔐 **Privacy Protection** - Your prompts remain your intellectual property

---

## 📚 Documentation

### For Developers

- [MCP Package Documentation](https://www.npmjs.com/package/mcp-prompt-optimizer)
- [API Reference](https://promptoptimizer-blog.vercel.app/docs/api)
- [Integration Examples](https://promptoptimizer-blog.vercel.app/docs/examples)
- [Client SDK Documentation](https://promptoptimizer-blog.vercel.app/docs/sdk)

### For Users

- [Getting Started Guide](https://promptoptimizer-blog.vercel.app/docs/getting-started)
- [Optimization Best Practices](https://promptoptimizer-blog.vercel.app/docs/best-practices)
- [Template Management](https://promptoptimizer-blog.vercel.app/docs/templates)
- [Troubleshooting Guide](https://promptoptimizer-blog.vercel.app/docs/troubleshooting)

---

## 🚀 Getting Started

### 1. Choose Your Integration Method

**For MCP Clients (Claude Desktop, Cursor, Windsurf)**:
```bash
npm install -g mcp-prompt-optimizer
mcp-prompt-optimizer --setup
```

**For Direct API Integration**:
1. Visit [Dashboard](https://promptoptimizer-blog.vercel.app/dashboard)
2. Subscribe to a plan
3. Generate an API key
4. Start making API calls

**For Web Interface**:
1. Visit [Prompt Optimizer](https://promptoptimizer-blog.vercel.app)
2. Create an account
3. Start optimizing prompts in your browser

### 2. Test Your Setup

**MCP Test**:
```
ask Claude: "Please optimize this prompt: 'help me code'"
```

**API Test**:
```bash
curl -X POST "https://p01--project-optimizer--fvrdk8m9k9j.code.run/api/v1/optimize" \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "help me code", "goals": ["clarity"]}'
```

---

## 🔧 Troubleshooting

### Common Issues

**MCP Connection Issues**:
1. Verify Node.js is installed: `node --version`
2. Check package installation: `npm list -g mcp-prompt-optimizer`
3. Restart your MCP client after configuration
4. Verify config file syntax

**API Authentication Issues**:
1. Check API key format: Should start with `sk-opt-`
2. Verify subscription is active in dashboard
3. Test key validation: `curl -X POST .../validate-key -H "X-API-Key: your-key"`

**Backend Connectivity**:
1. Test backend health: `curl https://p01--project-optimizer--fvrdk8m9k9j.code.run/health`
2. Check internet connectivity
3. Verify no firewall blocking HTTPS requests

---

## 📞 Support

- 📚 **Documentation**: [promptoptimizer-blog.vercel.app/docs](https://promptoptimizer-blog.vercel.app/docs)
- 🎫 **Support Portal**: [promptoptimizer-blog.vercel.app/support](https://promptoptimizer-blog.vercel.app/support)
- 🐛 **Report Issues**: [GitHub Issues](https://github.com/nivlewd1/prompt-optimizer/issues)
- 💬 **Community**: [Discord Server](https://discord.gg/prompt-optimizer)
- 📧 **Email**: support@promptoptimizer.com

---

## 📄 License

**Commercial License** - This software is licensed for commercial use. See [LICENSE](./LICENSE) file for details.

**Your Content**: You retain full intellectual property rights over all prompts, templates, and content you create using this service.

---

## 🏢 Enterprise

For enterprise deployments, custom integrations, or volume licensing:

- 📧 **Enterprise Sales**: enterprise@promptoptimizer.com
- 📞 **Schedule Demo**: [Calendar Link](https://cal.com/prompt-optimizer/enterprise)
- 💼 **Custom Solutions**: On-premise deployment available
- 🔒 **Enhanced Security**: SSO, SAML, custom compliance requirements

---

**Made with ❤️ by the Prompt Optimizer Team**  
*Empowering better AI interactions through optimized prompts*

[![NPM Version](https://img.shields.io/npm/v/mcp-prompt-optimizer)](https://www.npmjs.com/package/mcp-prompt-optimizer)
[![API Status](https://img.shields.io/badge/API-Production-green)](https://p01--project-optimizer--fvrdk8m9k9j.code.run/health)
[![License](https://img.shields.io/badge/License-Commercial-blue)](./LICENSE)