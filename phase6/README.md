# Phase 6: Video Generation Execution

## Overview

Phase 6 executes the actual video generation based on the strategies defined in Phase 4. This phase coordinates with external AI video generation services and manages the generation queue, asset preparation, and output collection.

## Purpose

Transform generation strategies into actual video clips by:
- Preparing prompts and assets for each clip
- Submitting generation requests to appropriate services
- Managing generation queue and monitoring progress
- Collecting and validating generated outputs
- Organizing generated clips for Phase 7 editing

## Input Requirements

Phase 6 requires:

1. **Phase 4 Output**: Generation strategies for all clips
   - Generation mode selection (Veo2, Sora, Runway, etc.)
   - Prompt templates
   - Asset requirements
   - Technical parameters

2. **Phase 3 Output**: Clip division with timing
   - Clip IDs and durations
   - Shot types and camera parameters (from shot-grammar)
   - Section assignments

3. **Phase 1 Output**: Character designs
   - Visual consistency guides
   - Character reference images

## Process Flow

```
1. Load generation strategies from Phase 4
2. Prepare generation queue
3. For each clip:
   a. Load prompt template and assets
   b. Format final generation prompt
   c. Submit to appropriate service (Veo2/Sora/Runway/etc.)
   d. Monitor generation progress
   e. Validate output quality
   f. Store generated clip with metadata
4. Generate execution report
5. Save results to SharedState
```

## Generation Services Integration

### Supported Services

- **Veo2 (Google)**: Best for realistic motion, complex camera work
- **Sora (OpenAI)**: Cinematic quality, longer clips
- **Runway Gen-3**: Fast iteration, experimental visuals
- **Pika**: Stylized anime/cartoon aesthetics
- **Traditional Shooting**: Real camera footage integration
- **Hybrid**: Mix of multiple approaches

### Service Selection Logic

The generation mode for each clip is determined in Phase 4 based on:
- Clip complexity and duration
- Budget constraints
- Quality requirements
- Timeline constraints
- Visual style consistency

## Output Format

Phase 6 produces:

```json
{
  "generated_clips": [
    {
      "clip_id": "clip_001",
      "status": "completed",
      "generation_mode": "veo2",
      "output_path": "shared-workspace/sessions/{session}/clips/clip_001.mp4",
      "generation_time": "2025-11-16T10:30:00Z",
      "actual_duration": 4.2,
      "quality_score": 0.92,
      "metadata": {
        "prompt_used": "...",
        "model_version": "veo2-v1.0",
        "seed": 12345,
        "generation_params": {...}
      }
    }
  ],
  "execution_summary": {
    "total_clips": 45,
    "completed": 43,
    "failed": 2,
    "total_generation_time": "4.5 hours",
    "total_cost": "$450.00",
    "quality_average": 0.89
  },
  "failed_clips": [
    {
      "clip_id": "clip_015",
      "reason": "API timeout",
      "retry_count": 3,
      "fallback_strategy": "use_runway_instead"
    }
  ]
}
```

## Usage

### Running Phase 6

```python
from phase6 import run_phase6

# Execute video generation
results = run_phase6(session_id, mock_mode=True)

# Access generated clips
generated_clips = results['generated_clips']
for clip in generated_clips:
    print(f"{clip['clip_id']}: {clip['status']} - {clip['output_path']}")
```

### Using the Runner Class

```python
from phase6 import Phase6Runner

# Initialize runner
runner = Phase6Runner(session_id, mock_mode=True)

# Run generation
results = runner.run()

# Check status
print(f"Completed: {results['execution_summary']['completed']}/{results['execution_summary']['total_clips']}")
```

## Mock Mode

In mock mode (default), Phase 6:
- Simulates generation requests without calling external APIs
- Creates placeholder video files
- Generates realistic execution timelines
- Provides sample quality scores

This allows testing the full pipeline without incurring API costs.

## Real Mode

In real mode, Phase 6:
- Requires API keys for generation services
- Makes actual API calls to video generation platforms
- Handles rate limiting and retries
- Manages actual file downloads and storage
- Tracks real costs and generation times

### Required Environment Variables

```bash
# For real mode
export VEO2_API_KEY="your-veo2-key"
export SORA_API_KEY="your-sora-key"
export RUNWAY_API_KEY="your-runway-key"
export PIKA_API_KEY="your-pika-key"
```

## Quality Validation

Phase 6 includes automatic quality validation:
- Duration matching (actual vs. planned)
- Visual quality assessment
- Audio sync check (if applicable)
- Consistency with character designs
- Compliance with shot parameters

Failed clips trigger automatic retry with fallback strategies.

## Output Organization

Generated clips are stored in:
```
shared-workspace/sessions/{session_id}/clips/
├── clip_001.mp4
├── clip_002.mp4
├── ...
└── metadata/
    ├── clip_001_meta.json
    ├── clip_002_meta.json
    └── ...
```

## Error Handling

Phase 6 implements robust error handling:
- Automatic retries (up to 3 attempts)
- Fallback to alternative generation modes
- Graceful degradation for non-critical clips
- Detailed error logging
- Recovery from partial failures

## Performance

- **Mock Mode**: Completes in ~10-20 seconds
- **Real Mode**: Depends on service response times
  - Veo2: ~2-5 minutes per clip
  - Sora: ~3-8 minutes per clip
  - Runway: ~1-3 minutes per clip
  - Total: ~2-6 hours for full 45-clip video

## Dependencies

```python
# Optional external service clients
# veo2-client>=1.0.0
# sora-client>=1.0.0
# runway-client>=1.0.0
# pika-client>=1.0.0
```

## Future Enhancements

- Parallel generation support
- Progress streaming
- Cost optimization algorithms
- Quality prediction models
- Automated re-generation for low-quality outputs

---

**Status**: Phase 6 skeleton implemented
**Next Phase**: Phase 7 (Editing & Timeline Assembly)
