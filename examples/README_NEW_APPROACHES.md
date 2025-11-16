# New Approaches for Non-Interactive Claude Code Workflows

**Created**: 2025-11-16
**Purpose**: Innovative architectures for production-ready Claude Code automation

---

## Overview

This directory contains **4 new architectural approaches** for building robust, non-interactive Claude Code workflows beyond the basic Method 1/Method 2 comparison.

All approaches are designed for:
- **Non-interactive mode**: `claude -p --dangerously-skip-permission`
- **Production readiness**: Error handling, retries, persistence
- **Automation**: Script-driven, no human intervention required

---

## Table of Contents

1. [File-Based Workflow Architecture](#1-file-based-workflow-architecture)
2. [Declarative Workflow System](#2-declarative-workflow-system)
3. [Message History Persistence](#3-message-history-persistence)
4. [Error Handling & Retry Mechanisms](#4-error-handling--retry-mechanisms)
5. [Complete Integration Example](#5-complete-integration-example)
6. [Quick Start Guide](#quick-start-guide)
7. [Comparison Matrix](#comparison-matrix)

---

## 1. File-Based Workflow Architecture

**File**: `docs/file_based_workflow_architecture.md`
**Implementation**: Part of complete example

### Concept

Use **files as the communication layer** between orchestrator and Claude Code:

```
Orchestrator → prompt.txt → claude -p → response.json → Process → Loop
```

### Directory Structure

```
workspace/
├── state/
│   ├── session.json          # Current state
│   ├── message_history.jsonl # Full history
│   └── tool_results.json     # Latest results
├── prompts/                   # Generated prompts
├── responses/                 # Claude responses
└── config/                    # Workflow config
```

### Advantages

✅ **Debuggable**: All state visible in files
✅ **Resumable**: Can pause and restart
✅ **Auditable**: Complete history
✅ **Simple**: No complex in-memory state

### Use Cases

- Long-running batch processes
- Multi-step data pipelines
- Workflows that need audit trails

---

## 2. Declarative Workflow System

**File**: `examples/declarative_workflow.py`

### Concept

Define workflows in **YAML**, execute with an engine:

```yaml
name: Data Analysis Pipeline
steps:
  - name: Load Data
    prompt: "Load data from {data_file}"
    tools: [read_file, execute_python]
    output_variable: data

  - name: Analyze
    prompt: "Analyze: {data}"
    tools: [execute_python]
```

### Features

- **Template variables**: `{variable}` substitution
- **Conditional steps**: Execute based on previous results
- **Output capture**: Store results in variables
- **Error handling**: `continue_on_error` flag

### Advantages

✅ **Declarative**: Describe WHAT, not HOW
✅ **Reusable**: Share workflow templates
✅ **Version control**: YAML is git-friendly
✅ **Non-technical friendly**: Business users can write workflows

### Use Cases

- Standardized processes
- Team collaboration
- Workflow templates library

---

## 3. Message History Persistence

**File**: `examples/message_history_persistence.py`

### Three Strategies

| Strategy | Format | Speed | Queryable | Human-Readable |
|----------|--------|-------|-----------|----------------|
| **SQLite** | Database | ⚡⚡⚡ | ✅ Yes | ❌ No |
| **JSONL** | Text file | ⚡ | ❌ No | ✅ Yes |
| **Hybrid** | Both | ⚡⚡ | ✅ Yes | ✅ Yes |

### Hybrid Approach (Recommended)

Combines best of both:
- **SQLite** for fast queries and stats
- **JSONL** for human readability and backups

```python
store = HybridMessageStore(
    db_path="./workspace/messages.db",
    jsonl_path="./workspace/messages.jsonl"
)

# Save message
store.save_message(message)

# Query efficiently
messages = store.get_messages(session_id)
stats = store.get_session_stats(session_id)
```

### Advantages

✅ **Fast queries**: SQLite indices
✅ **Auditable**: JSONL backup
✅ **Scalable**: Handles large histories
✅ **Debuggable**: Can inspect JSONL files

### Use Cases

- Long-running sessions
- Need for analytics/reporting
- Compliance/audit requirements

---

## 4. Error Handling & Retry Mechanisms

**File**: `examples/error_handling_retry.py`

### Four Strategies

#### A. Exponential Backoff Retry

```python
@exponential_backoff_retry(max_retries=4, base_delay=2.0)
def call_api():
    # Will retry with: 2s, 4s, 8s, 16s delays
    pass
```

#### B. Circuit Breaker Pattern

```python
circuit = CircuitBreaker(failure_threshold=5, recovery_timeout=60)

circuit.call(risky_operation)
# Opens circuit after 5 failures
# Attempts recovery after 60s
```

#### C. Adaptive Retry

Automatically adjusts retry strategy based on error type:
- **Network errors**: Fast retry (2s base)
- **Rate limits**: Slow retry (60s base)
- **Validation errors**: No retry

```python
@adaptive_retry
def smart_call():
    # Automatically adapts based on error
    pass
```

#### D. Graceful Degradation

```python
result = GracefulDegradation.with_fallback(
    primary_func=lambda: call_real_api(),
    fallback_func=lambda: return_cached_response()
)
```

### Error Classification

Automatically classifies errors:
- `NETWORK`: Connection issues
- `API_LIMIT`: Rate limiting
- `VALIDATION`: Input errors
- `TIMEOUT`: Timeouts
- `UNKNOWN`: Other

### Advantages

✅ **Resilient**: Handles transient failures
✅ **Intelligent**: Adapts to error types
✅ **Production-ready**: Prevents cascading failures
✅ **Observable**: Detailed logging

### Use Cases

- Production deployments
- Unreliable networks
- API rate limiting scenarios

---

## 5. Complete Integration Example

**File**: `examples/complete_integration_example.py`

### All Features Combined

```python
engine = ProductionWorkflowEngine(
    workspace_dir="./production_workspace",
    enable_persistence=True,      # Hybrid message store
    enable_circuit_breaker=True   # Protection
)

engine.execute_workflow("workflow.yaml", max_iterations=10)
```

### What It Includes

1. ✅ File-based state management
2. ✅ YAML workflow definitions
3. ✅ Hybrid message persistence (SQLite + JSONL)
4. ✅ Exponential backoff retry
5. ✅ Circuit breaker protection
6. ✅ Graceful degradation
7. ✅ Adaptive error handling
8. ✅ Template variable substitution
9. ✅ Tool execution
10. ✅ Comprehensive logging

### Production Features

- **Session management**: Unique session IDs
- **State persistence**: Resume from failures
- **Audit trail**: Complete history
- **Error recovery**: Multiple strategies
- **Resource cleanup**: Proper shutdown

---

## Quick Start Guide

### 1. Basic File-Based Workflow

```bash
# Create workspace
mkdir -p workspace/{state,prompts,responses}

# Run orchestrator
python examples/file_based_orchestrator.py
```

### 2. Declarative Workflow

```bash
# Create workflow YAML
cat > workflow.yaml << EOF
name: My Workflow
steps:
  - name: Step 1
    prompt: "Do something"
    tools: [read_file]
EOF

# Execute
python examples/declarative_workflow.py
```

### 3. Message Persistence

```python
from message_history_persistence import HybridMessageStore

store = HybridMessageStore("messages.db", "messages.jsonl")
store.save_message(message)
stats = store.get_session_stats("session_123")
```

### 4. Error Handling

```python
from error_handling_retry import exponential_backoff_retry

@exponential_backoff_retry(max_retries=3)
def my_function():
    # Your code here
    pass
```

### 5. Complete Production Example

```bash
python examples/complete_integration_example.py
```

---

## Comparison Matrix

| Feature | Method 1 | Method 2 | File-Based | Declarative | Complete |
|---------|----------|----------|------------|-------------|----------|
| **Tool Result Handling** | User msg | Content block | Either | Either | Either |
| **State Management** | In-memory | In-memory | Files | Files | Hybrid |
| **Persistence** | ❌ | ❌ | JSONL | ❌ | SQLite+JSONL |
| **Error Handling** | Basic | Basic | Basic | Basic | Advanced |
| **Retry Logic** | Manual | Manual | Manual | Manual | Automatic |
| **Circuit Breaker** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **YAML Config** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Resumable** | ❌ | ❌ | ✅ | Partial | ✅ |
| **Auditable** | ❌ | ❌ | ✅ | Partial | ✅ |
| **Production Ready** | ⚡ | ⚡⚡ | ⚡⚡ | ⚡⚡⚡ | ⚡⚡⚡⚡ |

Legend:
- ⚡ = Basic
- ⚡⚡ = Good
- ⚡⚡⚡ = Very Good
- ⚡⚡⚡⚡ = Excellent

---

## Recommendations

### For Prototyping
→ Use **Method 1** or **Method 2**
Simple, quick to test

### For Small Scripts
→ Use **File-Based Architecture**
Good balance of simplicity and debuggability

### For Team Collaboration
→ Use **Declarative Workflows**
YAML is easy to share and version control

### For Production Deployments
→ Use **Complete Integration**
All error handling, persistence, and observability

---

## Architecture Decision Tree

```
Start
  │
  ├─ Need to share with non-technical users?
  │    └─ YES → Declarative Workflows
  │
  ├─ Need audit trail / compliance?
  │    └─ YES → Hybrid Message Persistence
  │
  ├─ Dealing with unreliable APIs?
  │    └─ YES → Error Handling + Retry
  │
  ├─ Production deployment?
  │    └─ YES → Complete Integration
  │
  └─ Simple one-off script?
       └─ YES → Method 1 or File-Based
```

---

## Future Enhancements

Potential additions:
- [ ] Distributed execution (Celery, Ray)
- [ ] Streaming support
- [ ] Webhook integrations
- [ ] Metrics and monitoring (Prometheus)
- [ ] Web UI for workflow management
- [ ] Workflow scheduling (cron, triggers)
- [ ] Multi-agent orchestration
- [ ] Version control integration (git hooks)

---

## Contributing

These are innovative patterns! If you develop new approaches:

1. Document the pattern
2. Provide working code
3. Include examples
4. Add to comparison matrix
5. Share with the community

---

## License

MIT License - Use freely, modify, share

---

## Questions?

- Check the code comments (heavily documented)
- Run the examples to see them in action
- Experiment and adapt to your needs

**Remember**: These are templates and patterns. Adapt them to your specific requirements!
