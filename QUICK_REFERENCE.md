# MV Orchestra v2.8 - Quick Reference

**Last Updated:** 2025-11-15

---

## TL;DR

```bash
# Default (mock mode - free, no AI)
python3 run_all_phases.py my_session --audio song.mp3

# Real AI (Claude Code mode - no cost, uses subscription)
python3 run_all_phases.py my_session --mode claudecode --audio song.mp3
# Then process evaluations in Claude Code (see guide)
```

---

## Modes

| Mode | Command | Cost | Use When |
|------|---------|------|----------|
| **Mock** | `--mode mock` (default) | $0 | Development, testing, learning |
| **Claude Code** | `--mode claudecode` | $0 | Production with Claude Code |
| **Interactive** | `--mode interactive` | $0 | Manual evaluation outside Claude Code |

---

## File Locations

### Input
- Audio: `shared-workspace/input/*.mp3`
- Lyrics: `shared-workspace/input/lyrics.txt`
- Analysis: `shared-workspace/input/analysis.json`

### Output
- Session: `shared-workspace/sessions/{session_id}/`
- Results: `shared-workspace/sessions/{session_id}/phase*/`
- Evaluations: `shared-workspace/sessions/{session_id}/evaluations/`

### Claude Code Mode
- Prompts: `shared-workspace/sessions/{session_id}/evaluations/prompts/`
- Results: `shared-workspace/sessions/{session_id}/evaluations/results/`

---

## Common Commands

### Basic Usage
```bash
# Run with sample data
python3 run_all_phases.py my_session

# Use your own audio
python3 run_all_phases.py my_session --audio song.mp3 --lyrics lyrics.txt

# Rebuild analysis from audio
python3 run_all_phases.py my_session --rebuild-analysis --audio song.mp3
```

### Validation
```bash
# Enable validation
python3 run_all_phases.py my_session --validate

# Disable validation
python3 run_all_phases.py my_session --no-validate
```

### Evaluation Modes
```bash
# Mock mode (default)
python3 run_all_phases.py my_session

# Claude Code mode
python3 run_all_phases.py my_session --mode claudecode

# Interactive mode
python3 run_all_phases.py my_session --mode interactive
```

### Helper Scripts
```bash
# Check evaluation status
python3 tools/process_evaluation.py my_session

# Show next pending evaluation
python3 tools/process_evaluation.py my_session --next

# Validate all results
python3 tools/process_evaluation.py my_session --validate
```

---

## Claude Code Workflow

### 1. Start Pipeline
```bash
python3 run_all_phases.py my_session --mode claudecode --audio song.mp3
```

### 2. Process Evaluations
When you see:
```
======================================================================
CLAUDE CODE EVALUATION REQUIRED
======================================================================
Prompt exported to: [path/to/prompt.txt]
...
Save result to: [path/to/result.json]
======================================================================
```

Ask Claude Code:
```
Please read the evaluation prompt at:
[path/to/prompt.txt]

Evaluate the proposal and save the result to:
[path/to/result.json]
```

### 3. Re-run Pipeline
```bash
# Same command as step 1
python3 run_all_phases.py my_session --mode claudecode --audio song.mp3
```

Now it finds the result and uses it!

---

## Phase Overview

| Phase | Focus | Output |
|-------|-------|--------|
| **0** | Overall Design | Concept, theme, style |
| **1** | Character Design | Characters and consistency |
| **2** | Section Direction | Per-section creative direction |
| **3** | Clip Division | Shot-by-shot breakdown |
| **4** | Generation Strategy | Technical parameters |
| **5** | Claude Review | Final quality control (optional) |

---

## Directors

| Director | Type | Focus |
|----------|------|-------|
| 田中健一 | Corporate | Safe, commercial |
| 佐藤美咲 | Freelancer | Innovative, risky |
| 鈴木太郎 | Veteran | Experienced, balanced |
| 高橋愛 | Award Winner | Artistic, boundary-pushing |
| 山田花子 | Newcomer | Fresh, experimental |

---

## Troubleshooting

### "No analysis.json found"
```bash
# Rebuild from audio
python3 run_all_phases.py my_session --rebuild-analysis --audio song.mp3
```

### "No result file found" (Claude Code mode)
1. Check the expected path in output
2. Create result file at that path
3. Validate with: `python3 -m json.tool result.json`
4. Re-run pipeline

### "Invalid JSON"
```bash
# Validate
python3 -m json.tool result.json

# Use helper
python3 tools/process_evaluation.py my_session --validate
```

### Pipeline uses mock despite claudecode mode
- Result file must exist BEFORE pipeline runs
- Check file name matches expected format exactly
- Verify file is in correct directory

---

## Documentation

| File | Purpose |
|------|---------|
| **README.md** | Overview and features |
| **QUICKSTART.md** | Getting started |
| **CLAUDE_CODE_GUIDE.md** | Complete Claude Code workflow |
| **CLAUDE_CODE_REDESIGN.md** | Redesign details and rationale |
| **INSTALL.md** | Installation guide |
| **tools/README.md** | Tools documentation |

---

## Key Differences from Old Version

| Aspect | v2.8 (New) | v2.7 (Old) |
|--------|-----------|-----------|
| **Real AI** | Claude Code Task tool | Anthropic API |
| **Setup** | None needed | API key + pip install |
| **Cost** | $0 | $0.50-2.00 per session |
| **Dependencies** | Standard library only | `anthropic` package |
| **Command** | `--mode claudecode` | `--real-mode` |
| **Workflow** | File-based exchange | Automatic API calls |

---

## Quick Examples

### Example 1: Quick Test
```bash
# 30 seconds to results
python3 run_all_phases.py test_session
```

### Example 2: Your Own Song
```bash
# With your MP3
python3 run_all_phases.py my_song --audio my_song.mp3 --lyrics lyrics.txt
```

### Example 3: Production Run
```bash
# Real AI evaluations
python3 run_all_phases.py production --mode claudecode --audio song.mp3
# Process evaluations in Claude Code
```

---

## Tips

1. **Start with mock mode** to understand the system
2. **Use validation** to catch errors early
3. **Check helper scripts** for status and next steps
4. **Read prompts** before processing to understand context
5. **Save results** in git for reproducibility

---

For complete documentation, see:
- `CLAUDE_CODE_GUIDE.md` - Full workflow guide
- `README.md` - Complete feature list
- `QUICKSTART.md` - Detailed getting started

---

**Version:** 2.8
**Last Updated:** 2025-11-15
