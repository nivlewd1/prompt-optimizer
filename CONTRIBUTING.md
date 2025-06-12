# Contributing to Prompt Optimizer

Thank you for your interest in contributing to Prompt Optimizer! This document provides guidelines for contributing to the project.

## Table of Contents

- [Types of Contributions](#types-of-contributions)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Community Guidelines](#community-guidelines)

## Types of Contributions

We welcome several types of contributions:

### 🐛 Bug Reports
- Report bugs in the MCP package
- Documentation errors
- API client issues
- Integration problems

### 💡 Feature Requests
- New MCP client integrations
- Enhanced documentation
- Developer tools and utilities
- Integration examples

### 📚 Documentation
- Improve existing documentation
- Add usage examples
- Create tutorials and guides
- Translate documentation

### 🔧 Code Contributions
- MCP package improvements
- Client library enhancements
- Integration examples
- Development tools

**Note**: Core optimization algorithms are proprietary and not open for contribution.

## Getting Started

### Prerequisites

- Node.js 16+ for MCP package development
- Git for version control
- A Prompt Optimizer API key for testing

### Setting Up Development Environment

1. **Fork the Repository**
   ```bash
   git clone https://github.com/your-username/prompt-optimizer.git
   cd prompt-optimizer
   ```

2. **Install Dependencies**
   ```bash
   cd mcp-package
   npm install
   ```

3. **Set Up API Key**
   ```bash
   node index.js --setup
   # Enter your API key when prompted
   ```

4. **Run Tests**
   ```bash
   npm test
   ```

## Development Process

### 1. Issue First

Before making significant changes:
- Check existing issues
- Create a new issue to discuss your proposal
- Get feedback from maintainers

### 2. Branch Naming

Use descriptive branch names:
- `feature/add-new-client-support`
- `bugfix/fix-config-loading`
- `docs/improve-api-examples`
- `test/add-integration-tests`

### 3. Commit Messages

Follow conventional commits:
```
type(scope): description

[optional body]

[optional footer]
```

Examples:
```
feat(mcp): add support for new optimization goal
bugfix(api): fix timeout handling in requests
docs(readme): update installation instructions
test(client): add unit tests for error handling
```

## Code Standards

### JavaScript/Node.js

- Use ES6+ features appropriately
- Follow consistent indentation (2 spaces)
- Use meaningful variable and function names
- Add JSDoc comments for public APIs
- Handle errors appropriately

### Example Code Style

```javascript
/**
 * Validates and processes optimization goals
 * @param {string[]} goals - Array of optimization goal names
 * @returns {string[]} Filtered valid goals
 */
function validateGoals(goals) {
  const validGoals = [
    'clarity', 'conciseness', 'technical_accuracy'
    // ... other goals
  ];
  
  const filtered = goals.filter(goal => validGoals.includes(goal));
  return filtered.length > 0 ? filtered : ['clarity'];
}
```

### Documentation

- Use clear, concise language
- Include code examples
- Provide both basic and advanced usage
- Keep examples up-to-date

## Testing

### Running Tests

```bash
# Run all tests
npm test

# Run specific test file
node test-package.js

# Test with coverage (if available)
npm run test:coverage
```

### Writing Tests

- Test all public APIs
- Include edge cases
- Test error conditions
- Mock external dependencies

### Test Structure

```javascript
const { expect } = require('chai');
const Config = require('./lib/config');

describe('Config Management', () => {
  it('should save and load API keys correctly', () => {
    const config = new Config();
    const testKey = 'sk-opt-test123';
    
    const saved = config.setApiKey(testKey);
    const loaded = config.getApiKey();
    
    expect(saved).to.be.true;
    expect(loaded).to.equal(testKey);
  });
});
```

## Documentation

### Types of Documentation

1. **API Documentation**: JSDoc comments in code
2. **User Guides**: Step-by-step instructions
3. **Examples**: Working code samples
4. **Troubleshooting**: Common issues and solutions

### Documentation Standards

- Use Markdown for formatting
- Include code examples that work
- Test all commands and examples
- Update screenshots when UI changes

## Submitting Changes

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow code standards
   - Add tests if applicable
   - Update documentation

3. **Test Thoroughly**
   ```bash
   npm test
   # Test with real API if possible
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat(scope): add new feature"
   ```

5. **Push to Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Use descriptive title
   - Fill out PR template
   - Link related issues
   - Request review

### Pull Request Template

```markdown
## Description
[Brief description of changes]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Tests pass
- [ ] Manual testing completed
- [ ] Documentation updated

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added where needed
- [ ] No breaking changes
```

### Review Process

1. **Automated Checks**
   - Tests must pass
   - Code style checks
   - Security scanning

2. **Human Review**
   - Code quality assessment
   - Documentation review
   - Testing verification

3. **Feedback Integration**
   - Address reviewer comments
   - Make requested changes
   - Re-request review

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Avoid personal attacks or harassment

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **Pull Requests**: Code discussions
- **Discord**: Community chat (link in README)
- **Email**: Direct contact for sensitive issues

### Getting Help

- Check existing documentation first
- Search issues for similar problems
- Ask questions in Discord community
- Create detailed issue if needed

## Recognition

Contributors are recognized through:

- **Contributors List**: Added to repository
- **Release Notes**: Mentioned in changelogs
- **Discord Role**: Special contributor role
- **Swag**: Occasional contributor merchandise

## Legal

### License Agreement

By contributing, you agree that:
- Your contributions are original work
- You grant us rights to use your contributions
- Your contributions are compatible with project license

### Intellectual Property

- **Your Code**: You retain copyright to your contributions
- **Our Code**: Core optimization algorithms remain proprietary
- **Combined Work**: Final product follows project license

## Quick Start Checklist

- [ ] Read this contributing guide
- [ ] Set up development environment
- [ ] Run tests successfully
- [ ] Create feature branch
- [ ] Make small test change
- [ ] Submit first pull request
- [ ] Join Discord community

## Questions?

If you have questions about contributing:

- 📧 Email: contributors@promptoptimizer.com
- 💬 Discord: [Community Server](https://discord.gg/prompt-optimizer)
- 🐛 Issues: [GitHub Issues](https://github.com/nivlewd1/prompt-optimizer/issues)

Thank you for contributing to Prompt Optimizer! 🚀