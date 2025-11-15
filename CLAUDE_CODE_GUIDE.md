# Claude Code Integration Guide

**MV Orchestra v2.8 - Real AI Evaluation Workflow**

**Last Updated:** 2025-11-15
**Version:** 2.8

---

## Overview

MV Orchestra v2.8 is designed to work **inside Claude Code** using the built-in **Task tool**, NOT with the Anthropic API directly.

This approach:
- Uses your Claude Code subscription (no additional API costs)
- Provides better integration with your development workflow
- Allows Claude to understand full project context
- No need for API key management

---

## Architecture

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User runs MV Orchestra pipeline in Claude Code          │
│    python3 run_all_phases.py my_session --mode claudecode  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Python exports evaluation prompts to files              │
│    shared-workspace/sessions/{session}/evaluations/prompts/ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Claude Code (you) reads prompt files                    │
│    Uses context from the entire project                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Claude Code runs evaluation via Task tool               │
│    Task-based agent evaluates the proposal                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Result saved to file                                    │
│    shared-workspace/sessions/{session}/evaluations/results/ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. Python imports result and continues pipeline            │
│    Evaluation integrated into competition flow              │
└─────────────────────────────────────────────────────────────┘
```

---

## Usage Modes

### Mode 1: Mock (Default)

No AI, simulated evaluations only.

```bash
python3 run_all_phases.py my_session --mode mock
# OR
python3 run_all_phases.py my_session  # mock is default
```

**Use when:**
- Testing the pipeline
- Developing new features
- Don't need real AI feedback

### Mode 2: Claude Code (Recommended)

Exports prompts for Claude Code Task tool processing.

```bash
python3 run_all_phases.py my_session --mode claudecode
```

**Use when:**
- Running inside Claude Code
- Want real AI evaluations
- Using Claude Code subscription (no extra cost)

**Workflow:**
1. Pipeline exports prompts to files
2. You read the prompts
3. You run evaluations via Task tool
4. You save results to files
5. Pipeline continues automatically

### Mode 3: Interactive

Pauses and prompts you to paste evaluation results.

```bash
python3 run_all_phases.py my_session --mode interactive
```

**Use when:**
- Running outside Claude Code
- Want to manually copy/paste evaluations
- Quick one-off testing

---

## Step-by-Step Workflow

### Running a Full Pipeline with Claude Code

#### Step 1: Start the Pipeline

```bash
python3 run_all_phases.py my_session --mode claudecode --audio song.mp3
```

The pipeline will:
- Process audio and lyrics
- Generate proposals for Phase 0
- Export evaluation prompt to file
- Wait for result file

#### Step 2: Read Evaluation Prompt

The pipeline outputs:
```
======================================================================
CLAUDE CODE EVALUATION REQUIRED
======================================================================
Prompt exported to: shared-workspace/sessions/my_session/evaluations/prompts/phase0_freelancer_overall_design_prompt.txt

To run this evaluation in Claude Code:
1. Read the prompt file: [path]
2. Run the evaluation (see CLAUDE_CODE_GUIDE.md)
3. Save result to: [path]
======================================================================
```

Read the prompt file:
```bash
cat shared-workspace/sessions/my_session/evaluations/prompts/phase0_freelancer_overall_design_prompt.txt
```

#### Step 3: Run Evaluation in Claude Code

**Option A: Ask Claude Code to run it**

```
Please read the evaluation prompt at:
shared-workspace/sessions/my_session/evaluations/prompts/phase0_freelancer_overall_design_prompt.txt

Then evaluate the proposal and save the result to:
shared-workspace/sessions/my_session/evaluations/results/phase0_freelancer_overall_design_result.json
```

**Option B: Use Task tool directly**

If Claude Code exposes Task tool in Python:
```python
from claude_code import Task

# Read prompt
with open('path/to/prompt.txt') as f:
    prompt = f.read()

# Run evaluation
result = Task(
    description="Evaluate MV Orchestra Phase 0 proposal as Freelancer director",
    prompt=prompt
)

# Save result
with open('path/to/result.json', 'w') as f:
    f.write(result)
```

#### Step 4: Pipeline Continues

Once the result file exists, the pipeline:
- Detects the result file
- Parses the evaluation
- Continues to next phase
- Repeats for each director/phase

---

## File Structure

### Prompt Files

Location: `shared-workspace/sessions/{session_id}/evaluations/prompts/`

Format: `phase{N}_{director}_{type}_prompt.txt`

Example:
```
phase0_freelancer_overall_design_prompt.txt
phase0_corporate_overall_design_prompt.txt
phase1_veteran_character_design_prompt.txt
```

Content:
```
[Full evaluation template for this director]
[Evaluation criteria and scoring guidelines]
[Director-specific guidance]

======================================================================
## EVALUATION TASK

**Phase**: 0
**Evaluation Type**: overall_design

### Proposals to Evaluate

```json
{
  "concept_theme": "Urban romance in neon city",
  "visual_style": "Cyberpunk meets romantic drama",
  ...
}
```

### Your Task

Please evaluate the proposal(s) above using your evaluation criteria.
Return your response in the JSON format specified in the template above.
...
```

### Result Files

Location: `shared-workspace/sessions/{session_id}/evaluations/results/`

Format: `phase{N}_{director}_{type}_result.json`

Example:
```
phase0_freelancer_overall_design_result.json
```

Content (expected format):
```json
{
  "scores": {
    "emotional_authenticity": {
      "score": 7,
      "weight": 0.30,
      "weighted_score": 2.1,
      "rationale": "Strong emotional core but..."
    },
    "artistic_distinctiveness": {
      "score": 6,
      "weight": 0.25,
      "weighted_score": 1.5,
      "rationale": "Decent vision, lacks uniqueness"
    },
    ...
  },
  "total_score": 6.5,
  "recommendation": "NEEDS REVISION",
  "summary": "This proposal shows promise but...",
  "what_works": [
    "Emotional authenticity is present",
    "Production planning is realistic"
  ],
  "what_needs_work": [
    "Visual style lacks distinctiveness",
    "Budget seems optimistic"
  ],
  "honest_feedback": [
    "This feels safe and corporate",
    "Missing the raw edge this song deserves"
  ]
}
```

---

## Helper Scripts

### Script 1: Batch Process All Prompts

Create `tools/batch_evaluate.py`:

```python
#!/usr/bin/env python3
"""
Batch process all evaluation prompts in a session.
"""

import sys
from pathlib import Path

def main(session_id):
    prompts_dir = Path(f"shared-workspace/sessions/{session_id}/evaluations/prompts")

    if not prompts_dir.exists():
        print(f"No prompts found for session: {session_id}")
        return

    prompt_files = list(prompts_dir.glob("*.txt"))

    print(f"Found {len(prompt_files)} prompts to process:")
    for i, prompt_file in enumerate(prompt_files, 1):
        print(f"\n{i}. {prompt_file.name}")
        print(f"   Read: {prompt_file}")

        result_file = prompt_file.parent.parent / "results" / prompt_file.name.replace("_prompt.txt", "_result.json")

        if result_file.exists():
            print(f"   ✓ Result exists: {result_file}")
        else:
            print(f"   ⚠ Need result: {result_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 batch_evaluate.py <session_id>")
        sys.exit(1)

    main(sys.argv[1])
```

### Script 2: Validate Result Format

Create `tools/validate_result.py`:

```python
#!/usr/bin/env python3
"""
Validate that a result JSON file has the correct format.
"""

import json
import sys
from pathlib import Path

REQUIRED_FIELDS = [
    'total_score',
    'recommendation',
    'summary',
    'what_works',
    'what_needs_work'
]

def validate_result(result_file):
    """Validate result file format."""
    try:
        with open(result_file) as f:
            data = json.load(f)

        # Check required fields
        missing = [f for f in REQUIRED_FIELDS if f not in data]
        if missing:
            print(f"✗ Missing fields: {', '.join(missing)}")
            return False

        # Check score range
        if not (0 <= data['total_score'] <= 10):
            print(f"✗ total_score must be 0-10, got: {data['total_score']}")
            return False

        # Check recommendation
        valid_recs = ['APPROVE', 'NEEDS REVISION', 'REJECT']
        if data['recommendation'] not in valid_recs:
            print(f"✗ recommendation must be one of {valid_recs}, got: {data['recommendation']}")
            return False

        print(f"✓ Result file is valid")
        print(f"  Score: {data['total_score']}/10")
        print(f"  Recommendation: {data['recommendation']}")
        return True

    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 validate_result.py <result_file.json>")
        sys.exit(1)

    success = validate_result(sys.argv[1])
    sys.exit(0 if success else 1)
```

---

## Example: Complete Evaluation Flow

### 1. Start Pipeline

```bash
$ python3 run_all_phases.py demo_session --mode claudecode
```

### 2. Pipeline Outputs

```
======================================================================
MV ORCHESTRA v2.8 - PIPELINE START
======================================================================
Session ID: demo_session
Analysis: shared-workspace/input/analysis.json
Evaluation Mode: claudecode
⚠ Claude Code mode: Evaluations will be exported for manual processing
Validation: True
======================================================================

======================================================================
Phase 0: Overall Design
======================================================================

[Phase 0 generates 5 proposals]

======================================================================
CLAUDE CODE EVALUATION REQUIRED
======================================================================
Prompt exported to: shared-workspace/sessions/demo_session/evaluations/prompts/phase0_freelancer_overall_design_prompt.txt

To run this evaluation in Claude Code:
1. Read the prompt file: [path]
2. Run the evaluation (see CLAUDE_CODE_GUIDE.md)
3. Save result to: shared-workspace/sessions/demo_session/evaluations/results/phase0_freelancer_overall_design_result.json
======================================================================

⚠ No result file found, using mock evaluation
  To use real evaluation, create: [path]
```

### 3. You (in Claude Code) Process Evaluation

```
Hi Claude, please help me run this evaluation.

Read the prompt at:
shared-workspace/sessions/demo_session/evaluations/prompts/phase0_freelancer_overall_design_prompt.txt

Evaluate the proposal as described and save your response to:
shared-workspace/sessions/demo_session/evaluations/results/phase0_freelancer_overall_design_result.json
```

### 4. Claude Code Responds

Claude reads the prompt, processes it, and writes the result file with proper JSON format.

### 5. Re-run Pipeline

```bash
$ python3 run_all_phases.py demo_session --mode claudecode
```

Now it finds the result file and uses it!

---

## Advantages of Claude Code Integration

### 1. **No API Costs**
- Uses your Claude Code subscription
- No per-request charges
- Unlimited evaluations (within subscription limits)

### 2. **Better Context**
- Claude sees your entire project
- Can reference other files
- Understands project structure

### 3. **Interactive Refinement**
- Ask Claude to revise evaluations
- Discuss proposals before evaluating
- Iterative improvement

### 4. **Version Control Integration**
- All prompts and results are files
- Can track changes in git
- Reproducible evaluations

### 5. **Flexibility**
- Process evaluations in any order
- Batch process multiple evaluations
- Custom processing scripts

---

## Troubleshooting

### "No result file found"

**Problem:** Pipeline can't find evaluation result.

**Solution:**
1. Check the expected path in the output
2. Ensure result file exists at that exact path
3. Verify JSON format with `validate_result.py`
4. Check file permissions

### "Invalid JSON in result file"

**Problem:** Result file doesn't parse correctly.

**Solution:**
1. Validate with: `python3 -m json.tool result.json`
2. Check for missing commas, quotes, braces
3. Use `validate_result.py` to check format
4. Ensure all required fields present

### "Pipeline continues but uses mock"

**Problem:** Result exists but pipeline doesn't use it.

**Solution:**
1. Ensure result file name matches expected format
2. Check that result was created BEFORE pipeline ran
3. Verify result file contains valid JSON
4. Check file is in correct directory

### "Claude Code can't access files"

**Problem:** Claude Code says it can't read/write files.

**Solution:**
1. Ensure you're running IN Claude Code (not just asking Claude)
2. Use absolute paths
3. Check file permissions
4. Verify directories exist

---

## Migration from API Mode

If you were using the old Anthropic API mode:

### Old Way (DEPRECATED)
```bash
export ANTHROPIC_API_KEY="your-key"
pip install anthropic
python3 run_all_phases.py my_session --real-mode
```

### New Way (RECOMMENDED)
```bash
# No API key needed!
# No pip install needed!
python3 run_all_phases.py my_session --mode claudecode
# Then process evaluations in Claude Code as described above
```

### Benefits
- No API costs
- No key management
- Better integration
- Full project context

---

## Advanced Usage

### Pre-generate All Prompts

```bash
# Run pipeline in claudecode mode, let it generate all prompts
python3 run_all_phases.py my_session --mode claudecode

# Pipeline will export prompts but use mock evaluations
# Now you have all prompts ready to process
```

### Batch Process Later

```bash
# List all prompts
ls shared-workspace/sessions/my_session/evaluations/prompts/

# Process them one by one in Claude Code
# Or create a batch script to handle them all
```

### Hybrid Mode

```bash
# Use claudecode for Phase 0 only
# Use mock for other phases
# Manually run pipeline phase by phase
python3 -c "from phase0 import run_phase0; run_phase0('my_session', mode='claudecode')"
```

---

## Best Practices

### 1. **Use Mock Mode for Development**
- Test pipeline with mock mode first
- Verify all phases work
- Check output structure
- Then switch to claudecode mode

### 2. **Organize Result Files**
- Keep prompts and results in git
- Use clear commit messages
- Track which evaluations are real vs mock
- Document evaluation decisions

### 3. **Validate Results**
- Always validate JSON before saving
- Use `validate_result.py` script
- Check score ranges (0-10)
- Verify all required fields

### 4. **Batch Processing**
- Generate all prompts first
- Process similar evaluations together
- Use helper scripts for automation
- Keep track of progress

### 5. **Documentation**
- Document why you made specific evaluation decisions
- Save discussion notes with results
- Track iterations and refinements
- Share knowledge with team

---

## FAQ

### Q: Can I still use the Anthropic API?

A: The API integration was removed in favor of Claude Code integration. If you need API-based evaluation, use an older version or modify `codex_runner.py` yourself.

### Q: How do I run this without Claude Code?

A: Use `--mode interactive` to manually paste evaluations, or stick with `--mode mock` for simulated evaluations.

### Q: Can I automate the Claude Code evaluations?

A: Not directly from Python. Claude Code's Task tool is meant to be used by Claude (the AI assistant) when helping you, not called programmatically.

### Q: What if I want to use a different AI model?

A: You can modify the workflow to use any AI. Read prompts from files, process them however you want, save results in the expected JSON format.

### Q: Is mock mode good enough for production?

A: Mock mode is for testing only. For production, use claudecode or interactive mode with real AI evaluations.

---

## Summary

**MV Orchestra v2.8 is designed for Claude Code:**

1. Run pipeline with `--mode claudecode`
2. Prompts exported to files
3. Process evaluations in Claude Code
4. Results saved to files
5. Pipeline continues automatically

**No API costs. No key management. Better integration.**

For questions or issues, see:
- `README.md` - General documentation
- `QUICKSTART.md` - Quick start guide
- `CLAUDE.md` - Project guidelines

---

**Last Updated:** 2025-11-15
**MV Orchestra v2.8**
