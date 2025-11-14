# Phase 5: Real Claude Review (Optional)

## Overview

Phase 5 is an **optional** quality control phase that uses the real Claude API to review generation mode selections and prompt strategies from Phase 4. This provides an independent evaluation and can suggest improvements before actual video generation begins.

## Key Features

- **Optional Execution**: Can be skipped entirely or run in mock mode
- **Real API Integration**: Uses actual Claude API when enabled
- **Cost Estimation**: Estimates API costs before execution
- **Intelligent Adjustments**: Suggests alternative modes when appropriate
- **Flexible Modes**: Supports mock, real, and skip modes

## Execution Modes

### Skip Mode (Default)
```python
run_phase5(session_id, mode="skip")
```
- Completely skips Phase 5
- No API calls, no cost
- Fastest option
- Use when: Budget is tight or confidence in Phase 4 is high

### Mock Mode
```python
run_phase5(session_id, mode="mock")
```
- Simulates Claude review without API calls
- No cost
- Good for development and testing
- Use when: Testing the pipeline or developing locally

### Real Mode
```python
run_phase5(session_id, mode="real")
```
- Uses actual Claude API (claude-sonnet-4-5-20250929)
- Costs money (estimated $0.50-$5 per session depending on clip count)
- Provides genuine AI review
- Use when: Production deployment and quality is critical

## What Claude Reviews

For each clip, Claude evaluates:

1. **Generation Mode Appropriateness**: Is the selected mode (Veo2, Sora, etc.) optimal for this clip?
2. **Prompt Quality**: Is the prompt well-structured and likely to produce good results?
3. **Potential Issues**: Are there any concerns or red flags?
4. **Alternative Suggestions**: Should a different mode be considered?

## Input Data

Phase 5 requires:
- **Phase 4 winner's proposal**: The complete generation strategy to review

## Output Data

Phase 5 produces:

```json
{
  "skipped": false,
  "mode": "real",
  "review_conducted": true,
  "reviews": [
    {
      "clip_id": "clip_001",
      "original_mode": "veo2",
      "claude_feedback": "Veo2 is appropriate for this establishing shot...",
      "claude_score": 8.5,
      "suggested_alternative": null,
      "adjustment_made": false
    }
  ],
  "summary": {
    "total_clips_reviewed": 45,
    "average_score": 7.8,
    "min_score": 5.5,
    "max_score": 9.2,
    "clips_with_suggestions": 3,
    "actual_cost_usd": 2.50
  },
  "adjustments": [
    {
      "clip_id": "clip_015",
      "original_mode": "sora",
      "new_mode": "runway_gen3",
      "reason": "Consider Runway for faster iteration..."
    }
  ],
  "final_strategy": {...}
}
```

## Module Structure

### `runner.py`
Main orchestrator for Phase 5.

**Key Classes:**
- `Phase5Runner`: Main runner class

**Key Functions:**
- `run_phase5(session_id, mode, max_clips, adjustment_threshold)`: Entry point

### `api_client.py`
Wrapper for Claude API calls with mock support.

**Key Classes:**
- `ClaudeAPIClient`: API client with mock/real mode support

**Key Functions:**
- `create_client(mode)`: Create API client
- `review_generation_strategy(...)`: Review a single clip
- `batch_review(...)`: Review multiple clips
- `estimate_cost(...)`: Estimate API costs

## Usage Examples

### Skip Phase 5
```python
from phase5 import run_phase5

# Skip entirely
results = run_phase5(session_id, mode="skip")
# Results will show: {"skipped": True, ...}
```

### Mock Review (Development)
```python
from phase5 import run_phase5

# Run in mock mode for testing
results = run_phase5(session_id, mode="mock")

# Check reviews
for review in results['reviews']:
    print(f"{review['clip_id']}: {review['claude_score']}/10")
```

### Real API Review (Production)
```python
from phase5 import run_phase5

# Run with real Claude API
results = run_phase5(
    session_id=session_id,
    mode="real",
    max_clips=10,  # Limit to first 10 clips for cost control
    adjustment_threshold=6.5  # Adjust clips scoring below 6.5
)

# Check cost
print(f"Cost: ${results['summary']['actual_cost_usd']}")

# Check adjustments
if results['adjustments']:
    print(f"Made {len(results['adjustments'])} adjustments")
    for adj in results['adjustments']:
        print(f"  {adj['clip_id']}: {adj['original_mode']} → {adj['new_mode']}")
```

### Direct API Client Usage
```python
from phase5 import ClaudeAPIClient

# Create client
client = ClaudeAPIClient(mock_mode=False)

# Estimate cost before running
cost = client.estimate_cost(num_clips=45)
print(f"Estimated cost: ${cost['estimated_total_cost_usd']}")

# Review single clip
review = client.review_generation_strategy(
    clip_id="clip_001",
    generation_mode="veo2",
    prompt="A young woman standing in urban street...",
    clip_context={'clip_type': 'performance', 'duration': 3.0}
)
print(f"Score: {review['claude_score']}/10")
print(f"Feedback: {review['claude_feedback']}")
```

## Cost Management

### Pricing (as of 2025)
- **Input tokens**: $3 per million tokens
- **Output tokens**: $15 per million tokens

### Typical Costs
- **10 clips**: ~$0.20 - $0.50
- **50 clips**: ~$1.00 - $2.50
- **100 clips**: ~$2.00 - $5.00

### Cost Control Strategies

1. **Limit Clips Reviewed**
   ```python
   run_phase5(session_id, mode="real", max_clips=20)
   ```

2. **Use Mock Mode for Development**
   ```python
   run_phase5(session_id, mode="mock")
   ```

3. **Skip When Unnecessary**
   ```python
   run_phase5(session_id, mode="skip")
   ```

4. **Check Estimate First**
   ```python
   client = ClaudeAPIClient(mock_mode=False)
   estimate = client.estimate_cost(num_clips=45)
   if estimate['estimated_total_cost_usd'] < 5.0:
       # Proceed with review
       run_phase5(session_id, mode="real")
   ```

## Adjustment Logic

Phase 5 makes adjustments based on:

1. **Claude Score**: If score < threshold (default 6.5/10)
2. **Alternative Suggested**: Claude must suggest a specific alternative mode
3. **Automatic Application**: Adjustments are automatically applied to final strategy

### Adjustment Threshold

```python
# Strict (only adjust very low scores)
run_phase5(session_id, mode="real", adjustment_threshold=5.0)

# Moderate (default)
run_phase5(session_id, mode="real", adjustment_threshold=6.5)

# Aggressive (adjust anything not excellent)
run_phase5(session_id, mode="real", adjustment_threshold=8.0)
```

## API Key Setup

### Environment Variable
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Python
```python
import os
os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-...'
```

### Direct to Client
```python
client = ClaudeAPIClient(mock_mode=False, api_key="sk-ant-...")
```

## Error Handling

Phase 5 handles errors gracefully:

```python
try:
    results = run_phase5(session_id, mode="real")
except ImportError:
    print("anthropic package not installed")
    # Fall back to mock mode
    results = run_phase5(session_id, mode="mock")
except ValueError:
    print("API key not found")
    # Fall back to skip mode
    results = run_phase5(session_id, mode="skip")
```

## Testing

See `test_phase5.py` for testing examples.

```bash
# Run Phase 5 tests
python -m pytest phase5/test_phase5.py -v

# Test specific mode
python -m pytest phase5/test_phase5.py::test_mock_mode -v
```

## When to Use Phase 5

### Use Phase 5 When:
- Production deployment with budget for API calls
- Quality is critical (e.g., client projects)
- Uncertain about Phase 4 generation mode selections
- Want independent AI validation
- Have budget for API costs

### Skip Phase 5 When:
- Development/testing
- Low budget projects
- High confidence in Phase 4 results
- Rapid iteration needed
- Cost control is critical

## Integration with Pipeline

Phase 5 is designed to be seamlessly skippable:

```python
# Full pipeline with Phase 5
from phase4 import run_phase4
from phase5 import run_phase5

# Phase 4
phase4_results = run_phase4(session_id, mock_mode=True)

# Phase 5 (optional)
phase5_results = run_phase5(session_id, mode="mock")

# Use final strategy from Phase 5 if available, otherwise Phase 4
if phase5_results.get('skipped'):
    final_strategy = phase4_results['winner']['proposal']
else:
    final_strategy = phase5_results['final_strategy']
```

## Related Phases

- **Phase 4** (Generation Strategy): Provides strategies to review
- **Phase 6+** (Future): Would use the reviewed/adjusted strategies for actual generation

## Requirements

### For Mock Mode
- No additional requirements

### For Real Mode
```bash
pip install anthropic
```

Or add to requirements.txt:
```
anthropic>=0.40.0
```

## Notes

- Phase 5 is **completely optional** and can be disabled in config
- Mock mode produces deterministic but realistic results
- Real mode requires valid Anthropic API key
- Cost scales linearly with number of clips
- Reviews are independent of Phase 4 director evaluations
- Adjustments preserve all other strategy parameters

## Version

Phase 5 Module v2.8 - Part of MV Orchestra v2.8
