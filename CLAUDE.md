# CLAUDE.md - Claude Code Assistant Guide

**Last Updated:** 2025-11-15
**Repository:** test
**Environment:** Claude Code (Session-driven AI Development)
**Purpose:** Claude Code test repository

---

## Table of Contents

1. [Repository Overview](#repository-overview)
2. [Claude Code Environment](#claude-code-environment)
3. [Codebase Structure](#codebase-structure)
4. [Development Workflow](#development-workflow)
5. [Git Operations](#git-operations)
6. [Code Conventions](#code-conventions)
7. [AI Assistant Guidelines](#ai-assistant-guidelines)
8. [Common Tasks](#common-tasks)
9. [Troubleshooting](#troubleshooting)

---

## Repository Overview

### Current State

This is a minimal test repository created for testing Claude Code functionality. The repository currently contains:

- **README.md**: Basic project description
- **CLAUDE.md**: This AI assistant guide (you are here)
- **.git/**: Git version control system

### Project Status

- **Stage:** Initial setup / Testing
- **Environment:** Claude Code (AI-assisted development)
- **Git Remote:** Local proxy (http://local_proxy@127.0.0.1)
- **Current Branch:** `claude/claude-md-mhz0gcnog5fy01zt-01V6MduXUjHxq9xuUj4Dh2eW`
- **Programming Languages:** None (yet)
- **Build System:** None (yet)
- **Testing Framework:** None (yet)

### Repository Purpose

This repository serves as a testing ground for Claude Code functionality, including:
- AI-assisted development workflows
- Session-driven code generation
- Git operations and branch management
- Documentation generation
- Collaboration patterns between humans and AI assistants

---

## Claude Code Environment

### What is Claude Code?

This repository is being developed in a **Claude Code environment**, where an AI assistant (Claude) directly executes development tasks through sessions. This differs from traditional development workflows.

### Key Characteristics

1. **Session-Driven Development**
   - Each development session uses a dedicated branch
   - Claude automatically manages branch creation and switching
   - Sessions are tracked by unique session IDs

2. **Local Proxy Git Remote**
   - Git remote uses local proxy: `http://local_proxy@127.0.0.1:PORT`
   - Not directly connected to GitHub.com during sessions
   - Changes are synchronized through the proxy

3. **Automatic Branch Management**
   - Branches follow the format: `claude/claude-md-<session-id>`
   - **CRITICAL**: Branches MUST start with `claude/` for push operations to succeed
   - Claude creates and manages these branches automatically

4. **Tool Availability**
   - **Available**: Bash, Read, Write, Edit, Grep, Glob, WebFetch, WebSearch, TodoWrite
   - **NOT Available**: `gh` CLI (GitHub CLI)
   - **NOT Available**: Direct GitHub API access

5. **Commit Authentication**
   - Commits are signed using SSH key signing
   - Author: Claude (noreply@anthropic.com)
   - Signing key: /home/claude/.ssh/commit_signing_key.pub

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

## Development Workflow

### Claude Code Session Workflow

Development in Claude Code follows a session-based workflow:

1. **User Initiates Session**
   - User opens Claude Code and provides a task or request
   - Claude analyzes the request and existing codebase

2. **Claude Plans and Executes**
   - Claude creates a todo list for complex tasks (using TodoWrite tool)
   - Claude reads relevant files to understand context
   - Claude makes changes using Write/Edit tools
   - Claude runs tests or validation as needed

3. **Claude Commits Changes**
   - Claude commits changes with descriptive messages
   - Only commits when explicitly requested by user or task requires it
   - Follows conventional commit message format

4. **Claude Pushes to Remote**
   - Pushes to the session-specific branch (format: `claude/claude-md-<session-id>`)
   - Uses retry logic with exponential backoff for network errors
   - **CRITICAL**: Branch name MUST start with `claude/` or push will fail (403 error)

5. **User Reviews and Provides Feedback**
   - User reviews changes and provides additional instructions
   - Claude continues iterating based on feedback

### For Human Developers (Manual Development)

If you need to develop manually outside Claude Code sessions:

```bash
# Clone the repository
git clone <repository-url>
cd test

# Create a feature branch (NOT for Claude Code - use different format)
git checkout -b feature/descriptive-name

# Make changes, commit, and push
git add .
git commit -m "type: description"
git push -u origin feature/descriptive-name
```

**Note**: Manual branches should NOT use the `claude/` prefix unless you're continuing a Claude Code session.

### Environment Setup

When this repository gains dependencies, document setup steps here:

```bash
# Install dependencies (example - adjust based on tech stack)
# npm install          # Node.js
# pip install -r requirements.txt  # Python
# bundle install       # Ruby

# Run tests (when available)
# npm test
# pytest
# make test
```

### Testing Guidelines

*To be established when tests are added*

- Write tests for all new functionality
- Run full test suite before committing
- Include both positive and negative test cases
- Document test requirements in this file

---

## Git Operations

### Branch Management

#### Claude Code Sessions (Automatic)

- **Format:** `claude/claude-md-<session-id>`
- **Example:** `claude/claude-md-mhz0gcnog5fy01zt-01V6MduXUjHxq9xuUj4Dh2eW`
- **Management:** Claude automatically creates and switches branches
- **Restriction:** MUST start with `claude/` prefix for pushes to succeed
- **Lifespan:** Session-specific, created per Claude Code session

#### Manual Development (Human Developers)

If developing outside Claude Code, use these branch naming conventions:

- **Feature branches:** `feature/short-description`
- **Bug fixes:** `fix/issue-description`
- **Documentation:** `docs/what-changed`
- **Refactoring:** `refactor/component-name`

**Important:** Do NOT use `claude/` prefix for manual branches.

### Commit Messages

All commits should follow the Conventional Commits format:

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
```

```
fix: resolve null pointer exception in data processor

Added null checks before accessing nested properties.
```

```
docs: update CLAUDE.md with session workflow

Revised to reflect Claude Code environment specifics.
```

### Push Operations

#### For Claude Code (Automatic)

Claude handles pushes automatically with these characteristics:

```bash
# Claude uses this format
git push -u origin claude/claude-md-<session-id>
```

**Retry Logic:**
- Automatic retry up to 4 times on network errors
- Exponential backoff: 2s, 4s, 8s, 16s
- **Critical:** 403 errors indicate incorrect branch naming (must start with `claude/`)

#### For Manual Development

```bash
# Standard push with upstream tracking
git push -u origin <branch-name>
```

### Fetch/Pull Operations

```bash
# Fetch specific branch
git fetch origin <branch-name>

# Pull latest changes
git pull origin <branch-name>
```

**Retry Logic:** Apply same exponential backoff (2s, 4s, 8s, 16s) on network errors.

### Remote Configuration

- **Remote Name:** origin
- **Remote URL:** `http://local_proxy@127.0.0.1:<port>/git/<owner>/<repo>`
- **Authentication:** Handled by local proxy
- **Signing:** SSH key signing enabled for commits

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

### Claude Code Operating Principles

As an AI assistant (Claude) working in this repository, follow these guidelines:

#### 1. Context Analysis

**Before any task:**
- Read CLAUDE.md (this file) to understand environment and conventions
- Use Glob/Grep tools to explore codebase structure
- Read relevant files with the Read tool to understand existing patterns
- For open-ended exploration, use the Task tool with Explore subagent

**Don't:**
- Make changes without understanding existing code
- Assume project structure without verification
- Skip reading relevant documentation

#### 2. Task Planning and Tracking

**For complex tasks (3+ steps or non-trivial work):**
- **MUST** use TodoWrite tool to create task list
- Break down work into specific, actionable items
- Mark tasks as in_progress when starting (exactly ONE at a time)
- Mark tasks as completed IMMEDIATELY after finishing
- Update todo list as new sub-tasks are discovered

**Simple tasks (1-2 trivial steps):**
- Proceed directly without TodoWrite overhead

**Example Todo List:**
```
1. Explore existing authentication code
2. Design new OAuth integration approach
3. Implement OAuth provider configuration
4. Add OAuth callback handlers
5. Write integration tests
6. Update documentation
```

#### 3. Code Generation Standards

**Quality Requirements:**
- Write production-ready code, not prototypes
- Include comprehensive error handling
- Add appropriate logging where needed
- Consider performance and security implications
- Follow existing code style and patterns

**Documentation:**
- Add clear comments for complex logic
- Update README.md when adding features
- Document configuration options and environment variables
- Include usage examples for new functionality

**Testing:**
- Write tests for new functionality
- Update tests when changing behavior
- Test both success and failure paths
- Run tests before committing (when available)

#### 4. Security Best Practices

**Never:**
- Generate code with known vulnerabilities (SQL injection, XSS, command injection)
- Commit secrets, API keys, passwords, or credentials
- Skip input validation and sanitization
- Use insecure authentication methods

**Always:**
- Validate and sanitize external input
- Use parameterized queries for databases
- Implement proper error handling without exposing sensitive data
- Follow OWASP security guidelines

#### 5. Tool Usage in Claude Code

**Preferred Tools:**
- **File Operations**: Use Read, Write, Edit (NOT cat, echo >)
- **Search**: Use Grep, Glob (NOT grep/find commands)
- **Exploration**: Use Task tool with Explore subagent for open-ended searches
- **Todo Tracking**: Use TodoWrite for complex tasks

**Bash Tool Usage:**
- Use for actual terminal operations (git, npm, pytest, etc.)
- Do NOT use for file operations (cat, echo, sed, awk)
- Do NOT use for communication with user (no echo for messages)
- Always quote paths with spaces: `cd "path with spaces"`

**Parallel Tool Execution:**
- Run independent tool calls in parallel (single message, multiple tools)
- Run dependent operations sequentially (use && in Bash or separate messages)

#### 6. Git and Commit Practices

**Branch Management:**
- Claude automatically manages branches (format: `claude/claude-md-<session-id>`)
- Do NOT manually create branches unless explicitly requested
- Current branch is tracked in environment info

**Committing Changes:**
- **ONLY** commit when user explicitly requests or task completion requires it
- Follow Conventional Commits format (feat:, fix:, docs:, etc.)
- Use heredoc for multi-line commit messages
- Include descriptive summary and detailed explanation

**Commit Message Example:**
```bash
git commit -m "$(cat <<'EOF'
feat: add user profile management

Implements CRUD operations for user profiles including:
- Profile creation and validation
- Update with conflict detection
- Secure deletion with cascade handling

Includes comprehensive error handling and input validation.
EOF
)"
```

**Push Operations:**
- Push to session branch: `git push -u origin claude/claude-md-<session-id>`
- Automatic retry with exponential backoff on network errors
- Never skip hooks (--no-verify) unless explicitly requested

#### 7. Communication

**With User:**
- Provide clear, concise explanations
- Ask for clarification when requirements are ambiguous
- Explain significant decisions or tradeoffs
- Report errors and blockers clearly
- Use markdown formatting for readability
- Do NOT use emojis unless explicitly requested

**In Code:**
- Write self-documenting code with clear naming
- Add comments for non-obvious logic
- Document assumptions and limitations
- Include TODO comments only with full context

#### 8. What to Avoid

**Never:**
- Use `gh` CLI (not available in this environment)
- Assume GitHub-specific features are available
- Create unnecessary files (prefer editing existing)
- Commit without user request (except when task requires it)
- Make breaking changes without discussion
- Add dependencies without justification
- Leave commented-out code
- Skip error handling

#### 9. Environment-Specific Notes

**This Environment Has:**
- Local proxy git remote (not direct GitHub connection)
- SSH-signed commits (automatic)
- Specific branch naming requirements (`claude/` prefix)
- Limited external tool availability (no gh CLI)

**This Environment Does NOT Have:**
- Direct GitHub API access
- GitHub CLI (`gh` command)
- Pull request creation from CLI
- GitHub Actions visibility

---

## Common Tasks

### For Claude (AI Assistant)

#### Implementing a New Feature

1. **Understand Requirements**
   - Clarify ambiguous requirements with user
   - Explore existing codebase for related functionality
   - Create todo list with TodoWrite for complex features

2. **Implementation**
   - Read existing code to understand patterns
   - Implement feature following project conventions
   - Add error handling and validation
   - Write tests for new functionality

3. **Documentation and Commit**
   - Update README or relevant docs
   - Add code comments for complex logic
   - Commit with descriptive message (feat: ...)
   - Push to session branch

#### Fixing a Bug

1. **Reproduce and Understand**
   - Read code to understand the bug
   - Identify root cause
   - Write failing test if possible (TDD approach)

2. **Fix and Verify**
   - Implement fix with proper error handling
   - Verify test passes (or manually test if no test suite)
   - Check for similar issues elsewhere

3. **Document and Commit**
   - Add comments explaining the fix if needed
   - Commit with fix: type message
   - Reference issue number if applicable
   - Push to session branch

#### Refactoring Code

1. **Safety First**
   - Ensure tests exist (or add them first)
   - Understand current implementation thoroughly
   - Plan refactoring approach

2. **Refactor**
   - Make changes incrementally
   - Maintain existing functionality
   - Improve code structure, readability, or performance
   - Run tests after each significant change

3. **Document and Commit**
   - Explain what was refactored and why
   - Commit with refactor: type message
   - Push to session branch

#### Updating Documentation

1. **Identify What Needs Updates**
   - Code changes that affect usage
   - New features requiring documentation
   - Outdated information needing correction

2. **Update Documentation**
   - Modify README.md, CLAUDE.md, or other docs
   - Ensure examples are accurate and tested
   - Check for broken links or references

3. **Commit**
   - Use docs: type commit message
   - No extensive testing needed unless docs include code
   - Push to session branch

#### Adding Dependencies

**Before Adding:**
1. Justify why the dependency is necessary
2. Check for security vulnerabilities (npm audit, safety, etc.)
3. Verify license compatibility with project
4. Consider bundle size and performance impact

**When Adding:**
1. Update dependency file (package.json, requirements.txt, etc.)
2. Document the dependency in README
3. Update setup instructions if needed
4. Commit with chore: or feat: depending on context
5. Push to session branch

### For Human Developers (Manual Work)

#### Standard Development Flow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and test
# ... edit files ...

# Commit and push
git add .
git commit -m "feat: add my feature"
git push -u origin feature/my-feature

# Create PR through GitHub web interface or other means
```

**Note:** Do not use `claude/` prefix for manual branches.

---

## Troubleshooting

### Common Issues in Claude Code Environment

#### Git Push Failures (403 Error)

**Problem:** Push fails with HTTP 403 Forbidden error

**Root Cause:** Branch name does not start with `claude/` prefix

**Solution:**
- Ensure branch follows format: `claude/claude-md-<session-id>`
- Claude automatically uses correct format, but if manually pushing:
  ```bash
  # Correct - will succeed
  git push -u origin claude/claude-md-mhz0gcnog5fy01zt-01V6MduXUjHxq9xuUj4Dh2eW

  # Incorrect - will fail with 403
  git push -u origin feature/my-feature
  git push -u origin main
  ```

**For Claude:**
- This should not occur if using automatic branch management
- If it does, verify you're on the correct session branch

#### Network Timeouts

**Problem:** Git operations timeout or fail with network errors

**Solution:**
- Retry automatically implemented with exponential backoff (2s, 4s, 8s, 16s)
- Affects: push, fetch, pull operations
- If persistent, notify user of network issues

**For Claude:**
- Implement retry logic in git operations
- Report to user if all retries exhausted

#### Tool Not Available Errors

**Problem:** Error when trying to use `gh` CLI or GitHub-specific features

**Root Cause:** GitHub CLI is not available in Claude Code environment

**Solution:**
- Do NOT use `gh` commands
- Do NOT attempt direct GitHub API calls
- For PR creation, inform user to use GitHub web interface
- For issue retrieval, ask user to provide information directly

**For Claude:**
- Never invoke `gh` commands
- Check tool availability before use
- Suggest alternative approaches (web interface, manual steps)

#### File Not Found During Read/Edit

**Problem:** Read or Edit tool fails to find file

**Root Cause:**
- Incorrect file path (relative vs absolute)
- File doesn't exist yet
- Typo in filename

**Solution:**
1. Use Glob to verify file exists: `**/*filename*`
2. Check current working directory context
3. Use absolute paths for Read/Write/Edit operations
4. List directory contents with `ls` before reading

**For Claude:**
- Always verify file existence before operations
- Use Glob tool to search for files when uncertain
- Provide clear error messages to user

#### Merge Conflicts

**Problem:** Conflicts when merging or pulling branches

**Solution:**
```bash
# Fetch latest changes
git fetch origin <branch-name>

# Attempt merge
git merge origin/<branch-name>

# If conflicts occur, resolve manually
# Edit conflicting files, then:
git add <resolved-files>
git commit -m "resolve: merge conflicts from <branch-name>"
```

**For Claude:**
- Report conflicts clearly to user
- Identify conflicting files
- Ask user for guidance on resolution approach
- Do not attempt automatic conflict resolution without user input

#### Unexpected Code Behavior

**Problem:** Generated code doesn't work as expected

**Debugging Steps:**
1. Review error messages carefully
2. Check file was actually written/edited (use Read to verify)
3. Verify dependencies are installed
4. Run tests to identify specific failures
5. Check for typos or syntax errors

**For Claude:**
- Read generated files to verify changes
- Run appropriate test/validation commands
- Provide detailed error analysis to user
- Iterate on fixes based on error messages

### Getting Help and Clarification

#### For Claude (AI Assistant)

When stuck or uncertain:

1. **Read Documentation**
   - Check README.md for project overview
   - Review CLAUDE.md (this file) for conventions
   - Look for inline code comments

2. **Explore Codebase**
   - Use Glob to find relevant files
   - Use Grep to search for similar implementations
   - Use Task/Explore for open-ended investigation

3. **Ask User for Clarification**
   - When requirements are ambiguous
   - When multiple valid approaches exist
   - When blocked by external dependencies
   - When user input/decision is needed

4. **Consult External Resources**
   - Use WebSearch for current information
   - Use WebFetch for specific documentation pages
   - Check official docs for libraries/frameworks

5. **Report Issues Clearly**
   - Describe what you were trying to do
   - Show error messages or unexpected behavior
   - Explain what you've already tried
   - Ask specific questions

#### For Human Developers

If encountering issues outside Claude Code sessions:

1. Check git status and current branch
2. Verify remote configuration: `git remote -v`
3. Review recent commits: `git log --oneline`
4. Check Claude Code documentation for environment-specific issues

---

## Appendix

### Useful Commands

#### Git Commands (For Both Claude and Humans)

```bash
# Check git status
git status

# View commit history
git log --oneline --graph --all

# View changes
git diff

# View specific file history
git log -p <file-path>

# List all branches
git branch -a

# Check remote configuration
git remote -v

# View current branch
git branch --show-current
```

#### For Human Developers Only

```bash
# Discard local changes
git checkout -- <file-path>

# Create and switch to new branch (do NOT use claude/ prefix)
git checkout -b <branch-name>

# Delete local branch
git branch -d <branch-name>

# Merge another branch
git merge <branch-name>
```

### Claude Code Tool Reference

**File Operations:**
- `Read`: Read file contents (supports images, PDFs, notebooks)
- `Write`: Create new files (avoid when editing existing is possible)
- `Edit`: Modify existing files with exact string replacement
- `Glob`: Find files by pattern (e.g., `**/*.js`)
- `Grep`: Search file contents with regex

**Execution:**
- `Bash`: Run terminal commands (git, npm, pytest, etc.)
- `BashOutput`: Check output from background processes
- `KillShell`: Terminate background processes

**Planning and Organization:**
- `TodoWrite`: Create and manage task lists

**Research:**
- `Task`: Launch specialized agents (Explore, Plan, etc.)
- `WebSearch`: Search the web for current information
- `WebFetch`: Fetch and analyze specific URLs

**NOT Available:**
- `gh` (GitHub CLI)
- Direct GitHub API access

### Resources

**Claude Code:**
- Claude Code Documentation: https://docs.claude.com/claude-code
- Environment: Linux 4.4.0
- Working Directory: /home/user/test

**This Repository:**
- README.md: Project overview
- CLAUDE.md: This file (AI assistant guide)
- Future docs/: To be created as needed

**External:**
- Conventional Commits: https://www.conventionalcommits.org/
- OWASP Security: https://owasp.org/www-project-top-ten/

---

## Maintenance

### When to Update This File

Update CLAUDE.md when:

- **Project structure changes** (new directories, reorganization)
- **New conventions established** (coding style, testing requirements)
- **Development workflow changes** (new tools, processes)
- **New dependencies added** (frameworks, libraries)
- **Common issues discovered** (and solutions found)
- **Claude Code environment changes** (new tools, restrictions)

### Update Process

1. Edit CLAUDE.md with changes
2. Update "Last Updated" date in header
3. Add entry to Version History table below
4. Commit with `docs:` type message
5. Push to repository

### Review Schedule

- **Regular Review:** Quarterly (every 3 months)
- **Ad-hoc Review:** After major project changes
- **Next Scheduled Review:** 2026-02-15

**Last Updated:** 2025-11-15
**Last Updated By:** Claude (Revision for Claude Code environment)

---

## Version History

| Version | Date       | Changes                                                      | Updated By |
|---------|------------|--------------------------------------------------------------|------------|
| 1.0.0   | 2025-11-14 | Initial creation                                             | Claude     |
| 2.0.0   | 2025-11-15 | Major revision for Claude Code environment specifics         | Claude     |
|         |            | - Added Claude Code Environment section                      |            |
|         |            | - Revised workflow for session-driven development           |            |
|         |            | - Updated Git operations for claude/ branch requirements     |            |
|         |            | - Enhanced AI Assistant Guidelines with tool usage           |            |
|         |            | - Removed GitHub-specific features (gh CLI, PR creation)     |            |
|         |            | - Added comprehensive troubleshooting for Claude Code        |            |
|         |            | - Updated all examples to reflect actual environment         |            |

