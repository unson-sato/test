# Quick Start: Real AI Integration

## 3-Step Setup

### 1. Install Package
```bash
pip install anthropic
```

### 2. Set API Key
```bash
export ANTHROPIC_API_KEY="your-key-from-console.anthropic.com"
```

### 3. Test It
```bash
python3 test_real_ai.py
```

---

## Usage

### Test Single Evaluation (~$0.02)
```bash
python3 test_real_ai.py
```

### Test All 5 Directors (~$0.10)
```bash
python3 test_real_ai.py --all
```

### Run Full Pipeline (~$1.00)
```bash
python3 run_all_phases.py my_project --real-mode
```

---

## Troubleshooting

**Error: "ANTHROPIC_API_KEY not set"**
```bash
export ANTHROPIC_API_KEY="your-key"
```

**Error: "anthropic package not installed"**
```bash
pip install anthropic
```

**API call fails**
- Check key at https://console.anthropic.com/
- Verify billing is set up
- System auto-falls back to mock mode

---

## What Gets Called

When you run real mode:
1. Loads director prompt: `.claude/prompts_v2/evaluation_[director].md`
2. Formats with your proposal data
3. Calls Claude Sonnet 4.5 API
4. Parses JSON response
5. Returns score (0-100), feedback, suggestions, highlights, concerns

---

## Cost Control

- **Default**: Mock mode (FREE)
- **Test script**: Ask before API calls
- **Pipeline**: Use `--real-mode` flag explicitly
- **Monitor**: Check console.anthropic.com

---

## Files You Need

All already present:
- ✅ `/home/user/test/core/codex_runner.py` - Real AI implementation
- ✅ `/home/user/test/test_real_ai.py` - Test script
- ✅ `/home/user/test/.claude/prompts_v2/evaluation_*.md` - 5 director prompts

---

## Example Output

```
======================================================================
EVALUATION RESULTS
======================================================================

Director: freelancer
Score: 65.0/100

Feedback:
----------------------------------------------------------------------
This is competent but lacks soul. It's too safe, too polished...

Suggestions:
----------------------------------------------------------------------
1. Emotional authenticity is severely lacking
2. No distinctive artistic voice - feels generic
3. Too many safe choices, no creative courage

Highlights:
----------------------------------------------------------------------
1. Production planning is realistic and solid
2. Technical execution will be professional
```

---

For complete documentation, see:
- `/home/user/test/README.md` - Full usage guide
- `/home/user/test/REAL_AI_IMPLEMENTATION.md` - Implementation details
