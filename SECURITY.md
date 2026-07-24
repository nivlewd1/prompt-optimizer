# Security Policy

## Supported Versions

We actively support the latest published version of each component with security updates:

| Component | Version | Supported |
| --- | --- | --- |
| Backend | production-v2.3.0 | :white_check_mark: |
| `mcp-prompt-optimizer` (Cloud) | 3.7.5 | :white_check_mark: |
| `mcp-prompt-optimizer-local` | 4.1.2 | :white_check_mark: |
| Older releases | — | :x: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### 1. **DO NOT** create a public GitHub issue

Security vulnerabilities should not be disclosed publicly until they have been addressed.

### 2. Email our security team

Send details to: **privacy@promptoptimizer.com**

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

### API Key Security

- **Local Storage Only**: API keys are stored locally on your device
- **HTTPS Encryption**: All communication uses TLS 1.3
- **Key Rotation**: API keys can be regenerated at any time
- **Scope Limitation**: API keys are scoped to specific services

### Data Protection

- **Scoped Storage**: Prompts are saved to your own template library (not shared across users) and encrypted at rest — not used to train models
- **Template Encryption**: User templates are encrypted at rest
- **Right to Erasure**: Request permanent deletion of your prompts, optimization history, and account metadata at any time — see [promptoptimizer.xyz/privacy](https://promptoptimizer.xyz/privacy)
- **Access Controls**: Strict access controls on all systems
- **Audit Logging**: Comprehensive audit trails

### Infrastructure Security

- **Enterprise Hosting**: Northflank enterprise deployment
- **Database Security**: Supabase with row-level security
- **Rate Limiting**: Comprehensive rate limiting and abuse protection
- **Monitoring**: 24/7 security monitoring and alerting

### Client Security

- **Input Validation**: All inputs are validated and sanitized
- **Error Handling**: Secure error handling without information leakage
- **Dependency Management**: Regular security updates for dependencies
- **Code Review**: All code changes undergo security review

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
   - Set up usage alerts

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
   - Contact our security team

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

Security updates are distributed through:

- **NPM Package**: Automatic updates via npm
- **Email Notifications**: Critical security alerts
- **GitHub Security Advisories**: Public disclosure of resolved issues
- **Dashboard Notifications**: In-app security notices

## Bug Bounty Program

We're considering a bug bounty program for security researchers. Stay tuned for updates!

## Contact Information

- **Security & General Support**: support@promptoptimizer.help
- **Emergency Contact**: Available through the dashboard

---

**Note**: This security policy applies to all Prompt Optimizer services, including the MCP package, REST API, and web dashboard.