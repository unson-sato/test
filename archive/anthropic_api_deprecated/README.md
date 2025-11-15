# Deprecated: Anthropic API Integration

**Date Deprecated:** 2025-11-15
**Reason:** Replaced with Claude Code Task-based integration

---

## What Changed

MV Orchestra v2.8 was redesigned to use Claude Code's built-in Task tool instead of the Anthropic API directly.

### Old Approach (Deprecated)
- Used `anthropic` Python package
- Required API key management
- Costs money per API call
- Direct API integration

### New Approach (Current)
- Uses Claude Code's Task tool
- No API key needed
- Uses Claude Code subscription (no extra cost)
- Better project integration

---

## Files in This Archive

### `test_real_ai.py`
Test script for the old Anthropic API integration. This tested direct API calls with `anthropic` package.

**No longer maintained.**

### `REAL_AI_IMPLEMENTATION.md`
Documentation for the Anthropic API implementation. Describes how the `_real_evaluation()` method worked with the API.

**Replaced by:** `CLAUDE_CODE_GUIDE.md` (in project root)

### `QUICK_START_REAL_AI.md`
Quick start guide for setting up Anthropic API keys and running real evaluations.

**Replaced by:** `CLAUDE_CODE_GUIDE.md` (in project root)

---

## Migration Guide

If you were using the old API-based approach:

### Before (Deprecated)
```bash
# Install package
pip install anthropic

# Set API key
export ANTHROPIC_API_KEY="your-key"

# Run with real AI
python3 run_all_phases.py my_session --real-mode
```

### After (Current)
```bash
# No installation needed
# No API key needed

# Run in Claude Code mode
python3 run_all_phases.py my_session --mode claudecode

# Process evaluations in Claude Code (see CLAUDE_CODE_GUIDE.md)
```

---

## Why the Change?

### Problems with API Approach
1. **Cost:** Every evaluation costs money
2. **Key Management:** Users need to acquire and manage API keys
3. **Limited Context:** API calls don't see full project
4. **Dependencies:** Required external package

### Benefits of Claude Code Approach
1. **No Cost:** Uses Claude Code subscription
2. **No Setup:** No keys, no packages
3. **Full Context:** Claude sees entire project
4. **Better Integration:** Works naturally with development workflow

---

## For Historical Reference

These files are kept for:
- Understanding the evolution of the system
- Reference for anyone who needs API-based integration
- Comparison of different approaches

If you need to implement API-based evaluation again, these files show how it was done.

---

## Current Documentation

See these files in the project root:
- `CLAUDE_CODE_GUIDE.md` - Complete workflow guide
- `README.md` - Updated with Claude Code approach
- `QUICKSTART.md` - Quick start guide

---

**Last Updated:** 2025-11-15
**MV Orchestra v2.8**
