# Prompt Optimizer

**Enterprise-Grade MCP-Native Prompt Engineering Platform**

Transform your AI development workflow with our comprehensive platform featuring cloud-powered optimization, local privacy-first processing, web dashboard, team collaboration, and 50+ professional optimization goals.

[![NPM Cloud](https://img.shields.io/npm/v/mcp-prompt-optimizer)](https://www.npmjs.com/package/mcp-prompt-optimizer) [![NPM Local](https://img.shields.io/npm/v/mcp-prompt-optimizer-local)](https://www.npmjs.com/package/mcp-prompt-optimizer-local) [![API Status](https://img.shields.io/badge/API-Production-green)](https://p01--project-optimizer--fvrdk8m9k9j.code.run/health) [![Dashboard](https://img.shields.io/badge/Dashboard-Live-blue)](https://promptoptimizer-blog.vercel.app)

---

## 🏗️ **Complete Platform Architecture**

Our sophisticated platform consists of four integrated components working in harmony:

### 🏢 **Backend Engine** - Production FastAPI System
- **10+ API Routers**: optimize, subscriptions, team, templates, api_key, user_settings, mcp, dashboard, local_license, admin
- **Dual Licensing Systems**: Cloud subscriptions + Local licenses
- **Complete User Management**: Profiles, API keys, teams, subscription management
- **Stripe Integration**: Recurring subscriptions + one-time payments
- **Admin System**: Override capabilities and system management
- **Template System**: Save, search, analytics, reuse functionality
- **Health Monitoring**: Circuit breakers, metrics, component health tracking

### 🌐 **Frontend Dashboard** - Next.js Web Platform
- **User Dashboard**: Metrics, recent optimizations, template management
- **Team Management**: Collaborative features for Creator/Innovator tiers
- **Local License Portal**: Free/Pro license generation with Stripe checkout
- **Payment Integration**: Subscription management and one-time purchases
- **API Key Management**: Both cloud and local key management
- **Template Browser**: View, search, and reuse saved templates

### ☁️ **Cloud MCP Package** - [`mcp-prompt-optimizer`](https://www.npmjs.com/package/mcp-prompt-optimizer)
- **Universal MCP Compatibility**: Claude Desktop, Cursor, Windsurf, and 17+ clients
- **Cloud-Powered Optimization**: Advanced algorithms with team collaboration
- **Subscription-Based**: Explorer/Creator/Innovator tiers
- **Template Sharing**: Team-wide template management
- **Real-time Analytics**: Usage tracking and insights

### 🔒 **Local MCP Package** - [`mcp-prompt-optimizer-local`](https://www.npmjs.com/package/mcp-prompt-optimizer-local)
- **Privacy-First Design**: No data transmission during optimization
- **Binary Distribution**: Platform-specific compiled optimizers
- **Local Licensing**: Basic (free, 5 daily) / Pro ($19.99 one-time, unlimited)
- **Python Fallback**: When binary unavailable
- **License Caching**: 24-48h offline operation
- **Complete Privacy**: Local processing only

---

## 🚀 **Quick Start Guide**

### Option 1: Cloud-Powered (Recommended for Teams)

```bash
# Install cloud MCP package
npm install -g mcp-prompt-optimizer

# Configure with subscription API key
mcp-prompt-optimizer --setup

# Add to your MCP client configuration
```

**✅ CORRECT MCP Configuration for Cloud Package:**
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

### Option 2: Local Privacy-First

```bash
# Install local MCP package
npm install -g mcp-prompt-optimizer-local

# Generate local license (Basic free, Pro $19.99)
mcp-prompt-optimizer-local --license

# Configure local settings
```

**✅ CORRECT MCP Configuration for Local Package:**
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

---

## 🎯 **50+ Professional Optimization Goals**

Transform your prompts with our comprehensive optimization techniques:

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

---

## 💰 **Licensing & Subscription Plans**

### **Local Licensing (Privacy-First)**

#### **Basic License** - FREE
- ✅ **5 optimizations/day** - Perfect for trying the platform
- ✅ **Complete privacy** - No data transmission
- ✅ **Core optimization goals** - Essential techniques (25 goals)
- ✅ **Local processing** - Runs entirely on your machine
- ✅ **No subscription required** - One-time setup

#### **Pro License** - $19.99 One-Time
- ✅ **Unlimited optimizations** - No daily limits
- ✅ **All 50+ optimization goals** - Complete technique library
- ✅ **Advanced algorithms** - Enhanced optimization engine
- ✅ **Priority binary updates** - Latest optimization improvements
- ✅ **Extended offline operation** - 48h license caching

### **Cloud Subscriptions (Team Collaboration)**

#### **Explorer** - $2.99/month
*Perfect for individual developers*
- ✅ **5,000 optimizations/month** - Generous personal quota
- ✅ **1 API key** - Individual access
- ✅ **Web dashboard access** - Browser-based optimization
- ✅ **Template history** - Save and review optimizations
- ✅ **Core optimization goals** - Essential techniques (25 goals)

#### **Creator** - $25.99/month
*Most popular for teams and creators*
- ✅ **18,000 optimizations/month** - Team-level capacity
- ✅ **Up to 3 API keys** - Team collaboration
- ✅ **2 team members** - Shared access and templates
- ✅ **Advanced optimization goals** - All professional techniques (50+ goals)
- ✅ **Template analytics** - Usage patterns and insights
- ✅ **Priority processing** - Faster response times

#### **Innovator** - $69.99/month
*Enterprise-grade for large teams*
- ✅ **75,000 optimizations/month** - Enterprise capacity
- ✅ **Up to 10 API keys** - Large team management
- ✅ **5 team members** - Full collaboration features
- ✅ **Advanced analytics dashboard** - Comprehensive insights
- ✅ **Priority support** - Dedicated support channel
- ✅ **Custom optimization models** - Domain-specific algorithms
- ✅ **Advanced team management** - Role-based permissions

---

## 🔧 **MCP Tools Available**

### **Cloud Package Tools** (`mcp-prompt-optimizer`)

#### `optimize_prompt`
Cloud-powered optimization with team collaboration features.

```json
{
  "prompt": "Your prompt to optimize",
  "goals": ["clarity", "technical_accuracy", "specificity"],
  "ai_context": "code_generation",
  "stream": false
}
```

#### `list_saved_templates`
Browse team-shared optimization templates.

#### `search_templates`
Find relevant templates by keywords or goals.

```json
{
  "query": "authentication system",
  "goals": ["technical_accuracy"],
  "limit": 10
}
```

#### `get_template`
Retrieve specific template details and metadata.

#### `get_template_stats`
Analytics for template usage and effectiveness.

#### `use_template_as_base`
Start optimization from a proven template.

### **Local Package Tools** (`mcp-prompt-optimizer-local`)

#### `optimize_prompt`
Privacy-first local optimization with binary processing.

```json
{
  "prompt": "Your prompt to optimize",
  "goals": ["clarity", "technical_accuracy"],
  "local_only": true
}
```

#### `check_license`
Verify local license status and quota.

#### `upgrade_license`
Upgrade from Basic to Pro license.

---

## 🌐 **Web Dashboard Features**

**Access**: [https://promptoptimizer-blog.vercel.app/dashboard](https://promptoptimizer-blog.vercel.app/dashboard)

### **User Management**
- 🔑 **API Key Generation** - Cloud and local key management
- 📊 **Usage Analytics** - Real-time optimization tracking
- 💳 **Subscription Management** - Plan upgrades and billing
- 📋 **Audit Trails** - Complete API usage history

### **Team Collaboration** (Creator/Innovator)
- 👥 **Team Member Management** - Invite and manage team access
- 🔗 **Shared API Keys** - Team-level authentication
- 📝 **Collaborative Templates** - Shared optimization patterns
- 📈 **Team Analytics** - Usage insights across team members

### **Template Management**
- 📚 **Template Library** - Browse and manage saved optimizations
- 🔍 **Advanced Search** - Find templates by goals, keywords, or metadata
- 📊 **Template Analytics** - Usage patterns and effectiveness metrics
- 🎯 **Goal Recommendations** - Suggested optimization goals based on usage

### **Local License Portal**
- 🆓 **Basic License Generation** - Free daily quota setup
- 💎 **Pro License Purchase** - One-time $19.99 upgrade via Stripe
- 📱 **License Management** - View status and transfer licenses
- 🔄 **Automatic Updates** - Binary distribution management

---

## 🏗️ **Technical Architecture**

### **Backend Infrastructure** (`C:\Users\nivle\FastAPI_Backend\app`)
- **🚀 FastAPI Framework** - High-performance async processing
- **☁️ Northflank Hosting** - Production Kubernetes infrastructure
- **🗄️ Supabase Database** - PostgreSQL with real-time features
- **💳 Stripe Integration** - Secure payment processing for both models
- **🔒 Production Security** - Multi-layered security with monitoring
- **📊 Analytics Engine** - Real-time usage tracking and insights

### **Frontend Technology** (`C:\Users\nivle\prompt-blog\src`)
- **⚛️ Next.js Framework** - Server-side rendered React application
- **🎨 Tailwind CSS** - Responsive design system
- **📊 Chart.js Integration** - Analytics and usage visualization
- **💳 Stripe Elements** - Secure payment forms
- **🔐 JWT Authentication** - Secure session management

### **NPM Package Architecture** (`C:\Users\nivle\mcp-local-prompt-optimizer-npm`)
- **📦 Dual Package System** - Cloud and local variants
- **🔧 Binary Distribution** - Platform-specific optimizers
- **🐍 Python Fallback** - Universal compatibility
- **🔐 License Validation** - Secure local licensing system
- **📡 MCP Protocol** - Native Model Context Protocol integration

### **MCP Server Engine** (`C:\Users\nivle\MCP\app`)
- **🎯 50+ Optimization Goals** - Comprehensive technique library
- **📊 Template Management** - Automatic saving with rich metadata
- **🔄 Streaming Support** - Real-time optimization responses
- **🧠 Context Detection** - Automatic AI context routing
- **⚡ Performance Optimization** - Sub-second response times

---

## 🛠️ **Installation & Configuration**

### **System Requirements**
- **Node.js**: 16.0.0 or higher
- **npm**: 8.0.0 or higher
- **Operating System**: Windows, macOS, Linux
- **Memory**: 512MB RAM (local package)
- **Storage**: 100MB for binaries

### **Cloud Package Setup**

```bash
# Install globally
npm install -g mcp-prompt-optimizer

# Configure API key
mcp-prompt-optimizer --setup

# Test connection
mcp-prompt-optimizer --test
```

### **Local Package Setup**

```bash
# Install globally
npm install -g mcp-prompt-optimizer-local

# Generate Basic license (free)
mcp-prompt-optimizer-local --license

# Upgrade to Pro ($19.99)
mcp-prompt-optimizer-local --upgrade

# Test local optimization
mcp-prompt-optimizer-local --test
```

### **MCP Client Configuration Examples**

#### **Claude Desktop** (✅ CORRECT Configuration)
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

#### **Cursor** (✅ CORRECT Configuration)
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

#### **Windsurf** (✅ CORRECT Configuration)
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

---

## 🚨 **Troubleshooting Guide**

### **Common Installation Issues**

#### **NPM Package Conflicts**
```bash
# Clear npm cache
npm cache clean --force

# Reinstall packages
npm uninstall -g mcp-prompt-optimizer mcp-prompt-optimizer-local
npm install -g mcp-prompt-optimizer mcp-prompt-optimizer-local

# Verify installations
npm list -g | grep mcp-prompt-optimizer
```

#### **MCP Configuration Problems**
```bash
# ❌ WRONG Configuration (DO NOT USE):
# {"command": "mcp-prompt-optimizer-local"}

# ✅ CORRECT Configuration:
# {"command": "npx", "args": ["mcp-prompt-optimizer-local"]}

# Validate JSON syntax
node -e "console.log(JSON.parse(require('fs').readFileSync('~/.claude/claude_desktop_config.json')))"

# Test MCP connectivity
npx mcp-prompt-optimizer --test-mcp
npx mcp-prompt-optimizer-local --test-mcp
```

### **API and License Issues**

#### **Cloud API Authentication**
```bash
# Verify API key format
echo $PROMPT_OPTIMIZER_API_KEY | grep "^sk-opt-"

# Test API connectivity
curl -H "X-API-Key: $PROMPT_OPTIMIZER_API_KEY" \
     https://p01--project-optimizer--fvrdk8m9k9j.code.run/api/v1/user/quota

# Reconfigure API key
mcp-prompt-optimizer --setup
```

#### **Local License Validation**
```bash
# Check license status
mcp-prompt-optimizer-local --license-status

# Verify license format
echo $PROMPT_OPTIMIZER_LOCAL_LICENSE | grep "^sk-local-"

# Regenerate license
mcp-prompt-optimizer-local --license --force
```

---

## 🎯 **Best Practices**

### **Optimization Goal Selection**
- **Start Simple**: Begin with core goals like `clarity` and `specificity`
- **Layer Complexity**: Add technical goals like `technical_accuracy` for development tasks
- **Domain-Specific**: Use specialized goals for specific industries or use cases
- **Goal Synergy**: Combine complementary goals for enhanced results

### **Template Management**
- **Consistent Naming**: Use descriptive names for saved templates
- **Regular Review**: Periodically audit and update template library
- **Team Sharing**: Leverage collaborative templates for consistency
- **Analytics-Driven**: Use template analytics to identify top performers

### **Security Best Practices**
- **Key Rotation**: Regularly rotate API keys for enhanced security
- **Access Control**: Use team features to control access appropriately
- **Audit Monitoring**: Review audit trails for unusual activity
- **Local vs Cloud**: Choose appropriate package based on privacy requirements

---

## 🚀 **Start Optimizing Today**

### **Quick Decision Matrix**

| Use Case | Recommended Package | Plan |
|----------|-------------------|------|
| **Individual Developer** | `mcp-prompt-optimizer-local` | Pro License ($19.99) |
| **Privacy-Critical Work** | `mcp-prompt-optimizer-local` | Pro License ($19.99) |
| **Small Team (2-3)** | `mcp-prompt-optimizer` | Creator ($25.99/month) |
| **Large Team (5+)** | `mcp-prompt-optimizer` | Innovator ($69.99/month) |
| **Enterprise** | Hybrid deployment | Custom Enterprise |

### **Setup Checklist**

#### **For Cloud Package:**
1. ✅ [Subscribe to a Plan](https://promptoptimizer-blog.vercel.app/pricing)
2. ✅ [Generate API Key](https://promptoptimizer-blog.vercel.app/dashboard)
3. ✅ Install: `npm install -g mcp-prompt-optimizer`
4. ✅ Configure: `mcp-prompt-optimizer --setup`
5. ✅ Add CORRECT MCP configuration to your client
6. ✅ Test: Ask your MCP client to optimize a prompt

#### **For Local Package:**
1. ✅ Install: `npm install -g mcp-prompt-optimizer-local`
2. ✅ Generate license: `mcp-prompt-optimizer-local --license`
3. ✅ [Upgrade to Pro](https://promptoptimizer-blog.vercel.app/local-license) (optional)
4. ✅ Add CORRECT MCP configuration to your client
5. ✅ Test: Optimize prompts locally

---

## 📞 **Support & Community**

### **Support Channels**
- 📚 **Documentation**: [promptoptimizer-blog.vercel.app/docs](https://promptoptimizer-blog.vercel.app/docs)
- 🎫 **Support Portal**: [promptoptimizer-blog.vercel.app/support](https://promptoptimizer-blog.vercel.app/support)
- 🐛 **GitHub Issues**: [Report bugs and feature requests](https://github.com/nivlewd1/prompt-optimizer/issues)
- 💬 **Discord Community**: [Join our community](https://discord.gg/prompt-optimizer)
- 📧 **Email Support**: promptoptimizer.help@gmail.com

### **Response Time SLA**
- **Basic/Local License**: Community support (24-48 hours)
- **Explorer**: Standard support (12-24 hours)
- **Creator**: Priority support (6-12 hours)
- **Innovator**: Premium support (2-6 hours)
- **Enterprise**: Dedicated support with custom SLA

---

**Made with ❤️ by the Prompt Optimizer Team**  
*Transforming AI interactions through professional prompt engineering*

---

### 🌟 **Transform Your AI Workflow Today**

*Choose your optimization approach. Experience the difference. Elevate your AI interactions.*

**Ready to start?** [Choose your plan](https://promptoptimizer-blog.vercel.app/pricing) or [try local for free](https://www.npmjs.com/package/mcp-prompt-optimizer-local)