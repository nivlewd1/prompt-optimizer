# REST API Documentation

## Overview

The Prompt Optimizer REST API provides direct access to our comprehensive prompt optimization platform through HTTP endpoints. This API powers both the MCP packages and web dashboard interfaces, offering 50+ professional optimization goals and enterprise-grade capabilities.

**Production Endpoint**: `https://p01--project-optimizer--fvrdk8m9k9j.code.run`

## Authentication

All API requests require authentication using an API key in the request headers:

```http
X-API-Key: sk-opt-your-api-key-here
```

### Getting an API Key

1. Visit [Prompt Optimizer Dashboard](https://promptoptimizer-blog.vercel.app/dashboard)
2. Subscribe to Explorer ($2.99/month), Creator ($25.99/month), or Innovator ($69.99/month) plan
3. Generate your API key from the dashboard
4. API keys follow the format: `sk-opt-xxxxxxxxxxxxxxxxxxxxxxxx`

## Base URL

```
https://p01--project-optimizer--fvrdk8m9k9j.code.run
```

## Core Endpoints

### Health Check

**GET** `/health`

Check the service health status and version.

```bash
curl -X GET "https://p01--project-optimizer--fvrdk8m9k9j.code.run/health"
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.3.1",
  "timestamp": "2025-07-11T12:00:00.000Z",
  "components": {
    "database": "healthy",
    "stripe": "healthy",
    "optimization_engine": "healthy"
  }
}
```

### Validate API Key

**POST** `/api/v1/validate-key`

Validate an API key and check associated subscription details.

```bash
curl -X POST "https://p01--project-optimizer--fvrdk8m9k9j.code.run/api/v1/validate-key" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk-opt-your-api-key"
```

**Response:**
```json
{
  "valid": true,
  "user_id": "user_abc123",
  "subscription_tier": "creator",
  "quota_limit": 18000,
  "quota_used": 150,
  "quota_remaining": 17850,
  "team_id": "team_xyz789",
  "api_keys_count": 2,
  "api_keys_limit": 3
}
```

### Optimize Prompt

**POST** `/api/v1/optimize`

Optimize a prompt using our advanced optimization engine with 50+ professional goals.

```bash
curl -X POST "https://p01--project-optimizer--fvrdk8m9k9j.code.run/api/v1/optimize" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk-opt-your-api-key" \
  -d '{
    "prompt": "Write me some code for a login system",
    "goals": ["clarity", "technical_accuracy", "security_enhancement"],
    "ai_context": "code_generation"
  }'
```

**Request Body:**
```json
{
  "prompt": "string (required)",
  "goals": ["array of goal strings (optional)"],
  "ai_context": "string (optional): code_generation, human_communication, technical_automation, etc.",
  "stream": "boolean (optional, default: false)"
}
```

**Response:**
```json
{
  "optimized_prompt": "Create a secure user authentication system with the following specifications:\n\n## Requirements:\n- Implement login functionality with username/email and password\n- Include proper input validation and sanitization\n- Add password hashing using bcrypt or similar\n- Implement session management with JWT tokens\n- Include error handling for invalid credentials\n- Add rate limiting to prevent brute force attacks\n\n## Technical Stack:\n- Backend: Node.js/Express or Python/FastAPI\n- Database: PostgreSQL or MongoDB\n- Frontend: React/Vue/Angular\n- Security: bcrypt, JWT, express-rate-limit\n\n## Deliverables:\n- User registration and login endpoints\n- Frontend authentication forms\n- Database schema for user accounts\n- Security middleware implementation\n- Unit tests for authentication flows",
  "confidence_score": 0.92,
  "optimization_goals": ["clarity", "technical_accuracy", "security_enhancement"],
  "quota_remaining": 17849,
  "template_saved": true,
  "request_id": "req_abc123xyz",
  "processing_time_ms": 850,
  "ai_context_detected": "code_generation"
}
```

### Check Quota

**GET** `/api/v1/quota`

Check current usage quota and subscription limits.

```bash
curl -X GET "https://p01--project-optimizer--fvrdk8m9k9j.code.run/api/v1/quota" \
  -H "X-API-Key: sk-opt-your-api-key"
```

**Response:**
```json
{
  "quota_limit": 18000,
  "quota_used": 150,
  "quota_remaining": 17850,
  "reset_date": "2025-08-11T00:00:00.000Z",
  "subscription_tier": "creator",
  "billing_cycle": "monthly",
  "team_usage": {
    "total_members": 2,
    "individual_usage": [
      {"user_id": "user_abc123", "usage": 120},
      {"user_id": "user_def456", "usage": 30}
    ]
  }
}
```

## Template Management Endpoints

### List Templates

**GET** `/api/v1/templates`

Retrieve optimization history and saved templates with advanced filtering.

```bash
curl -X GET "https://p01--project-optimizer--fvrdk8m9k9j.code.run/api/v1/templates?limit=20&goals=technical_accuracy" \
  -H "X-API-Key: sk-opt-your-api-key"
```

**Query Parameters:**
- `limit` (optional): Number of templates to return (default: 20, max: 100)
- `offset` (optional): Pagination offset (default: 0)
- `sort` (optional): Sort order - `newest`, `oldest`, `confidence`, `usage` (default: `newest`)
- `goals` (optional): Filter by optimization goals (comma-separated)
- `search` (optional): Search in template content
- `team_only` (optional): Show only team templates (boolean)

**Response:**
```json
{
  "templates": [
    {
      "id": "template_abc123",
      "saved_at_utc": "2025-07-11T12:00:00.000Z",
      "optimization_tier": "LLM",
      "confidence_score": 0.92,
      "original_prompt": "Write me some code for a login system",
      "optimized_prompt": "Create a secure user authentication system...",
      "optimization_goals": ["clarity", "technical_accuracy", "security_enhancement"],
      "context_snapshot": {
        "domain": "Software Development",
        "target_audience": "Developers",
        "ai_context": "code_generation"
      },
      "request_id": "req_abc123xyz",
      "request_metadata": {
        "api_request_type": "POST_non_streaming",
        "user_id": "user_abc123",
        "team_id": "team_xyz789"
      },
      "model_optimized_with": "openai/gpt-4o-mini",
      "usage_analytics": {
        "times_used": 15,
        "last_used": "2025-07-10T15:30:00.000Z",
        "average_confidence": 0.89
      }
    }
  ],
  "total_count": 45,
  "has_more": true,
  "filters_applied": ["goals: technical_accuracy"]
}
```

### Search Templates

**POST** `/api/v1/templates/search`

Advanced template search with multiple criteria.

```bash
curl -X POST "https://p01--project-optimizer--fvrdk8m9k9j.code.run/api/v1/templates/search" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk-opt-your-api-key" \
  -d '{
    "query": "authentication system",
    "goals": ["security_enhancement", "technical_accuracy"],
    "min_confidence": 0.8,
    "limit": 10
  }'
```

### Get Template

**GET** `/api/v1/templates/{template_id}`

Retrieve specific template with full details and analytics.

### Get Template Stats

**GET** `/api/v1/templates/{template_id}/stats`

Get detailed analytics for a specific template.

## Team Management Endpoints

### List Team Members

**GET** `/api/v1/teams/members`

List all team members and their roles.

### Invite Team Member

**POST** `/api/v1/teams/invite`

Invite a new member to the team.

### Remove Team Member

**DELETE** `/api/v1/teams/members/{user_id}`

Remove a team member.

### Team Usage Analytics

**GET** `/api/v1/teams/usage`

Get team-wide usage analytics and insights.

## User Management Endpoints

### User Profile

**GET** `/api/v1/user/profile`

Get current user profile information.

**PUT** `/api/v1/user/profile`

Update user profile settings.

### API Key Management

**GET** `/api/v1/user/api-keys`

List all API keys for the user.

**POST** `/api/v1/user/api-keys`

Generate a new API key.

**DELETE** `/api/v1/user/api-keys/{key_id}`

Revoke an API key.

## Local License Endpoints

### Generate Local License

**POST** `/api/v1/local-license/generate`

Generate a Basic (free) local license.

### Upgrade Local License

**POST** `/api/v1/local-license/upgrade`

Upgrade to Pro local license via Stripe.

### Validate Local License

**POST** `/api/v1/local-license/validate`

Validate a local license key.

## 50+ Professional Optimization Goals

Our platform offers the most comprehensive optimization goal library available:

### Core Enhancement (10 goals)
Available in all tiers:
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

### Technical Precision (12 goals)
Pro/Creator/Innovator tiers:
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

### AI Model Compatibility (8 goals)
Pro/Creator/Innovator tiers:
- `ai_model_compatibility` - Optimized for specific AI models
- `parameter_preservation` - Maintain critical prompt parameters
- `token_efficiency` - Maximize information per token
- `context_window_optimization` - Efficient use of context limits
- `model_specific_formatting` - Tailored for GPT/Claude/other models
- `streaming_optimization` - Enhanced for real-time responses
- `multimodal_enhancement` - Image + text optimization
- `cross_platform_compatibility` - Universal MCP client support

### Domain-Specific Enhancement (10 goals)
Pro/Creator/Innovator tiers:
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

### Advanced Techniques (8 goals)
Creator/Innovator tiers:
- `prompt_chaining` - Multi-step prompt sequences
- `few_shot_optimization` - Example-based learning enhancement
- `chain_of_thought` - Step-by-step reasoning optimization
- `role_play_enhancement` - Character and persona development
- `constraint_satisfaction` - Working within specific limitations
- `output_formatting` - Structured response optimization
- `error_handling` - Robust failure mode management
- `edge_case_coverage` - Comprehensive scenario handling

### Emerging Capabilities (6 goals)
Innovator tier:
- `real_time_adaptation` - Dynamic optimization based on usage
- `collaborative_enhancement` - Team-optimized prompts
- `enterprise_compliance` - Regulatory and compliance alignment
- `multilingual_optimization` - Cross-language enhancement
- `accessibility_enhancement` - Inclusive design principles
- `sustainability_focus` - Environmental and ethical considerations

### Specialized Applications (6 goals)
Creator/Innovator tiers:
- `data_analysis` - Statistical and analytical enhancements
- `project_management` - Planning and coordination optimization
- `customer_service` - Support and communication enhancement
- `content_moderation` - Safety and appropriateness focus
- `knowledge_extraction` - Information retrieval optimization
- `decision_support` - Choice and evaluation assistance

## AI Context Types

The `ai_context` parameter helps optimize prompts for specific use cases:

- `human_communication` - Human-to-human interaction optimization
- `llm_interaction` - AI model interaction optimization
- `image_generation` - Visual content creation prompts
- `technical_automation` - Automated system integration
- `structured_output` - Formatted data output requirements
- `code_generation` - Software development and programming
- `api_automation` - API integration and automation

## Error Handling

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (invalid or missing API key)
- `403` - Forbidden (quota exceeded or subscription issues)
- `404` - Not Found (resource doesn't exist)
- `429` - Too Many Requests (rate limiting)
- `500` - Internal Server Error
- `503` - Service Unavailable

### Error Response Format

```json
{
  "error": {
    "code": "QUOTA_EXCEEDED",
    "message": "Monthly quota limit reached. Upgrade plan or wait for reset.",
    "details": {
      "quota_used": 18000,
      "quota_limit": 18000,
      "reset_date": "2025-08-11T00:00:00.000Z",
      "suggested_action": "upgrade_plan"
    }
  },
  "request_id": "req_error_123",
  "timestamp": "2025-07-11T12:00:00.000Z"
}
```

### Common Error Codes

- `INVALID_API_KEY` - API key is malformed or invalid
- `SUBSCRIPTION_REQUIRED` - Valid subscription required for this endpoint
- `QUOTA_EXCEEDED` - Monthly usage quota has been reached
- `RATE_LIMITED` - Too many requests, retry after delay
- `INVALID_GOALS` - One or more optimization goals are not supported for your tier
- `PROMPT_TOO_LONG` - Prompt exceeds maximum length limit (10,000 characters)
- `PROMPT_EMPTY` - Prompt cannot be empty
- `TEMPLATE_NOT_FOUND` - Requested template doesn't exist or not accessible
- `TEAM_LIMIT_REACHED` - Team member limit exceeded for subscription tier
- `SERVICE_UNAVAILABLE` - Backend service temporarily unavailable

## Rate Limiting

API requests are subject to rate limiting based on subscription tier:

- **Explorer Plan**: 5 requests per minute
- **Creator Plan**: 15 requests per minute
- **Innovator Plan**: 30 requests per minute  
- **Enterprise**: Custom limits

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 15
X-RateLimit-Remaining: 12
X-RateLimit-Reset: 1672531260
X-RateLimit-Tier: creator
```

## Subscription Tiers & Pricing

### Explorer - $2.99/month
- 5,000 optimizations/month
- 1 API key
- Core optimization goals (25 goals)
- Web dashboard access
- Standard support

### Creator - $25.99/month
- 18,000 optimizations/month
- 3 API keys
- All optimization goals (50+ goals)
- 2 team members
- Template analytics
- Priority support

### Innovator - $69.99/month
- 75,000 optimizations/month
- 10 API keys
- All optimization goals (50+ goals)
- 5 team members
- Advanced analytics
- Custom optimization models
- Premium support

## SDK Examples

### JavaScript/Node.js

```javascript
const PromptOptimizer = require('prompt-optimizer-sdk');

const optimizer = new PromptOptimizer({
  apiKey: 'sk-opt-your-api-key',
  baseUrl: 'https://p01--project-optimizer--fvrdk8m9k9j.code.run'
});

// Basic optimization
async function optimizePrompt() {
  try {
    const result = await optimizer.optimize({
      prompt: "Write me some code for a login system",
      goals: ["clarity", "technical_accuracy", "security_enhancement"],
      aiContext: "code_generation"
    });
    
    console.log('Optimized:', result.optimized_prompt);
    console.log('Confidence:', result.confidence_score);
    console.log('Quota remaining:', result.quota_remaining);
  } catch (error) {
    console.error('Optimization failed:', error.message);
  }
}

// Template search
async function searchTemplates() {
  const templates = await optimizer.searchTemplates({
    query: "authentication",
    goals: ["security_enhancement"],
    minConfidence: 0.8
  });
  
  return templates;
}
```

### Python

```python
import requests
from typing import List, Optional

class PromptOptimizer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://p01--project-optimizer--fvrdk8m9k9j.code.run'
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def optimize(self, 
                 prompt: str, 
                 goals: Optional[List[str]] = None,
                 ai_context: Optional[str] = None) -> dict:
        """Optimize a prompt with optional goals and context"""
        data = {'prompt': prompt}
        if goals:
            data['goals'] = goals
        if ai_context:
            data['ai_context'] = ai_context
            
        response = requests.post(
            f'{self.base_url}/api/v1/optimize',
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def search_templates(self, 
                        query: str,
                        goals: Optional[List[str]] = None,
                        min_confidence: Optional[float] = None) -> dict:
        """Search for templates matching criteria"""
        data = {'query': query}
        if goals:
            data['goals'] = goals
        if min_confidence:
            data['min_confidence'] = min_confidence
            
        response = requests.post(
            f'{self.base_url}/api/v1/templates/search',
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def get_quota(self) -> dict:
        """Check current quota usage"""
        response = requests.get(
            f'{self.base_url}/api/v1/quota',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

# Usage example
optimizer = PromptOptimizer('sk-opt-your-api-key')

# Optimize with advanced goals
result = optimizer.optimize(
    prompt="Create a machine learning model", 
    goals=["technical_accuracy", "specificity", "code_optimization"],
    ai_context="code_generation"
)

print(f"Optimized prompt: {result['optimized_prompt']}")
print(f"Confidence: {result['confidence_score']}")
```

## Integration Best Practices

1. **Error Handling**: Implement comprehensive error handling with retry logic
2. **Rate Limiting**: Respect rate limits and implement exponential backoff
3. **API Key Security**: Use environment variables, never expose in client code
4. **Quota Management**: Monitor usage and implement graceful degradation
5. **Template Reuse**: Leverage template search for consistency
6. **Goal Selection**: Choose goals appropriate for your use case and tier
7. **Context Setting**: Use `ai_context` for better optimization results
8. **Monitoring**: Log API usage patterns and response times

## Webhook Support (Beta)

Real-time notifications for events:

- **quota_threshold**: When quota usage reaches 80%, 90%, 95%
- **optimization_complete**: For long-running optimizations
- **subscription_change**: Plan upgrades/downgrades
- **team_member_added**: New team member invitations

Configure webhooks in the dashboard or via API.

## Support & Resources

- 📚 **API Documentation**: [promptoptimizer-blog.vercel.app/docs/api](https://promptoptimizer-blog.vercel.app/docs/api)
- 🎫 **Support Portal**: [promptoptimizer-blog.vercel.app/support](https://promptoptimizer-blog.vercel.app/support)
- 📧 **API Support**: api-support@promptoptimizer.help
- 💬 **Developer Discord**: [Join our community](https://discord.gg/prompt-optimizer-devs)
- 🚀 **Status Page**: [status.promptoptimizer.help](https://status.promptoptimizer.help)

---

**Note**: This API is under active development with new features and optimization goals added regularly. Subscribe to our [Developer Newsletter](https://promptoptimizer-blog.vercel.app/newsletter) for updates and announcements.