# Security Policy

## Supported Versions

We support the latest published version of each component with security updates:

| Component | Version | Supported |
| --- | --- | --- |
| Backend | production-v2.3.0 | :white_check_mark: |
| `mcp-prompt-optimizer` (Cloud) | 3.8.6 | :white_check_mark: |
| `mcp-prompt-optimizer-local` | 4.1.10 | :white_check_mark: |
| Older releases | — | :x: |

## Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

### 1. **DO NOT** create a public GitHub issue

Security vulnerabilities should not be disclosed publicly until they have been addressed.

### 2. Email us

Send details to: **support@promptoptimizer.xyz**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Your contact information

### 3. Response Timeline

- **24 hours**: Initial acknowledgment
- **72 hours**: Preliminary assessment
- **7 days**: Detailed response with remediation plan
- **30 days**: Resolution and disclosure (if applicable)

### 4. Responsible Disclosure

We follow responsible disclosure practices:
- We'll work with you to understand and address the issue
- We'll credit you in our security advisories (if desired)
- We ask that you don't disclose the vulnerability until we've had time to fix it

## Security Measures

### API Keys

- **Key Management**: API keys can be created and deleted from the dashboard.
- **HTTPS**: All traffic uses HTTPS (TLS 1.2 or newer, with HSTS enabled).

### Data Protection

- **Scoped Storage**: Prompts are saved to your own template library (not shared across users) in Supabase Postgres, which the provider encrypts at rest. They are not used to train models.
- **Row Level Security**: Row Level Security is enabled on user-data tables such as templates, template versions and usage events.
- **Version History**: Template changes are versioned and can be rolled back.
- **Usage Logs**: API-call, quota-limit and upgrade-prompt events (metadata only, never prompt content) are deleted automatically after 90 days.
- **Right to Erasure**: Request permanent deletion of your prompts, optimization history, and account metadata at any time — see [promptoptimizer.xyz/privacy](https://promptoptimizer.xyz/privacy)

### Infrastructure

- **Hosting**: The API runs on Northflank, the web app on Vercel, and the database on Supabase.
- **Usage Quotas**: Each plan has a monthly usage quota.
- **Monitoring**: Automated production health checks and operator alerts. The service is run by one operator, so there is no 24/7 on-call.

### Client Security

- **Input Validation**: Request bodies are validated against typed schemas.
- **CI**: Every push to the main branch runs automated lint and tests.

## Security Best Practices for Users

### API Key Management

1. **Keep API Keys Secret**
   - Never share your API keys
   - Don't commit API keys to version control
   - Use environment variables in production

2. **Regular Rotation**
   - Rotate API keys regularly
   - Immediately rotate if compromised
   - Use different keys for different environments

3. **Monitor Usage**
   - Regularly check your usage in the dashboard
   - Report unusual activity immediately

### MCP Client Security

1. **Secure Configuration**
   - Protect your MCP configuration files
   - Use proper file permissions
   - Regular client updates

2. **Network Security**
   - Use secure networks for API calls
   - Avoid public Wi-Fi for sensitive operations
   - Consider VPN for additional protection

## Incident Response

In case of a security incident:

1. **Immediate Steps**
   - Rotate affected API keys immediately
   - Check your usage logs for unauthorized activity
   - Contact us at support@promptoptimizer.xyz

2. **We Will**
   - Investigate the incident thoroughly
   - Provide regular updates on our findings
   - Implement additional safeguards if needed
   - Assist with any remediation efforts

## Compliance Posture

We design our data handling around, but are not formally certified against:

- **GDPR / CCPA principles**: Prompts and optimization history live in your own scoped template library; never shared across users or used to train models. Right to export and right to erasure are available on request — see [promptoptimizer.xyz/privacy](https://promptoptimizer.xyz/privacy).
- **Industry Standards**: Following OWASP guidance for API and web application security.

We are a small, independently-operated product — if formal certification (e.g. SOC 2) matters for your use case, contact us before relying on it.

## Security Updates

Fixes ship as new versions: the backend is deployed continuously, and the npm packages are published to npm. The packages do not update themselves; update with `npm install -g mcp-prompt-optimizer@latest` (or `mcp-prompt-optimizer-local@latest`). Package changes are listed in each package's changelog.

## Bug Bounty Program

We're considering a bug bounty program for security researchers. Stay tuned for updates!

## Contact Information

- **Security & General Support**: support@promptoptimizer.xyz

---

**Note**: This security policy applies to all Prompt Optimizer services, including the MCP package, REST API, and web dashboard.
