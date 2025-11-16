# Phase 7: Editing & Timeline Assembly

## Overview

Phase 7 assembles generated video clips into a cohesive timeline using shot-grammar editing rules. This phase applies transitions, temporal techniques, and ensures proper pacing and emotional flow.

## Purpose

Transform individual clips into a complete music video by:
- Assembling clips into timeline according to Phase 3 divisions
- Applying transitions based on shot-grammar rules
- Implementing temporal techniques (speed ramps, freeze frames, etc.)
- Ensuring beat-accurate editing
- Applying scene transition logic for emotional flow
- Generating editing project files (DaVinci Resolve/Premiere)

## Input Requirements

Phase 7 requires:

1. **Phase 6 Output**: Generated video clips
   - All clip files (.mp4)
   - Clip metadata and quality scores

2. **Phase 3 Output**: Clip division and timing
   - Start/end times for each clip
   - Shot parameters (shot_size, camera_movement, etc.)
   - Beat alignment data

3. **Shot Grammar**: Editing rules
   - `editing_transitions`: 15 transition types
   - `temporal_techniques`: 10 time manipulation techniques
   - `scene_transition_logic`: 7 transition rules
   - `camera_choreo_sync`: Sync patterns

4. **Analysis Data**: Musical structure
   - Beat timestamps
   - Section boundaries
   - BPM and tempo changes

## Process Flow

```
1. Load generated clips from Phase 6
2. Load clip timing from Phase 3
3. Load shot-grammar editing rules
4. For each clip transition:
   a. Analyze energy levels of adjacent clips
   b. Select appropriate transition from shot-grammar
   c. Apply transition with beat sync
5. Apply temporal techniques
   a. Slow-motion for emotional peaks
   b. Speed ramps for energy shifts
   c. Freeze frames for punctuation
6. Generate timeline
7. Export editing project file
8. Save results to SharedState
```

## Shot-Grammar Editing Rules

### Editing Transitions (15 types)

From `shot-grammar.json`:

- **hard_cut**: Direct, immediate (0 frames)
- **crossfade_dissolve**: Soft, dreamlike (12-36 frames)
- **whip_pan_transition**: Dynamic energy transfer
- **match_cut**: Visual poetry (action/graphic/conceptual)
- **smash_cut**: Shock, contrast emphasis
- **fade_to_black/white**: Chapter endings, transcendence
- **light_leak_transition**: Organic, warm transition
- **glitch_cut**: Digital, modern aesthetic
- **speed_ramp_transition**: Momentum shift
- And more...

### Scene Transition Logic (7 rules)

- **energy_curve**: Small → medium → large → max → calm
- **contrast_pairs**: Intense → calm for rhythm
- **motion_match_cut**: Match direction/speed
- **shape_match_cut**: Match visual structure
- **lyric_synced_cut**: Sync to lyric keywords
- **tempo_shift_transition**: Speed ramp on tempo change
- **emotional_drop_transition**: Color/composition shift

### Temporal Techniques (10 types)

- **slow_motion**: Emotion extension, beauty detail
- **fast_motion**: Time compression, urgency
- **reverse_playback**: Surreal, time reversal
- **freeze_frame**: Moment crystallization
- **speed_ramp**: Momentum shift
- **time_lapse**: Change over time
- **bullet_time_360**: Matrix effect
- And more...

## Transition Selection Logic

```python
def select_transition(clip_a, clip_b, beat_sync=True):
    """
    Select appropriate transition based on:
    - Energy difference between clips
    - Shot types and movements
    - Section boundaries
    - Beat alignment
    - Emotional arc
    """
    energy_diff = calculate_energy_difference(clip_a, clip_b)

    if energy_diff > 0.7:
        # Large energy jump: use dynamic transition
        return "whip_pan_transition" or "smash_cut"
    elif energy_diff < -0.5:
        # Energy drop: use soft transition
        return "crossfade_dissolve" or "fade_to_black"
    elif is_section_boundary(clip_b):
        # Section change: match to section type
        return select_by_section_type(clip_b.section)
    else:
        # Normal flow: use standard cut
        return "hard_cut"
```

## Timeline Structure

The generated timeline includes:

```json
{
  "timeline": {
    "clips": [
      {
        "clip_id": "clip_001",
        "track": "video1",
        "start_time": 0.0,
        "end_time": 4.2,
        "source_file": "clips/clip_001.mp4",
        "in_point": 0.0,
        "out_point": 4.2,
        "transition_in": null,
        "transition_out": {
          "type": "hard_cut",
          "duration": 0.0
        },
        "effects": [],
        "speed": 1.0
      },
      {
        "clip_id": "clip_002",
        "track": "video1",
        "start_time": 4.2,
        "end_time": 7.8,
        "source_file": "clips/clip_002.mp4",
        "in_point": 0.0,
        "out_point": 3.6,
        "transition_in": {
          "type": "hard_cut",
          "duration": 0.0
        },
        "transition_out": {
          "type": "crossfade_dissolve",
          "duration": 0.5
        },
        "effects": [
          {
            "type": "slow_motion",
            "speed_factor": 0.8,
            "start_offset": 2.0,
            "duration": 1.6
          }
        ],
        "speed": 1.0
      }
    ],
    "total_duration": 180.0,
    "frame_rate": 24,
    "resolution": "1920x1080"
  }
}
```

## Output Formats

### DaVinci Resolve XML

Phase 7 can export timeline as:
- `.drp` (DaVinci Resolve Project)
- XML for Final Cut Pro
- EDL for legacy systems
- JSON for custom tools

### Premiere Pro XML

Compatible with Adobe Premiere Pro for further editing.

## Usage

### Running Phase 7

```python
from phase7 import run_phase7

# Execute timeline assembly
results = run_phase7(session_id, mock_mode=True)

# Access timeline
timeline = results['timeline']
print(f"Timeline duration: {timeline['total_duration']}s")
print(f"Total clips: {len(timeline['clips'])}")
```

### Custom Transition Rules

```python
from phase7 import Phase7Runner

runner = Phase7Runner(session_id)

# Override transition selection
runner.set_transition_rule('intro', 'fade_to_white')
runner.set_transition_rule('outro', 'fade_to_black')

results = runner.run()
```

## Beat-Accurate Editing

Phase 7 ensures all cuts align to beats:

```python
def snap_cut_to_beat(cut_time, beat_times):
    """Snap edit points to nearest beat"""
    nearest_beat = min(beat_times, key=lambda b: abs(b - cut_time))
    if abs(nearest_beat - cut_time) < 0.1:  # 100ms tolerance
        return nearest_beat
    return cut_time
```

## Emotional Flow Optimization

Phase 7 optimizes transitions for emotional impact:

1. **Energy Curve Matching**: Follow shot-grammar energy curve patterns
2. **Contrast Pairing**: Alternate high/low energy for rhythm
3. **Lyric Sync**: Special cuts on keyword lyrics
4. **Section Transitions**: Appropriate transitions at section boundaries

## Mock Mode

In mock mode, Phase 7:
- Generates timeline structure without actual editing
- Simulates transition selection
- Creates project file templates
- Provides preview of edit decisions

## Real Mode

In real mode, Phase 7:
- Loads actual video files
- Applies real transitions and effects
- Generates editable project files
- Exports preview renders

## Dependencies

```python
# Optional
# ffmpeg-python>=0.2.0  # For video processing
# xmltodict>=0.13.0     # For XML project files
```

## Performance

- **Mock Mode**: ~5-10 seconds
- **Real Mode**: ~1-3 minutes (depending on clip count)

## Future Enhancements

- Advanced color grading integration
- Audio-reactive editing
- AI-powered transition selection
- Multi-track editing support
- Real-time preview generation

---

**Status**: Phase 7 skeleton implemented
**Next Phase**: Phase 8 (Effects & Lyric Motion)
