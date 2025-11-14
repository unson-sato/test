# CLAUDE.md - AI Assistant Guide

**Last Updated:** 2025-11-14
**Repository:** test
**Purpose:** Claude Code test repository

---

## Table of Contents

1. [Repository Overview](#repository-overview)
2. [Codebase Structure](#codebase-structure)
3. [Development Workflows](#development-workflows)
4. [Git Conventions](#git-conventions)
5. [Code Conventions](#code-conventions)
6. [AI Assistant Guidelines](#ai-assistant-guidelines)
7. [Common Tasks](#common-tasks)
8. [Troubleshooting](#troubleshooting)

---

## Repository Overview

### Current State

This is a minimal test repository created for testing Claude Code functionality. The repository currently contains:

- **README.md**: Basic project description
- **CLAUDE.md**: This AI assistant guide (you are here)
- **.git/**: Git version control system

### Project Status

- **Stage:** Initial setup / Testing
- **Primary Branch:** Not yet established (currently on feature branch)
- **Active Development Branch:** `claude/claude-md-mhz0gcnog5fy01zt-01V6MduXUjHxq9xuUj4Dh2eW`
- **Programming Languages:** None (yet)
- **Build System:** None (yet)
- **Testing Framework:** None (yet)

### Repository Purpose

This repository serves as a testing ground for Claude Code functionality, including:
- AI-assisted development workflows
- Git operations and branch management
- Code generation and refactoring
- Documentation generation
- Collaboration patterns between humans and AI

---

## Codebase Structure

### Current Structure

```
/home/user/test/
├── .git/                  # Git version control
├── README.md              # Project overview
└── CLAUDE.md             # AI assistant guide (this file)
```

### Recommended Future Structure

As the project evolves, consider organizing it as follows:

```
/home/user/test/
├── .git/                  # Git version control
├── .github/               # GitHub-specific files
│   ├── workflows/         # CI/CD workflows
│   └── ISSUE_TEMPLATE/    # Issue templates
├── docs/                  # Documentation
│   ├── architecture.md    # Architecture decisions
│   ├── api.md            # API documentation
│   └── guides/           # User guides
├── src/                   # Source code
│   ├── main/             # Main application code
│   ├── utils/            # Utility functions
│   └── config/           # Configuration files
├── tests/                 # Test files
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── fixtures/         # Test fixtures
├── scripts/               # Build and utility scripts
├── .gitignore            # Git ignore rules
├── README.md             # Project overview
├── CLAUDE.md             # AI assistant guide
├── CONTRIBUTING.md       # Contribution guidelines
└── LICENSE               # License file
```

### Directory Conventions (To Be Established)

When adding code to this repository:

1. **Source Code:** Place in `src/` directory
2. **Tests:** Co-locate with source or place in `tests/` directory
3. **Documentation:** Place in `docs/` or keep alongside code
4. **Scripts:** Place build/deploy scripts in `scripts/` directory
5. **Configuration:** Keep config files at root or in `config/` directory

---

## Development Workflows

### Setting Up Development Environment

When this repository gains dependencies, document setup steps here:

```bash
# Clone the repository
git clone <repository-url>
cd test

# Install dependencies (example - adjust based on tech stack)
# npm install          # Node.js
# pip install -r requirements.txt  # Python
# bundle install       # Ruby

# Run tests (when available)
# npm test
# pytest
# make test
```

### Development Cycle

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/descriptive-name
   ```

2. **Make Changes**
   - Write code following established conventions
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Changes**
   - Run test suite
   - Verify functionality locally
   - Check for linting/formatting issues

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "descriptive message"
   ```

5. **Push and Create PR**
   ```bash
   git push -u origin feature/descriptive-name
   ```

### Testing Guidelines

*To be established when tests are added*

- Write tests for all new functionality
- Maintain test coverage above X%
- Run full test suite before committing
- Include both positive and negative test cases

---

## Git Conventions

### Branch Naming

Follow these conventions for branch names:

- **Feature branches:** `feature/short-description`
- **Bug fixes:** `fix/issue-description`
- **Documentation:** `docs/what-changed`
- **Refactoring:** `refactor/component-name`
- **Claude-generated:** `claude/claude-md-<session-id>`

### Commit Messages

Write clear, descriptive commit messages:

**Format:**
```
<type>: <short summary>

<optional detailed description>

<optional footer with issue references>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `style`: Code style changes (formatting)

**Examples:**
```
feat: add user authentication module

Implements JWT-based authentication with refresh tokens.
Includes middleware for protected routes.

Closes #123
```

```
fix: resolve null pointer exception in data processor

Added null checks before accessing nested properties.
```

### Git Push Operations

**Critical:** Always use the correct branch name format when pushing:

```bash
# Standard push with upstream
git push -u origin <branch-name>

# For Claude-generated branches, ensure format: claude/claude-md-*
git push -u origin claude/claude-md-mhz0gcnog5fy01zt-01V6MduXUjHxq9xuUj4Dh2eW
```

**Retry Logic:** If network errors occur, retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s).

### Git Fetch/Pull Operations

```bash
# Fetch specific branch
git fetch origin <branch-name>

# Pull latest changes
git pull origin <branch-name>
```

**Retry Logic:** Apply same exponential backoff as push operations.

---

## Code Conventions

### General Principles

*To be established based on chosen technology stack*

1. **Readability First:** Code should be self-documenting
2. **DRY Principle:** Don't Repeat Yourself
3. **SOLID Principles:** Follow object-oriented design principles
4. **Error Handling:** Always handle errors explicitly
5. **Security:** Never commit secrets or credentials

### Formatting

*Update when a formatter is chosen*

- Use consistent indentation (2 or 4 spaces, or tabs)
- Maximum line length: 80-120 characters
- Use meaningful variable and function names
- Add comments for complex logic

### Security Best Practices

1. **Never commit:**
   - API keys, tokens, passwords
   - `.env` files with secrets (use `.env.example` instead)
   - Private keys or certificates
   - Database credentials

2. **Always:**
   - Use `.gitignore` to exclude sensitive files
   - Validate and sanitize user input
   - Use parameterized queries for databases
   - Keep dependencies updated

---

## AI Assistant Guidelines

### Core Responsibilities

When working as an AI assistant on this repository:

1. **Understand Context First**
   - Read existing code before making changes
   - Understand the project's architecture and patterns
   - Check for related issues or discussions

2. **Follow Existing Patterns**
   - Match the coding style of surrounding code
   - Use existing utilities and helpers
   - Maintain consistency with current architecture

3. **Be Thorough**
   - Test changes before committing
   - Update documentation when changing functionality
   - Consider edge cases and error scenarios
   - Add appropriate comments for complex logic

4. **Communicate Clearly**
   - Explain significant changes or decisions
   - Ask for clarification when requirements are ambiguous
   - Provide context in commit messages
   - Document assumptions made

### Code Generation Guidelines

1. **Quality Standards**
   - Write production-ready code, not just prototypes
   - Include error handling and validation
   - Add appropriate logging
   - Consider performance implications

2. **Documentation**
   - Add docstrings/comments for public APIs
   - Update README when adding new features
   - Document configuration options
   - Include usage examples

3. **Testing**
   - Write tests for new functionality
   - Update tests when changing behavior
   - Ensure tests are meaningful and maintainable
   - Test both success and failure paths

### What to Avoid

1. **Don't:**
   - Introduce breaking changes without discussion
   - Add dependencies without justification
   - Commit commented-out code
   - Leave TODO comments without context
   - Make assumptions about user intent
   - Skip error handling
   - Ignore existing conventions

2. **Security Considerations**
   - Never generate code with known vulnerabilities
   - Avoid command injection risks
   - Prevent XSS in web applications
   - Use secure authentication methods
   - Validate all external input

### Task Planning

For complex tasks, use the TodoWrite tool to:

1. Break down the task into steps
2. Track progress through implementation
3. Ensure nothing is forgotten
4. Provide visibility to users

**Example:**
```
1. Research existing authentication implementation
2. Design JWT token structure
3. Implement authentication middleware
4. Add login/logout endpoints
5. Write tests for authentication flow
6. Update API documentation
```

---

## Common Tasks

### Adding a New Feature

1. Create feature branch: `git checkout -b feature/feature-name`
2. Implement feature with tests
3. Update documentation
4. Commit with descriptive message
5. Push to remote
6. Create pull request (if using PRs)

### Fixing a Bug

1. Create fix branch: `git checkout -b fix/bug-description`
2. Write failing test that reproduces bug
3. Fix the bug
4. Verify test passes
5. Commit and push
6. Reference issue number in commit message

### Refactoring Code

1. Ensure test coverage exists
2. Create refactor branch: `git checkout -b refactor/component-name`
3. Make refactoring changes
4. Verify all tests still pass
5. Commit with explanation of what was refactored and why
6. Push changes

### Updating Documentation

1. Create docs branch: `git checkout -b docs/what-changed`
2. Update relevant documentation files
3. Check for broken links or outdated information
4. Commit and push
5. No need for extensive testing unless docs include code examples

### Adding Dependencies

*When adding new dependencies:*

1. Justify why the dependency is needed
2. Check for security vulnerabilities
3. Verify license compatibility
4. Document in README or relevant docs
5. Update dependency files (package.json, requirements.txt, etc.)

---

## Troubleshooting

### Common Issues

#### Git Push Failures (403 Error)

**Problem:** Push fails with HTTP 403 error

**Solution:** Ensure branch name follows the format `claude/claude-md-*` when using Claude Code

```bash
# Correct format
git push -u origin claude/claude-md-mhz0gcnog5fy01zt-01V6MduXUjHxq9xuUj4Dh2eW

# Incorrect - will fail
git push -u origin feature/my-feature
```

#### Network Timeouts

**Problem:** Git operations timeout

**Solution:** Commands should automatically retry with exponential backoff (2s, 4s, 8s, 16s)

#### Merge Conflicts

**Problem:** Conflicts when merging branches

**Solution:**
```bash
# Update your branch
git fetch origin
git merge origin/main

# Resolve conflicts manually
# Edit conflicting files
git add <resolved-files>
git commit -m "resolve merge conflicts"
```

### Getting Help

When stuck or uncertain:

1. **Read the documentation** - Check README and relevant docs
2. **Search existing code** - Look for similar implementations
3. **Ask for clarification** - Don't make assumptions about requirements
4. **Consult external resources** - Official documentation for libraries/frameworks
5. **Raise questions** - If something seems wrong, ask about it

---

## Appendix

### Useful Commands

```bash
# Check git status
git status

# View commit history
git log --oneline --graph --all

# View changes
git diff

# View specific file history
git log -p <file-path>

# Discard local changes
git checkout -- <file-path>

# Create and switch to new branch
git checkout -b <branch-name>

# List all branches
git branch -a

# Delete local branch
git branch -d <branch-name>
```

### Resources

*Add links to relevant documentation as the project grows*

- Project Documentation: docs/
- Issue Tracker: (to be established)
- Contributing Guide: CONTRIBUTING.md (to be created)
- Code of Conduct: (to be created if needed)

---

## Maintenance

This CLAUDE.md file should be updated when:

- Project structure changes significantly
- New conventions are established
- Development workflows change
- New tools or frameworks are added
- Common issues are discovered and resolved

**Update Frequency:** Review and update quarterly or after major changes.

**Last Updated By:** Claude (Initial creation)
**Next Review Date:** 2026-02-14

---

## Version History

| Version | Date       | Changes                          | Updated By |
|---------|------------|----------------------------------|------------|
| 1.0.0   | 2025-11-14 | Initial creation                 | Claude     |

