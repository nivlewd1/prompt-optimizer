# Deployment Guide

This document provides information about the Prompt Optimizer deployment architecture and instructions for various deployment scenarios.

## Architecture Overview

### Production Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Clients   │    │   Web Dashboard  │    │   Direct API    │
│                 │    │                  │    │                 │
│ • Claude Desktop│    │ • User Interface │    │ • Custom Apps   │
│ • Cursor IDE    │────▶│ • Admin Panel    │────▶│ • Integrations  │
│ • Windsurf IDE  │    │ • Analytics      │    │ • Scripts       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │    Load Balancer        │
                    │  (Northflank Managed)   │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │     FastAPI Backend     │
                    │                         │
                    │ • Authentication        │
                    │ • Rate Limiting         │
                    │ • Optimization Engine   │
                    │ • Template Management   │
                    └─────────────────────────┘
                                  │
                     ┌────────────┼────────────┐
                     │            │            │
                     ▼            ▼            ▼
            ┌────────────┐ ┌─────────────┐ ┌─────────────┐
            │  Supabase  │ │   Stripe    │ │  External   │
            │ PostgreSQL │ │  Payments   │ │ AI Services │
            │            │ │             │ │             │
            │ • Users    │ │ • Billing   │ │ • OpenAI    │
            │ • Templates│ │ • Subscript.│ │ • Anthropic │
            │ • Analytics│ │ • Invoices  │ │ • Others    │
            └────────────┘ └─────────────┘ └─────────────┘
```

## Production Deployment

### Current Production Environment

- **Platform**: Northflank Cloud
- **URL**: `https://p01--project-optimizer--fvrdk8m9k9j.code.run`
- **Database**: Supabase PostgreSQL
- **CDN**: Cloudflare
- **Monitoring**: Northflank + Custom dashboards

### Infrastructure Components

#### 1. Application Server (FastAPI)

```yaml
# northflank.yaml (simplified)
name: prompt-optimizer-api
runtime: python
version: 3.11

build:
  dockerfile: Dockerfile
  context: .

resources:
  cpu: 2
  memory: 4Gi
  replicas: 2

environment:
  - DATABASE_URL: ${SUPABASE_URL}
  - STRIPE_SECRET_KEY: ${STRIPE_SECRET}
  - OPENAI_API_KEY: ${OPENAI_KEY}
  - ANTHROPIC_API_KEY: ${ANTHROPIC_KEY}
```

#### 2. Database (Supabase)

- **Type**: PostgreSQL 15
- **Backup**: Automated daily backups
- **Scaling**: Auto-scaling enabled
- **Security**: Row Level Security (RLS)

#### 3. Payment Processing (Stripe)

- **Webhooks**: Real-time subscription updates
- **Security**: PCI DSS compliant
- **Features**: Subscriptions, invoicing, tax calculation

## MCP Package Deployment

### NPM Registry

The MCP package is published to npm and can be installed globally:

```bash
npm install -g mcp-prompt-optimizer
```

### Package Distribution

```json
{
  "name": "mcp-prompt-optimizer",
  "version": "1.0.1",
  "main": "index.js",
  "bin": {
    "mcp-prompt-optimizer": "./bin/start-server"
  },
  "files": [
    "index.js",
    "lib/",
    "bin/",
    "docs/",
    "README.md",
    "CHANGELOG.md",
    "LICENSE"
  ]
}
```

### Update Process

1. **Version Bump**
   ```bash
   npm version patch  # or minor/major
   ```

2. **Publish to NPM**
   ```bash
   npm publish
   ```

3. **Update Documentation**
   - Update README.md
   - Update CHANGELOG.md
   - Create GitHub release

## Self-Hosted Deployment

### Prerequisites

- Docker and Docker Compose
- PostgreSQL database
- SSL certificate
- Domain name

### Docker Deployment

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/promptopt
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=promptopt
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - api

volumes:
  postgres_data:
  redis_data:
```

### Environment Variables

```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost:5432/promptopt
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
STRIPE_SECRET_KEY=sk_test_...
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
ALLOWED_HOSTS=your-domain.com
DEBUG=false
```

### Database Setup

```sql
-- Create database
CREATE DATABASE promptopt;

-- Create user
CREATE USER promptopt_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE promptopt TO promptopt_user;

-- Run migrations (handled by application)
```

## Development Deployment

### Local Development Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/nivlewd1/prompt-optimizer.git
   cd prompt-optimizer
   ```

2. **Backend Setup**
   ```bash
   cd backend  # if backend code was included
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

### MCP Package Development

```bash
cd mcp-package
npm install
npm test
npm link  # For local testing
```

## Security Considerations

### Production Security

1. **HTTPS Only**
   - All traffic encrypted with TLS 1.3
   - HSTS headers enabled
   - Certificate auto-renewal

2. **API Security**
   - Rate limiting per IP and API key
   - Input validation and sanitization
   - SQL injection prevention
   - XSS protection

3. **Authentication**
   - JWT tokens with short expiration
   - API key rotation capability
   - Multi-factor authentication for admin

4. **Data Protection**
   - Encryption at rest
   - Regular security audits
   - GDPR compliance

### Network Security

```nginx
# nginx.conf security headers
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
add_header Content-Security-Policy "default-src 'self';";
```

## Monitoring and Observability

### Application Monitoring

- **Health Checks**: `/health` endpoint
- **Metrics**: Prometheus integration
- **Logging**: Structured logging with correlation IDs
- **Alerting**: Slack/email notifications

### Performance Monitoring

```python
# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "0.2.2",
        "timestamp": datetime.utcnow().isoformat(),
        "database": await check_database(),
        "redis": await check_redis(),
        "external_apis": await check_external_apis()
    }
```

### Logging Configuration

```yaml
# logging.yaml
version: 1
formatters:
  standard:
    format: '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
  json:
    format: '%(message)s'
    class: pythonjsonlogger.jsonlogger.JsonFormatter

handlers:
  console:
    class: logging.StreamHandler
    formatter: json
    level: INFO

root:
  level: INFO
  handlers: [console]
```

## Backup and Recovery

### Database Backups

```bash
# Automated daily backup
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${DATE}.sql"

pg_dump $DATABASE_URL > $BACKUP_FILE
aws s3 cp $BACKUP_FILE s3://backups/database/

# Cleanup old backups (keep 30 days)
find . -name "backup_*.sql" -mtime +30 -delete
```

### Recovery Procedures

```bash
# Database recovery
psql $DATABASE_URL < backup_file.sql

# Application recovery
docker-compose down
docker-compose pull
docker-compose up -d
```

## Scaling Considerations

### Horizontal Scaling

- **Load Balancer**: Northflank managed load balancing
- **Auto Scaling**: CPU/memory-based scaling
- **Session Management**: Stateless design with JWT
- **Database**: Read replicas for heavy read workloads

### Performance Optimization

- **Caching**: Redis for frequent queries
- **CDN**: Static asset delivery
- **Database Indexing**: Optimized query performance
- **Async Processing**: Background task queues

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   ```bash
   # Check service status
   curl https://p01--project-optimizer--fvrdk8m9k9j.code.run/health
   
   # Check DNS resolution
   nslookup p01--project-optimizer--fvrdk8m9k9j.code.run
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connection
   psql $DATABASE_URL -c "SELECT 1;"
   ```

3. **MCP Package Issues**
   ```bash
   # Reinstall package
   npm uninstall -g mcp-prompt-optimizer
   npm install -g mcp-prompt-optimizer
   
   # Reset configuration
   rm -rf ~/.prompt-optimizer
   mcp-prompt-optimizer --setup
   ```

### Log Analysis

```bash
# Check application logs
docker-compose logs -f api

# Check specific error patterns
grep -i "error" /var/log/app.log | tail -20

# Monitor real-time logs
tail -f /var/log/app.log | grep -i "optimization"
```

## Support

For deployment support:

- 📧 **Technical Support**: devops@promptoptimizer.com
- 📚 **Documentation**: [docs.promptoptimizer.com](https://promptoptimizer-blog.vercel.app/docs)
- 🎫 **Support Tickets**: [support portal](https://promptoptimizer-blog.vercel.app/support)
- 💬 **Community**: [Discord server](https://discord.gg/prompt-optimizer)

---

**Note**: This deployment guide covers the public-facing components. Core optimization algorithms and proprietary backend logic are not included in this open-source repository.