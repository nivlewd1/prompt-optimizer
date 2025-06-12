# Changelog

All notable changes to the MCP Prompt Optimizer package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-06-05

### Changed
- **CRITICAL**: Updated default backend URL from placeholder to production deployment
  - Changed from `https://your-app.code.run` to `https://p01--project-optimizer--fvrdk8m9k9j.code.run`
  - Ensures out-of-the-box functionality without manual configuration
- Updated package repository information to proper GitHub URLs
- Enhanced error handling in API client for server errors (500 status)
- Improved documentation with backend infrastructure details

### Added
- Added comprehensive backend connectivity documentation
- Added troubleshooting section for backend connection issues
- Added environment variable documentation for debugging
- Added changelog file for version tracking
- Enhanced test suite with backend URL validation
- Added npm test script for package validation

### Fixed
- Fixed default backend URL configuration in `lib/config.js`
- Ensured consistency between API client and config defaults
- Improved package metadata and author information

### Documentation
- Updated README.md with production backend information
- Enhanced client configuration guide with backend details
- Added backend health check endpoints
- Improved troubleshooting documentation

## [1.0.0] - 2025-05-XX

### Added
- Initial release of MCP Prompt Optimizer package
- Support for Claude Desktop, Cursor, and Windsurf MCP clients
- API key authentication system with secure local storage
- Complete optimization goal support (10 different goals)
- MCP Protocol 2024-11-05 compliance
- Real-time quota tracking and usage monitoring
- Comprehensive error handling and validation
- Interactive setup command for API key configuration
- Global npm package installation support
- Cross-platform compatibility (Windows, macOS, Linux)

### Features
- **optimize_prompt** tool with advanced goal selection
- Secure API key management with local storage
- Base64 configuration encoding for MCP protocol compliance
- Automatic retry logic and rate limiting handling
- Health check and connectivity validation
- Development and production environment support

### Security
- HTTPS-only communication with backend
- Local-only API key storage
- No persistent data storage on servers
- Enterprise-grade security compliance

---

## Backend Compatibility

| Package Version | Backend API Version | Deployment URL |
|-----------------|--------------------|--------------------|  
| 1.0.1 | v0.2.2+ | https://p01--project-optimizer--fvrdk8m9k9j.code.run |
| 1.0.0 | v0.2.0+ | Placeholder URL (manual configuration required) |

## Migration Guide

### From 1.0.0 to 1.0.1

No breaking changes. The update automatically configures the correct backend URL.

**If you previously configured a custom backend URL:**
- Your configuration will be preserved
- To use the new default: delete `~/.prompt-optimizer/config.json` and run `mcp-prompt-optimizer --setup`

**For existing installations:**
```bash
# Update the package
npm update -g mcp-prompt-optimizer

# Verify new version
mcp-prompt-optimizer --version

# Test connectivity (optional)
npm test
```

## Known Issues

### 1.0.1
- None known at release time

### 1.0.0  
- Required manual backend URL configuration
- Placeholder URLs in documentation

## Support

For version-specific support:
- [GitHub Issues](https://github.com/nivlewd1/prompt-optimizer/issues)
- [Support Portal](https://promptoptimizer-blog.vercel.app/support)
- [Documentation](https://promptoptimizer-blog.vercel.app/docs)

When reporting issues, please include:
- Package version (`mcp-prompt-optimizer --version`)
- Node.js version (`node --version`)
- Operating system
- MCP client type and version
- Error messages and logs