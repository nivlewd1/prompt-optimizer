# Deployment Guide

This document describes how Prompt Optimizer is deployed in production and how to work with the parts that are in this repository.

## Architecture Overview

### Production Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Clients   │    │   Web Dashboard  │    │   Direct API    │
│                 │    │                  │    │                 │
│ • Claude Desktop│    │ • User Interface │    │ • Custom Apps   │
│ • Cursor IDE    │────▶│ • Analytics      │────▶│ • Integrations  │
│ • Windsurf IDE  │    │ • Evaluations    │    │ • Scripts       │
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
            │ • Users    │ │ • Billing   │ │ • OpenRouter│
            │ • Templates│ │ • Subscript.│ │ • OpenAI    │
            │ • Analytics│ │ • Invoices  │ │             │
            └────────────┘ └─────────────┘ └─────────────┘
```

## Production Deployment

### Current Production Environment

- **API**: Northflank, at `https://p01--project-optimizer--fvmrdk8m9k9j.code.run`
- **Web app**: Vercel, at [promptoptimizer.xyz](https://promptoptimizer.xyz)
- **Database**: Supabase PostgreSQL
- **Monitoring**: Northflank logs, a scheduled production health scan (every 4 hours), and Slack alerts for selected failures

### Infrastructure Components

#### 1. Application Server (FastAPI)

The API runs as a Docker container (Python 3.10) with a single Uvicorn worker, sized for a 512 MB environment.

#### 2. Database (Supabase)

- **Type**: PostgreSQL
- **Backups**: Managed by Supabase
- **Security**: Row Level Security (RLS) on user-data tables

#### 3. Payment Processing (Stripe)

- **Checkout**: Stripe Checkout. Card details are handled by Stripe and never reach our servers.
- **Webhooks**: Subscription updates, with signature verification.

## MCP Package Deployment

### NPM Registry

The MCP package is published to npm and can be installed globally:

```bash
npm install -g mcp-prompt-optimizer
```

The current source is [nivlewd1/mcp-prompt-optimizer-npm](https://github.com/nivlewd1/mcp-prompt-optimizer-npm). The `mcp-package/` directory in this repository is an older snapshot (v3.1.1).

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
   - Tag the release

## Self-Hosted Deployment

Self-hosting is not an officially offered or supported deployment mode. The production service runs on the managed infrastructure described above, and the backend source is not part of this repository.

## Development Deployment

### MCP Package Development

This repository ships the skills and documentation; the backend source is proprietary and not included. To work on the current MCP package:

```bash
git clone https://github.com/nivlewd1/mcp-prompt-optimizer-npm.git
cd mcp-prompt-optimizer-npm
npm install
npm test
npm link  # For local testing
npx mcp-prompt-optimizer connect   # configure your API key against the hosted backend
```

See [MCP_PACKAGE.md](./MCP_PACKAGE.md) for usage and troubleshooting.

## Security Considerations

### Production Security

1. **HTTPS Only**
   - TLS 1.2 or newer (TLS 1.3 supported)
   - HSTS headers enabled
   - `X-Content-Type-Options: nosniff` and `X-Frame-Options: DENY` on API responses

2. **API Security**
   - API key (`X-API-Key`) or token authentication
   - Per-plan usage quotas
   - Typed request validation
   - Stripe webhook signature verification

3. **Data Protection**
   - Row Level Security on user-data tables
   - Encryption at rest provided by Supabase

See [SECURITY.md](./SECURITY.md) for the full policy and what we do not claim.

## Monitoring and Observability

### Health Checks

- `/health` or `/health/live`: liveness
- `/health/ready`: readiness (component initialization)
- `/status`: component status and the deployed commit

Example `/health` response:

```json
{
  "status": "healthy",
  "timestamp": 1791963426.33,
  "version": "production-v2.3.0",
  "uptime": 2587.75
}
```

### Alerting

- A scheduled production health scan runs every 4 hours.
- Slack alerts go to the operator for selected failures (for example Stripe webhook errors and quality drift).
- The service is run by one operator; there is no 24/7 on-call.

## Backup and Recovery

Database backups are managed by Supabase. There is no separate backup job in this repository.

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   ```bash
   # Check service status
   curl https://p01--project-optimizer--fvmrdk8m9k9j.code.run/health

   # Check DNS resolution
   nslookup p01--project-optimizer--fvmrdk8m9k9j.code.run
   ```

2. **MCP Package Issues**
   ```bash
   # Reinstall package
   npm uninstall -g mcp-prompt-optimizer
   npm install -g mcp-prompt-optimizer

   # Reconnect your client and re-enter your key
   npx mcp-prompt-optimizer connect

   # Run diagnostics
   npx mcp-prompt-optimizer diagnose
   ```

## Support

For deployment support:

- 📧 **Technical Support**: support@promptoptimizer.xyz
- 📚 **Documentation**: [promptoptimizer.xyz/documentation](https://promptoptimizer.xyz/documentation)

---

**Note**: This deployment guide covers the public-facing components. Core optimization algorithms and proprietary backend logic are not included in this repository.
