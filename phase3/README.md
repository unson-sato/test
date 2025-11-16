# Phase 3: Clip Division

## Overview

Phase 3 of MV Orchestra v2.8 is where five AI directors compete to divide the timeline into individual clips/shots, aligned to musical beats and optimized for emotional flow. Each director proposes a clip division strategy that balances artistic vision with practical production needs.

## Purpose

Transform section-level directions (from Phase 2) into concrete clip-by-clip timelines with beat alignment, shot types, and duration allocation for efficient video generation.

## Input Requirements

Phase 3 requires the following inputs:

1. **Phase 2 Output**: Section-by-section directions with emotional arcs
2. **analysis.json**: Beat and timing data
   - Beat timestamps (in seconds)
   - Bar timestamps (optional)
   - BPM (beats per minute)
   - Total duration

## Process Flow

```
1. Load Phase 2 section directions
2. Load beat/bar data from analysis.json
3. For each of 5 directors:
   a. Generate clip division strategy
   b. For each clip:
      - Assign unique clip ID
      - Set start/end times (aligned to beats)
      - Specify section assignment
      - Define shot type and camera movement
      - Estimate complexity
      - Set base duration allocation
4. Each director evaluates all proposals
5. Aggregate scores and select winner
6. Save results to SharedState
7. [Future] Auto-trigger Clip Optimizer
```

## Beat Alignment

### The Beat Snapping Algorithm

Phase 3 uses a sophisticated beat alignment algorithm:

```python
def snap_to_beat(
    time: float,
    beat_times: List[float],
    tolerance: float = 0.2
) -> float:
    """
    Snap a time to the nearest beat within tolerance.

    Args:
        time: The time to snap (in seconds)
        beat_times: List of beat timestamps
        tolerance: Maximum distance to snap (default: 0.2s)

    Returns:
        Snapped time if within tolerance, else original time
    """
    # Find closest beat
    closest_beat = min(beat_times, key=lambda b: abs(b - time))
    distance = abs(closest_beat - time)

    # Only snap if within tolerance
    if distance <= tolerance:
        return closest_beat
    else:
        return time
```

### Beat Alignment Strategy

- **Tolerance**: Default 0.2 seconds (adjustable)
- **Priority**: Section boundaries snap first, then clip boundaries
- **Minimum Clip Duration**: 1.0 seconds after snapping
- **Adjustment**: If snapping creates clips <1s, use original times

## Output Format

Phase 3 produces the following output structure:

```json
{
  "proposals": [
    {
      "director": "freelancer",
      "clips": [
        {
          "clip_id": "clip_001",
          "start_time": 0.0,
          "end_time": 2.1,
          "duration": 2.1,
          "section": "intro",
          "shot_type": "establishing wide",
          "camera_movement": "static",
          "complexity": "medium",
          "beat_aligned": true,
          "base_allocation": 2.1
        }
      ],
      "total_clips": 45,
      "average_clip_length": 3.2,
      "beat_alignment_strategy": "snap to nearest beat"
    }
  ],
  "evaluations": [...],
  "winner": {
    "director": "freelancer",
    "total_score": 39.6,
    "proposal": {...}
  }
}
```

## Usage

### Running Phase 3

```python
from phase3 import run_phase3

# Run Phase 3 for a session
results = run_phase3(session_id, mock_mode=True)

# Access winner's clips
winner_clips = results['winner']['proposal']['clips']

print(f"Total clips: {len(winner_clips)}")
print(f"Average duration: {results['winner']['proposal']['average_clip_length']:.2f}s")

for clip in winner_clips[:5]:
    print(f"{clip['clip_id']}: {clip['shot_type']} ({clip['duration']:.2f}s)")
```

### Using the Runner Class

```python
from phase3 import Phase3Runner

# Initialize runner
runner = Phase3Runner(session_id, mock_mode=True)

# Load inputs
phase2_directions, beat_times, metadata = runner.load_phase_inputs()

# Generate proposal from specific director
from core.director_profiles import DirectorType

proposal = runner.generate_clip_proposal(
    DirectorType.FREELANCER,
    phase2_directions,
    beat_times,
    metadata
)

# Run complete competition
results = runner.run()
```

## Clip Utilities

### Core Functions

The `clip_utils.py` module provides essential utilities:

```python
from phase3.clip_utils import (
    snap_to_beat,
    load_beat_data,
    validate_clip_coverage,
    generate_clip_id,
    estimate_clip_complexity,
    calculate_clip_statistics,
    optimize_beat_alignment
)

# Beat alignment
beat_times = load_beat_data(analysis_data)
snapped_time = snap_to_beat(10.3, beat_times, tolerance=0.2)

# Clip validation
validate_clip_coverage(clips, total_duration=180.0)

# ID generation
clip_id = generate_clip_id(42)  # Returns "clip_042"

# Complexity estimation
complexity = estimate_clip_complexity("close-up detail", 1.8, has_movement=True)

# Statistics
stats = calculate_clip_statistics(clips)
print(f"Beat-aligned: {stats['beat_aligned_percentage']:.1f}%")
```

### Advanced Utilities

```python
from phase3.clip_utils import (
    find_nearest_beat,
    find_beat_range,
    merge_short_clips,
    split_long_clips,
    optimize_beat_alignment
)

# Find beats in a time range
beats_in_intro = find_beat_range(0.0, 8.5, beat_times)

# Optimize all clips for beat alignment
optimized_clips = optimize_beat_alignment(clips, beat_times, tolerance=0.3)

# Merge clips shorter than threshold
merged = merge_short_clips(clips, min_duration=1.5)

# Split clips longer than threshold
split = split_long_clips(clips, max_duration=8.0, beat_times=beat_times)
```

## Director Approaches

### Corporate Director
- **Pacing**: Moderate, audience-friendly (3-4s per clip)
- **Alignment**: Strong beat alignment for commercial appeal
- **Complexity**: Balanced, professional coverage

### Freelancer Director
- **Pacing**: Flexible, emotion-driven (2-5s variable)
- **Alignment**: Organic, allows creative flexibility
- **Complexity**: High variation, artistic choices

### Veteran Director
- **Pacing**: Thoughtful, traditional (3.5-5s per clip)
- **Alignment**: Respectful of musical structure
- **Complexity**: Refined, craftsmanship-focused

### Award Winner Director
- **Pacing**: Sophisticated, variable for impact (2-6s)
- **Alignment**: Strategic, serves artistic vision
- **Complexity**: High, pursuing excellence

### Newcomer Director
- **Pacing**: Fast, contemporary (2-3s per clip)
- **Alignment**: Tight to beats, modern style
- **Complexity**: Bold, experimental choices

## Clip Complexity Estimation

The system estimates clip complexity based on:

1. **Shot Type**:
   - Wide/establishing: +1 point
   - Medium: +1 point
   - Close-up/detail: +2 points

2. **Duration**:
   - < 2.0s: +2 points (harder to execute)
   - 2.0-3.5s: +1 point
   - > 3.5s: +0 points

3. **Camera Movement**:
   - Movement: +1 point
   - Static: +0 points

**Complexity Levels**:
- 0-2 points: "low"
- 3-4 points: "medium"
- 5+ points: "high"

## Evaluation Criteria

Directors evaluate clip proposals based on:

1. **Beat Alignment** (25%): How well clips align with music
2. **Pacing Variety** (20%): Appropriate rhythm and flow
3. **Production Feasibility** (20%): Can it be generated efficiently?
4. **Emotional Progression** (20%): Does it serve the story?
5. **Creative Innovation** (15%): Is it distinctive?

## Testing

Run the test suite to validate Phase 3 functionality:

```bash
# Run all tests
python /home/user/test/phase3/test_phase3.py

# Or use pytest
pytest /home/user/test/phase3/test_phase3.py -v
```

### Key Tests

- `test_snap_to_beat`: Beat alignment algorithm
- `test_load_beat_data`: Loading from analysis.json
- `test_validate_clip_coverage`: Timeline validation
- `test_generate_clip_id`: ID generation
- `test_estimate_clip_complexity`: Complexity calculation
- `test_phase3_full_run`: Complete end-to-end execution

## Integration Points

### Prerequisites
- Phase 0 completed (overall design concept)
- Phase 1 completed (character designs)
- Phase 2 completed (section directions)
- `analysis.json` with beat data

### Outputs Used By
- **Phase 4**: Clip definitions guide generation strategy
- **Clip Optimizer** (Wave 3): Refines timing and allocation
- **Generation Pipeline**: Uses clip metadata for video creation

### Post-Processing (Future)

After Phase 3 completes, the system will automatically trigger:

```python
# Wave 3 feature - not yet implemented
tools.optimization.clip_optimizer.optimize_clips(session_id)
```

The optimizer will:
- Compare clips to emotion target curve
- Adjust base_allocation times
- Add creative_adjustments suggestions
- Save optimization summary

## File Structure

```
phase3/
├── __init__.py              # Module exports
├── runner.py                # Main Phase 3 runner
├── clip_utils.py           # Clip processing and beat alignment
├── test_phase3.py          # Test suite
└── README.md               # This file
```

## Typical Clip Counts

Based on song duration and director style:

| Duration | Corporate | Freelancer | Veteran | Award Winner | Newcomer |
|----------|-----------|------------|---------|--------------|----------|
| 3 min    | 35-45     | 30-50      | 25-35   | 30-45        | 50-70    |
| 4 min    | 45-60     | 40-65      | 30-45   | 40-60        | 65-90    |
| 5 min    | 55-75     | 50-80      | 35-55   | 50-75        | 80-110   |

## Beat Alignment Best Practices

1. **Tolerance Settings**:
   - Strict (0.1s): For precise rhythmic sync
   - Normal (0.2s): Balanced flexibility
   - Loose (0.3s): More creative freedom

2. **Section Boundaries**:
   - Always align section starts to strong beats
   - Section ends can be more flexible

3. **Clip Duration**:
   - Minimum: 1.0s (after snapping)
   - Typical: 2.5-4.0s
   - Maximum: 8.0s (before splitting)

4. **Coverage**:
   - Allow small gaps (<0.5s) between clips
   - Validate no overlaps
   - Ensure full timeline coverage

## Error Handling

Phase 3 includes comprehensive error handling:

```python
try:
    results = run_phase3(session_id)
except RuntimeError as e:
    # Phase 2 not completed
    print(f"Prerequisites not met: {e}")
except FileNotFoundError as e:
    # analysis.json not found
    print(f"Missing input file: {e}")
except ValueError as e:
    # Invalid clip coverage
    print(f"Invalid clip data: {e}")
```

## Configuration

Phase 3 behavior can be configured via `config.json`:

```json
{
  "phases": {
    "3": {
      "name": "Clip Division",
      "enabled": true,
      "timeout_seconds": 300
    }
  },
  "audio_analysis": {
    "extract_beats": true,
    "sample_rate": 22050,
    "hop_length": 512
  }
}
```

## Troubleshooting

### "Phase 2 must be completed before running Phase 3"
- Ensure Phase 2 has been run successfully
- Check: `session.get_phase_data(2).status == 'completed'`

### "No beat data found in analysis.json"
- Verify 'beats' or 'beat_times' exists in analysis.json
- System will estimate beats from BPM if not found
- Check BPM value is present and reasonable (60-200)

### "Clip overlap detected"
- Review clip generation logic
- Check beat snapping isn't creating overlaps
- Validate clips are processed in time order

### "Clips end at X but duration is Y"
- Some directors may not cover full timeline
- Check if intentional (e.g., fade out on outro)
- Verify last clip end_time matches song duration

## Performance Optimization

For large projects:

```python
# Process clips in batches
batch_size = 100
for i in range(0, len(all_clips), batch_size):
    batch = all_clips[i:i + batch_size]
    validate_clip_coverage(batch, total_duration)

# Use beat range queries for efficiency
beats_needed = find_beat_range(section_start, section_end, beat_times)
```

## Future Enhancements

Planned improvements for Phase 3:

1. **Real AI Integration**: Replace mock with actual Claude API calls
2. **Multi-Pass Optimization**: Iterative refinement of clip boundaries
3. **Shot Variation Analysis**: Ensure good mix of shot types
4. **Transition Planning**: Smart transitions between clips
5. **Visual Similarity**: Group clips by visual requirements

## References

- [Director Profiles](/home/user/test/core/director_profiles.py)
- [Shared State Management](/home/user/test/core/shared_state.py)
- [Phase 3 Prompts](/home/user/test/.claude/prompts_v2/phase3_*.md)
- [Config](/home/user/test/config.json)
- [Phase 2 README](/home/user/test/phase2/README.md)
