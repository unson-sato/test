# Phase 4 & Phase 5 Quick Start Guide

## Installation

No additional installation needed for Phase 4 and mock Phase 5.

For Phase 5 real mode only:
```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Quick Usage

### Basic: Run Phase 4 Only
```python
from phase4 import run_phase4

# Run Phase 4 for your session
results = run_phase4(session_id="your_session_id", mock_mode=True)

# Get the winning strategy
winner = results['winner']
print(f"Winner: {winner['director']}")

# Access strategies
strategies = winner['proposal']['generation_strategies']
for s in strategies:
    print(f"{s['clip_id']}: {s['generation_mode']}")
```

### With Phase 5 Skip (Fastest)
```python
from phase4 import run_phase4
from phase5 import run_phase5

# Phase 4
phase4_results = run_phase4(session_id, mock_mode=True)

# Phase 5 (skip)
phase5_results = run_phase5(session_id, mode="skip")

# Use Phase 4 winner directly
final_strategy = phase4_results['winner']['proposal']
```

### With Phase 5 Mock (Development)
```python
from phase4 import run_phase4
from phase5 import run_phase5

# Phase 4
phase4_results = run_phase4(session_id, mock_mode=True)

# Phase 5 (mock review)
phase5_results = run_phase5(session_id, mode="mock")

# Use reviewed strategy
final_strategy = phase5_results['final_strategy']
print(f"Average review score: {phase5_results['summary']['average_score']}/10")
print(f"Adjustments made: {len(phase5_results['adjustments'])}")
```

### With Phase 5 Real (Production)
```python
from phase4 import run_phase4
from phase5 import run_phase5

# Phase 4
phase4_results = run_phase4(session_id, mock_mode=True)

# Phase 5 (real Claude API)
phase5_results = run_phase5(
    session_id,
    mode="real",
    max_clips=20,  # Limit for cost control
    adjustment_threshold=6.5
)

# Check cost
print(f"Cost: ${phase5_results['summary']['actual_cost_usd']}")

# Use reviewed strategy
final_strategy = phase5_results['final_strategy']
```

## Complete Example

```python
#!/usr/bin/env python3
"""Complete Phase 4 + Phase 5 example"""

from core import SharedState
from phase4 import run_phase4
from phase5 import run_phase5

# Assume you have a session with Phase 0-3 completed
session_id = "your_session_id"

# Run Phase 4: Generation Strategy
print("Running Phase 4...")
phase4_results = run_phase4(session_id, mock_mode=True)

print(f"\nPhase 4 Results:")
print(f"  Winner: {phase4_results['winner']['director']}")
print(f"  Score: {phase4_results['winner']['total_score']:.1f}/100")
print(f"  Strategies: {len(phase4_results['winner']['proposal']['generation_strategies'])}")

# Run Phase 5: Optional Review (choose mode)
MODE = "mock"  # or "skip" or "real"

print(f"\nRunning Phase 5 ({MODE} mode)...")
phase5_results = run_phase5(session_id, mode=MODE)

if phase5_results.get('skipped'):
    print("  Phase 5 skipped")
    final_strategy = phase4_results['winner']['proposal']
else:
    print(f"  Reviews: {len(phase5_results['reviews'])}")
    print(f"  Avg Score: {phase5_results['summary']['average_score']:.1f}/10")
    print(f"  Adjustments: {len(phase5_results['adjustments'])}")
    final_strategy = phase5_results['final_strategy']

# Use final strategy
print(f"\nFinal Strategy:")
print(f"  Total clips: {len(final_strategy['generation_strategies'])}")

# Show first clip strategy
first_clip = final_strategy['generation_strategies'][0]
print(f"\n  Example (Clip {first_clip['clip_id']}):")
print(f"    Mode: {first_clip['generation_mode']}")
print(f"    Type: {first_clip['clip_type']}")
print(f"    Prompt: {first_clip['prompt_template']['full_prompt'][:80]}...")
print(f"    Cost: {first_clip['estimated_cost']}")
```

## Common Patterns

### Pattern 1: Budget-Conscious (Skip Phase 5)
```python
results = run_phase4(session_id, mock_mode=True)
run_phase5(session_id, mode="skip")
strategy = results['winner']['proposal']
```

### Pattern 2: Development/Testing (Mock Everything)
```python
phase4 = run_phase4(session_id, mock_mode=True)
phase5 = run_phase5(session_id, mode="mock")
strategy = phase5['final_strategy']
```

### Pattern 3: Production with Review (Real API)
```python
phase4 = run_phase4(session_id, mock_mode=True)
phase5 = run_phase5(session_id, mode="real", max_clips=50)
strategy = phase5['final_strategy']
```

## Cost Management

### Estimate Before Running
```python
from phase5 import ClaudeAPIClient

client = ClaudeAPIClient(mock_mode=False)
estimate = client.estimate_cost(num_clips=50)
print(f"Estimated cost: ${estimate['estimated_total_cost_usd']}")

if estimate['estimated_total_cost_usd'] < 5.0:
    # Proceed with real review
    run_phase5(session_id, mode="real")
else:
    # Use mock instead
    run_phase5(session_id, mode="mock")
```

### Limit Clips Reviewed
```python
# Review only first 20 clips to control cost
phase5 = run_phase5(session_id, mode="real", max_clips=20)
```

## Testing

### Run Phase 4 Tests
```bash
python phase4/test_phase4.py
```

### Run Phase 5 Tests
```bash
python phase5/test_phase5.py
```

### Run Both
```bash
python phase4/test_phase4.py && python phase5/test_phase5.py
```

## Troubleshooting

### Issue: "No Phase 4 data found"
**Solution**: Ensure Phase 0-3 are completed first
```python
session = SharedState.load_session(session_id)
print(session.get_session_summary())  # Check phase status
```

### Issue: "anthropic module not found"
**Solution**: Only needed for Phase 5 real mode
```bash
pip install anthropic
```
Or use mock/skip mode instead.

### Issue: "ANTHROPIC_API_KEY not found"
**Solution**: Set environment variable
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```
Or use mock/skip mode.

### Issue: High API costs
**Solutions**:
1. Use `max_clips` parameter
2. Use mock mode for development
3. Skip Phase 5 entirely
4. Increase `adjustment_threshold` to reduce adjustments

## Advanced Usage

### Custom Prompt Building
```python
from phase4 import PromptBuilder

prompt = (PromptBuilder()
    .set_base("A futuristic cityscape")
    .add_style("cyberpunk aesthetic", "neon colors")
    .add_technical("wide angle lens", "8K resolution")
    .add_quality("photorealistic", "highly detailed")
    .set_negative("blur, distortion, low quality")
    .build())

print(prompt.build())  # Full prompt string
```

### Asset Management
```python
from phase4 import AssetManager, AssetType

manager = AssetManager(session_id)

# Create asset
asset = manager.create_asset(
    asset_type=AssetType.CHARACTER_REFERENCE,
    description="Main character reference",
    source="Phase 1 design"
)

# Add to clip
manager.add_clip_asset("clip_001", asset, required=True)

# Get summary
summary = manager.get_asset_summary()
print(summary)
```

### Direct API Client Usage
```python
from phase5 import ClaudeAPIClient

client = ClaudeAPIClient(mock_mode=True)

review = client.review_generation_strategy(
    clip_id="clip_001",
    generation_mode="veo2",
    prompt="A young woman in modern streetwear...",
    clip_context={'clip_type': 'performance', 'duration': 3.0}
)

print(f"Score: {review['claude_score']}/10")
print(f"Feedback: {review['claude_feedback']}")
```

## Next Steps

After Phase 4 & 5:
1. Use final strategy for actual video generation
2. Track asset requirements
3. Implement generation API calls
4. Monitor costs and quality
5. Iterate based on results

## References

- Full documentation: `phase4/README.md` and `phase5/README.md`
- Implementation report: `PHASE4_PHASE5_IMPLEMENTATION_REPORT.md`
- Example usage: `example_usage.py`

---

**Quick Reference Version**: 1.0
**Last Updated**: 2025-11-14
