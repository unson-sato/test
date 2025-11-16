# Optimization Tools - MV Orchestra v2.8

This directory contains optimization tools that enhance the multi-director AI competition system by matching visual elements to emotional content.

## Overview

The optimization tools bridge Phase 2 (Section Direction) and Phase 3 (Clip Division) by:

1. **Building target emotion curves** from section-level emotional tones
2. **Optimizing clip durations** to match emotional intensity
3. **Adding creative variance recommendations** for Phase 4 generation

## Tools

### 1. Emotion Target Builder (`emotion_target_builder.py`)

Builds a continuous emotion curve from Phase 2's discrete section directions.

**Purpose:**
- Convert section-level emotional descriptions into quantified values
- Generate smooth interpolation between sections
- Provide emotional intensity reference for optimization

**Input:**
- Phase 2 section directions (from winner proposal)
- Section timing information

**Output:**
- `target_emotion_curve.json` - Emotion values sampled at regular intervals

**Usage:**

```bash
# Standalone CLI
python -m tools.optimization.emotion_target_builder <session_id>

# With custom sampling rate
python -m tools.optimization.emotion_target_builder <session_id> --sampling-rate 0.25

# As module
from tools.optimization.emotion_target_builder import build_target_curve
result = build_target_curve(session_id)
```

**Output Format:**

```json
{
  "metadata": {
    "session_id": "mvorch_20251114_...",
    "created_at": "2025-11-14T10:40:00Z",
    "source_phase": 2,
    "sampling_rate": 0.5,
    "total_duration": 195.0
  },
  "curve": [
    {
      "time": 0.0,
      "emotion": 0.4,
      "source_section": "intro",
      "label": "mysterious"
    },
    ...
  ],
  "sections": [
    {
      "section_name": "intro",
      "start_time": 0.0,
      "end_time": 12.5,
      "target_emotion": 0.4,
      "emotion_label": "mysterious"
    },
    ...
  ],
  "statistics": {
    "min_emotion": 0.2,
    "max_emotion": 1.0,
    "avg_emotion": 0.62,
    "total_samples": 391
  }
}
```

---

### 2. Clip Optimizer (`clip_optimizer.py`)

Optimizes clip durations based on emotional intensity and adds creative recommendations.

**Purpose:**
- Match clip duration to emotional content (high emotion = longer clips)
- Maintain beat alignment and section boundaries
- Generate creative variance suggestions for Phase 4
- Preserve total timeline duration

**Input:**
- Phase 3 clip division (from winner proposal)
- Target emotion curve (from emotion_target_builder)
- Beat timing information

**Output:**
- Modified Phase 3 clip data with `base_allocation` and `creative_adjustments`
- `clip_optimization_summary.json` - Detailed optimization report

**Usage:**

```bash
# Standalone CLI
python -m tools.optimization.clip_optimizer <session_id>

# With custom constraints
python -m tools.optimization.clip_optimizer <session_id> --min-duration 1.0 --max-duration 6.0

# As module
from tools.optimization.clip_optimizer import optimize_clips
result = optimize_clips(session_id)
```

**Optimization Strategy:**

- **High emotion clips (0.8-1.0):** Extended by up to 30% for dramatic impact
- **Medium emotion clips (0.4-0.7):** Minor adjustments (-10% to +10%)
- **Low emotion clips (0.0-0.4):** May be shortened by up to 15% for pacing
- **Constraints:**
  - Minimum duration: 0.8s (configurable)
  - Maximum duration: 8.0s (configurable)
  - Beat alignment: Snaps to nearest beat within tolerance
  - Total duration: Preserved (no timeline expansion/contraction)

**Creative Adjustments:**

Based on emotion score, the optimizer suggests:

- **Lighting variance:** low / medium / high
- **Camera movement variance:** subtle / normal / dynamic
- **Color grading intensity:** minimal / moderate / intense
- **Specific suggestions:** Action items for Phase 4 generation

**Output Format:**

```json
{
  "metadata": {
    "session_id": "mvorch_20251114_...",
    "created_at": "2025-11-14T10:45:00Z",
    "optimization_algorithm": "emotion_matching_v1",
    "total_clips": 69
  },
  "optimization_results": [
    {
      "clip_id": "clip_015",
      "original_duration": 2.5,
      "optimized_duration": 3.2,
      "emotion_score": 0.85,
      "adjustment_made": true,
      "adjustment_reason": "high emotion section, extended for impact",
      "creative_adjustments": {
        "lighting_variance": "high",
        "camera_movement_variance": "high",
        "color_grading_intensity": "intense",
        "variance_level": "high"
      }
    },
    ...
  ],
  "statistics": {
    "clips_adjusted": 12,
    "clips_unchanged": 57,
    "avg_adjustment": 0.23,
    "max_adjustment": 0.8,
    "total_duration_before": 195.0,
    "total_duration_after": 195.0
  }
}
```

---

### 3. Emotion Utilities (`emotion_utils.py`)

Shared utilities for emotion mapping and interpolation.

**Functions:**

- `map_emotion_to_value(text)` - Convert emotion keywords to numeric values
- `interpolate_linear(...)` - Linear interpolation between values
- `interpolate_smooth(...)` - Smoothstep interpolation for natural transitions
- `get_section_emotion_value(section)` - Extract emotion from section dict
- `normalize_emotion_curve(curve)` - Normalize values to target range
- `get_emotion_statistics(curve)` - Calculate min/max/avg/std_dev

**Emotion Mapping:**

```python
EMOTION_MAP = {
    # Low energy (0.1-0.2)
    "calm": 0.2, "peaceful": 0.2, "serene": 0.2,

    # Low-medium energy (0.3-0.4)
    "mysterious": 0.4, "anticipatory": 0.4, "introspective": 0.3,

    # Medium energy (0.5-0.6)
    "neutral": 0.5, "emotional": 0.6, "nostalgic": 0.55,

    # Medium-high energy (0.7-0.8)
    "upbeat": 0.8, "energetic": 0.8, "joyful": 0.75, "euphoric": 0.85,

    # High energy (0.85-1.0)
    "intense": 1.0, "climactic": 1.0, "explosive": 1.0, "dramatic": 0.9
}
```

---

## Integration with Phase Pipeline

### Phase 2 Integration

After Phase 2 completes, automatically trigger emotion target builder:

```python
# In phase2/runner.py - Line 388-389
from tools.optimization.emotion_target_builder import build_target_curve

# After Phase 2 completion
build_target_curve(session_id)
```

### Phase 3 Integration

After Phase 3 completes, automatically trigger clip optimizer:

```python
# In phase3/runner.py - Line 471-472
from tools.optimization.clip_optimizer import optimize_clips

# After Phase 3 completion
optimize_clips(session_id)
```

### Phase 4 Usage

Phase 4 can use the optimization data:

```python
# Load optimized clips
clips = phase3_data['winner']['proposal']['clips']

for clip in clips:
    base_duration = clip['base_allocation']  # Optimized duration
    creative_adj = clip['creative_adjustments']  # Variance suggestions

    # Apply creative adjustments to generation parameters
    if creative_adj['variance_level'] == 'high':
        # Use dramatic lighting, dynamic camera, intense colors
        pass
```

---

## Testing

### Run All Tests

```bash
# Using pytest
pytest tools/optimization/ -v

# Manual test execution
python tools/optimization/test_emotion_target_builder.py
python tools/optimization/test_clip_optimizer.py
```

### Test Requirements

Tests require an existing session with Phase 0-3 completed. The test suite uses:
- Session ID: `mvorch_20251114_163545_d1c7c8d0` (or latest completed session)
- Required phases: 0 (Overall Design), 1 (Characters), 2 (Sections), 3 (Clips)

### Test Coverage

**Emotion Target Builder:**
- Emotion keyword mapping
- Section metadata extraction
- Curve building and interpolation
- Statistics calculation
- File output validation

**Clip Optimizer:**
- Input loading (clips, curve, beats)
- Emotion score calculation
- Ideal duration calculation
- Beat snapping
- Creative adjustment generation
- Full optimization process
- Phase 3 data updates

---

## Algorithm Details

### Emotion Matching Algorithm v1

**Objective:** Optimize clip durations to match emotional intensity while respecting constraints.

**Steps:**

1. **Load Inputs**
   - Phase 3 clips with original durations
   - Emotion curve from Phase 2 sections
   - Beat timing for alignment

2. **Calculate Emotion Scores**
   - For each clip, find all curve points within its timeframe
   - Average emotion values across clip duration
   - Result: emotion score 0.0-1.0 per clip

3. **Determine Ideal Duration**
   - High emotion (0.8+): Extend by up to 30% (dramatic impact)
   - Medium emotion (0.4-0.7): Adjust -10% to +10% (flow)
   - Low emotion (0.0-0.4): Shorten by up to 15% (pacing)
   - Apply shot type modifiers (wide shots need more time)

4. **Apply Constraints**
   - Snap to nearest beat (within tolerance)
   - Enforce min/max duration limits
   - Prevent gaps between clips
   - Maintain section boundaries

5. **Generate Creative Adjustments**
   - Map emotion score to variance levels
   - Suggest lighting, camera, color parameters
   - Provide actionable recommendations

6. **Update and Save**
   - Modify Phase 3 clips with `base_allocation`
   - Add `creative_adjustments` to each clip
   - Save optimization summary
   - Update session metadata

---

## Configuration

### Emotion Target Builder

```python
EmotionTargetBuilder(
    session_id="...",
    sampling_rate=0.5  # Time between samples (seconds)
)
```

### Clip Optimizer

```python
ClipOptimizer(
    session_id="...",
    min_clip_duration=0.8,  # Minimum clip length
    max_clip_duration=8.0   # Maximum clip length
)
```

### Emotion Mapping

Customize emotion keywords in `emotion_utils.py`:

```python
EMOTION_MAP = {
    "custom_keyword": 0.75,  # Add custom mappings
    # ...
}
```

---

## Output Files

All outputs are saved to the session directory: `shared-workspace/sessions/<session_id>/`

### Files Created

1. **target_emotion_curve.json**
   - Created by: emotion_target_builder
   - Contains: Emotion curve, section metadata, statistics
   - Used by: clip_optimizer, Phase 4 (optional)

2. **clip_optimization_summary.json**
   - Created by: clip_optimizer
   - Contains: Optimization results, statistics, creative adjustments
   - Used by: Phase 4, analysis tools

3. **state.json** (updated)
   - Session state with optimization logs
   - Global data with curve/summary paths

---

## Future Enhancements

### Potential Improvements

1. **Advanced Interpolation**
   - Bezier curves for more natural emotion transitions
   - Section-specific transition strategies

2. **Machine Learning Integration**
   - Learn optimal duration patterns from successful MVs
   - Predict emotional impact of clip sequences

3. **Multi-dimensional Optimization**
   - Optimize for multiple factors: emotion, energy, narrative flow
   - Balance competing objectives with weighted scoring

4. **Real-time Preview**
   - Generate preview timeline visualization
   - Interactive adjustment of emotion curve

5. **A/B Testing Support**
   - Generate multiple optimization variants
   - Compare results across different algorithms

6. **Beat-aware Transitions**
   - Optimize transition timing to musical phrases
   - Detect chorus drops, bridges, breaks

---

## Troubleshooting

### Common Issues

**Error: "Phase 2 must be completed before building emotion curve"**
- Ensure Phase 0, 1, and 2 have run successfully
- Check session status: `session.get_phase_data(2).status == "completed"`

**Error: "Target emotion curve not found"**
- Run emotion_target_builder before clip_optimizer
- Check for `target_emotion_curve.json` in session directory

**Error: "No clips found in Phase 3 winner proposal"**
- Ensure Phase 3 has completed
- Verify Phase 3 winner has clips array

**Emotion scores all similar (low variance)**
- Check Phase 2 sections have varied emotional tones
- Verify emotion keywords are being mapped correctly
- Consider normalizing the emotion curve

**Duration optimization seems too aggressive**
- Adjust min/max duration constraints
- Modify adjustment factors in `calculate_ideal_duration()`
- Increase beat snapping tolerance

---

## API Reference

### build_target_curve()

```python
def build_target_curve(session_id: str, sampling_rate: float = 0.5) -> Dict[str, Any]:
    """
    Build target emotion curve from Phase 2 sections.

    Args:
        session_id: Session identifier
        sampling_rate: Time between samples in seconds

    Returns:
        Dict with 'curve', 'sections', 'statistics', 'curve_path'

    Raises:
        RuntimeError: If Phase 2 not completed or data missing
    """
```

### optimize_clips()

```python
def optimize_clips(session_id: str,
                  min_duration: float = 0.8,
                  max_duration: float = 8.0) -> Dict[str, Any]:
    """
    Optimize clip durations and add creative adjustments.

    Args:
        session_id: Session identifier
        min_duration: Minimum clip duration in seconds
        max_duration: Maximum clip duration in seconds

    Returns:
        Dict with 'optimization_results', 'statistics', 'variance_counts', 'summary_path'

    Raises:
        RuntimeError: If Phase 3 not completed or emotion curve missing
    """
```

---

## Version History

| Version | Date       | Changes                                    |
|---------|------------|--------------------------------------------|
| 1.0.0   | 2025-11-14 | Initial implementation                     |
|         |            | - Emotion target builder                   |
|         |            | - Clip optimizer                           |
|         |            | - Emotion utilities                        |
|         |            | - Test suites                              |

---

## Authors

- MV Orchestra v2.8 Development Team
- AI Assistant (Claude)

## License

Part of the MV Orchestra v2.8 project.
