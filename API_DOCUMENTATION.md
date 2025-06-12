# REST API Documentation

## Overview

The Prompt Optimizer REST API provides direct access to prompt optimization services through HTTP endpoints. This API powers both the MCP package and web dashboard interfaces.

**Production Endpoint**: `https://p01--project-optimizer--fvrdk8m9k9j.code.run`

## Authentication

All API requests require authentication using an API key in the request headers:

```http
X-API-Key: sk-opt-your-api-key-here
```

### Getting an API Key

1. Visit [Prompt Optimizer Dashboard](https://promptoptimizer-blog.vercel.app/dashboard)
2. Subscribe to Creator ($12.99/month) or Innovator ($24.99/month) plan
3. Generate your API key from the dashboard
4. API keys follow the format: `sk-opt-xxxxxxxxxxxxxxxxxxxxxxxx`

## Base URL

```
https://p01--project-optimizer--fvrdk8m9k9j.code.run
```

## Endpoints

### Health Check

**GET** `/health`

Check the service health status.

```bash
curl -X GET "https://p01--project-optimizer--fvrdk8m9k9j.code.run/health"
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.2.2",
  "timestamp": "2025-06-05T12:00:00.000Z"
}
```

### Validate API Key

**POST** `/api/v1/validate-key`

Validate an API key and check associated subscription.

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
  "quota_limit": 200,
  "quota_used": 5,
  "quota_remaining": 195
}
```

### Optimize Prompt

**POST** `/api/v1/optimize`

Optimize a prompt based on specified goals.

```bash
curl -X POST "https://p01--project-optimizer--fvrdk8m9k9j.code.run/api/v1/optimize" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk-opt-your-api-key" \
  -d '{
    "prompt": "Write me some code for a login system",
    "goals": ["clarity", "specificity", "technical_accuracy"]
  }'
```

**Request Body:**
```json
{
  "prompt": "string (required)",
  "goals": ["array of goal strings (optional)"],
  "stream": "boolean (optional, default: false)"
}
```

**Response:**
```json
{
  "optimized_prompt": "Create a secure user authentication system with the following specifications:\n\n## Requirements:\n- Implement login functionality with username/email and password\n- Include proper input validation and sanitization\n- Add password hashing using bcrypt or similar\n- Implement session management\n- Include error handling for invalid credentials\n- Add rate limiting to prevent brute force attacks\n\n## Deliverables:\n- Backend authentication logic\n- Frontend login form\n- Database schema for user accounts\n- Security best practices implementation",
  "confidence_score": 0.87,
  "optimization_goals": ["clarity", "specificity", "technical_accuracy"],
  "quota_remaining": 194,
  "template_saved": true,
  "request_id": "req_abc123xyz",
  "processing_time_ms": 1250
}
```

### Check Quota

**GET** `/api/v1/quota`

Check current usage quota and limits.

```bash
curl -X GET "https://p01--project-optimizer--fvrdk8m9k9j.code.run/api/v1/quota" \
  -H "X-API-Key: sk-opt-your-api-key"
```

**Response:**
```json
{
  "quota_limit": 200,
  "quota_used": 5,
  "quota_remaining": 195,
  "reset_date": "2025-07-05T00:00:00.000Z",
  "subscription_tier": "creator"
}
```

### List Templates

**GET** `/api/v1/templates`

Retrieve optimization history and saved templates.

```bash
curl -X GET "https://p01--project-optimizer--fvrdk8m9k9j.code.run/api/v1/templates" \
  -H "X-API-Key: sk-opt-your-api-key" \
  -H "Content-Type: application/json"
```

**Query Parameters:**
- `limit` (optional): Number of templates to return (default: 20, max: 100)
- `offset` (optional): Pagination offset (default: 0)
- `sort` (optional): Sort order - `newest` or `oldest` (default: `newest`)

**Response:**
```json
{
  "templates": [
    {
      "id": "template_abc123",
      "saved_at_utc": "2025-06-05T12:00:00.000Z",
      "optimization_tier": "LLM",
      "confidence_score": 0.87,
      "original_prompt": "Write me some code for a login system",
      "optimized_prompt": "Create a secure user authentication system...",
      "optimization_goals": ["clarity", "specificity", "technical_accuracy"],
      "context_snapshot": {
        "domain": "Software Development",
        "target_audience": "Developers"
      },
      "request_id": "req_abc123xyz",
      "request_metadata": {
        "api_request_type": "POST_non_streaming",
        "user_id": "user_abc123"
      },
      "model_optimized_with": "openai/gpt-4o-mini"
    }
  ],
  "total_count": 15,
  "has_more": false
}
```

## Optimization Goals

Supported optimization goals for the `/api/v1/optimize` endpoint:

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

## Error Handling

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (invalid or missing API key)
- `403` - Forbidden (quota exceeded or subscription issues)
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
      "quota_used": 200,
      "quota_limit": 200,
      "reset_date": "2025-07-05T00:00:00.000Z"
    }
  },
  "request_id": "req_error_123"
}
```

### Common Error Codes

- `INVALID_API_KEY` - API key is malformed or invalid
- `SUBSCRIPTION_REQUIRED` - Valid subscription required for this endpoint
- `QUOTA_EXCEEDED` - Monthly usage quota has been reached
- `RATE_LIMITED` - Too many requests, retry after delay
- `INVALID_GOALS` - One or more optimization goals are not supported
- `PROMPT_TOO_LONG` - Prompt exceeds maximum length limit
- `PROMPT_EMPTY` - Prompt cannot be empty
- `SERVICE_UNAVAILABLE` - Backend service temporarily unavailable

## Rate Limiting

API requests are subject to rate limiting:

- **Creator Plan**: 10 requests per minute
- **Innovator Plan**: 20 requests per minute  
- **Enterprise**: Custom limits

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 8
X-RateLimit-Reset: 1672531200
```

## Request/Response Examples

### Basic Optimization

```bash
# Simple optimization with default goals
curl -X POST "https://p01--project-optimizer--fvrdk8m9k9j.code.run/api/v1/optimize" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk-opt-abc123" \
  -d '{
    "prompt": "help me debug this code"
  }'
```

### Advanced Optimization

```bash
# Optimization with specific goals
curl -X POST "https://p01--project-optimizer--fvrdk8m9k9j.code.run/api/v1/optimize" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk-opt-abc123" \
  -d '{
    "prompt": "Create a machine learning model",
    "goals": ["technical_accuracy", "specificity", "structure"]
  }'
```

### Pagination Example

```bash
# Get templates with pagination
curl -X GET "https://p01--project-optimizer--fvrdk8m9k9j.code.run/api/v1/templates?limit=10&offset=20" \
  -H "X-API-Key: sk-opt-abc123"
```

## SDKs and Libraries

### JavaScript/Node.js

```javascript
const axios = require('axios');

const client = axios.create({
  baseURL: 'https://p01--project-optimizer--fvrdk8m9k9j.code.run',
  headers: {
    'X-API-Key': 'sk-opt-your-api-key',
    'Content-Type': 'application/json'
  }
});

// Optimize a prompt
async function optimizePrompt(prompt, goals = []) {
  try {
    const response = await client.post('/api/v1/optimize', {
      prompt,
      goals
    });
    return response.data;
  } catch (error) {
    console.error('Optimization failed:', error.response.data);
    throw error;
  }
}
```

### Python

```python
import requests
import json

class PromptOptimizer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://p01--project-optimizer--fvrdk8m9k9j.code.run'
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def optimize(self, prompt, goals=None):
        """Optimize a prompt with optional goals"""
        data = {'prompt': prompt}
        if goals:
            data['goals'] = goals
            
        response = requests.post(
            f'{self.base_url}/api/v1/optimize',
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def get_quota(self):
        """Check current quota usage"""
        response = requests.get(
            f'{self.base_url}/api/v1/quota',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

# Usage
optimizer = PromptOptimizer('sk-opt-your-api-key')
result = optimizer.optimize(
    "Write me some code", 
    goals=["clarity", "specificity"]
)
print(result['optimized_prompt'])
```

## Integration Best Practices

1. **Error Handling**: Always implement comprehensive error handling for network issues and API errors

2. **Rate Limiting**: Respect rate limits and implement exponential backoff for retries

3. **API Key Security**: Never expose API keys in client-side code or public repositories

4. **Quota Management**: Monitor quota usage and handle quota exceeded scenarios gracefully

5. **Template Storage**: Leverage the automatic template saving feature for optimization history

6. **Goal Selection**: Choose optimization goals that align with your specific use case

7. **Request Validation**: Validate prompts on the client side before sending to reduce errors

8. **Monitoring**: Implement logging and monitoring for API usage patterns

## Webhook Support (Coming Soon)

Webhook endpoints for real-time notifications:

- Quota threshold alerts
- Optimization completion events
- Subscription changes
- Usage analytics

## Support

For API support and technical questions:

- 📚 [API Documentation](https://promptoptimizer-blog.vercel.app/docs/api)
- 🎫 [Support Portal](https://promptoptimizer-blog.vercel.app/support)
- 📧 Email: api-support@promptoptimizer.com
- 💬 [Developer Discord](https://discord.gg/prompt-optimizer-devs)

---

**Note**: This API is under active development. Subscribe to our [Developer Newsletter](https://promptoptimizer-blog.vercel.app/newsletter) for updates and new feature announcements.