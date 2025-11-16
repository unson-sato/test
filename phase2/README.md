# Phase 2: Section Direction Design

## Overview

Phase 2 of MV Orchestra v2.8 is where five AI directors compete to design section-by-section direction for the music video. Each director creates a detailed plan for every musical section (intro, verse, chorus, bridge, outro), specifying emotional tone, camera work, lighting, character actions, and transitions.

## Purpose

Transform the high-level concept (from Phase 0) and character designs (from Phase 1) into concrete section-by-section direction that maintains emotional flow throughout the music video.

## Input Requirements

Phase 2 requires the following inputs:

1. **Phase 0 Output**: Overall design concept and creative direction
2. **Phase 1 Output**: Character designs and visual identity
3. **analysis.json**: Song structure with section timing
   - Section labels (intro, verse, chorus, etc.)
   - Start and end times for each section
   - Optional: BPM and mood data

## Process Flow

```
1. Load Phase 0 concept
2. Load Phase 1 characters
3. Load song sections from analysis.json
4. For each of 5 directors:
   a. Generate section-by-section direction
   b. Specify for each section:
      - Emotional tone
      - Camera/composition choices
      - Lighting and color palette
      - Character actions/positioning
      - Transition to next section
5. Each director evaluates all proposals
6. Aggregate scores and select winner
7. Save results to SharedState
8. [Future] Auto-trigger Emotion Target Builder
```

## Output Format

Phase 2 produces the following output structure:

```json
{
  "proposals": [
    {
      "director": "award_winner",
      "sections": [
        {
          "section_name": "intro",
          "start_time": 0.0,
          "end_time": 8.5,
          "duration": 8.5,
          "emotional_tone": "mysterious, anticipation",
          "camera_work": "slow dolly in, wide to medium",
          "lighting": "low key, blue tones",
          "character_action": "protagonist standing alone",
          "transition": "match cut to verse",
          "director_notes": "..."
        }
      ],
      "overall_emotional_arc": "...",
      "visual_continuity_notes": "..."
    }
  ],
  "evaluations": [...],
  "winner": {
    "director": "award_winner",
    "total_score": 42.8,
    "proposal": {...}
  }
}
```

## Usage

### Running Phase 2

```python
from phase2 import run_phase2

# Run Phase 2 for a session
results = run_phase2(session_id, mock_mode=True)

# Access winner's section directions
winner_sections = results['winner']['proposal']['sections']

for section in winner_sections:
    print(f"{section['section_name']}: {section['emotional_tone']}")
```

### Using the Runner Class

```python
from phase2 import Phase2Runner

# Initialize runner
runner = Phase2Runner(session_id, mock_mode=True)

# Load inputs
phase0_concept, phase1_characters, song_sections = runner.load_phase_inputs()

# Generate proposal from specific director
from core.director_profiles import DirectorType

proposal = runner.generate_section_proposal(
    DirectorType.CORPORATE,
    phase0_concept,
    phase1_characters,
    song_sections
)

# Run complete competition
results = runner.run()
```

## Utilities

### Section Utilities

The `section_utils.py` module provides helper functions:

```python
from phase2.section_utils import (
    load_song_sections,
    validate_section_coverage,
    extract_section_summary,
    get_section_types,
    calculate_emotional_progression
)

# Load sections from analysis.json
sections = load_song_sections(analysis_data)

# Validate coverage
validate_section_coverage(sections)

# Get summary stats
summary = extract_section_summary(sections)
print(f"Total duration: {summary['total_duration']}s")
print(f"Section types: {summary['section_types']}")

# Calculate emotional arc
progression = calculate_emotional_progression(sections, section_directions)
```

## Director Approaches

Each director brings their unique perspective to section direction:

### Corporate Director
- Focus: Audience retention and engagement
- Strengths: Clear emotional beats, shareable moments
- Strategy: Hook early, build momentum, prevent drop-off

### Freelancer Director
- Focus: Artistic experimentation and authenticity
- Strengths: Creative risk-taking, unique vision
- Strategy: Follow emotional intuition, break conventions

### Veteran Director
- Focus: Traditional craftsmanship and timeless storytelling
- Strengths: Refined technique, emotional depth
- Strategy: Proven methods, meticulous execution

### Award Winner Director
- Focus: Artistic excellence and cultural impact
- Strengths: Sophisticated visual language, critical acclaim
- Strategy: Balance artistry with accessibility

### Newcomer Director
- Focus: Contemporary trends and fresh perspectives
- Strengths: Current cultural awareness, bold choices
- Strategy: Embrace trends, unafraid to experiment

## Evaluation Criteria

Directors evaluate proposals based on:

1. **Emotional Coherence** (25%): Does the emotional arc make sense?
2. **Visual Continuity** (20%): Is there consistent visual language?
3. **Engagement Strategy** (20%): Will it keep viewers watching?
4. **Creative Innovation** (20%): Is it fresh and distinctive?
5. **Feasibility** (15%): Can this actually be produced?

## Testing

Run the test suite to validate Phase 2 functionality:

```bash
# Run all tests
python /home/user/test/phase2/test_phase2.py

# Or use pytest
pytest /home/user/test/phase2/test_phase2.py -v
```

## Integration Points

### Prerequisites
- Phase 0 must be completed (overall design concept)
- Phase 1 must be completed (character designs)
- `analysis.json` must exist with section data

### Outputs Used By
- **Phase 3**: Section directions guide clip division
- **Phase 4**: Section emotional arcs inform generation strategy
- **Emotion Target Builder** (Wave 3): Creates emotion curves from sections

### Post-Processing (Future)

After Phase 2 completes, the system will automatically trigger:

```python
# Wave 3 feature - not yet implemented
tools.optimization.emotion_target_builder.build_target_curve(session_id)
```

This will analyze the winning section directions and create an emotion target curve for optimization.

## File Structure

```
phase2/
├── __init__.py              # Module exports
├── runner.py                # Main Phase 2 runner
├── section_utils.py         # Section processing utilities
├── test_phase2.py          # Test suite
└── README.md               # This file
```

## Error Handling

Phase 2 includes comprehensive error handling:

```python
try:
    results = run_phase2(session_id)
except RuntimeError as e:
    # Phase 0 or Phase 1 not completed
    print(f"Prerequisites not met: {e}")
except FileNotFoundError as e:
    # analysis.json not found
    print(f"Missing input file: {e}")
except ValueError as e:
    # Invalid section data
    print(f"Invalid data: {e}")
```

## Configuration

Phase 2 behavior can be configured via `config.json`:

```json
{
  "phases": {
    "2": {
      "name": "Section Direction",
      "enabled": true,
      "timeout_seconds": 300
    }
  },
  "evaluation": {
    "scoring_scale": {
      "min": 0,
      "max": 100,
      "passing_threshold": 60
    }
  }
}
```

## Best Practices

1. **Section Coverage**: Ensure analysis.json covers the entire song
2. **Validation**: Always validate section coverage before processing
3. **Mock Mode**: Use mock_mode=True for testing and development
4. **Error Handling**: Wrap Phase 2 execution in try-except blocks
5. **State Management**: Let SharedState handle persistence automatically

## Troubleshooting

### "Phase 0 must be completed before running Phase 2"
- Ensure Phase 0 has been run and completed successfully
- Check session state: `session.get_phase_data(0).status == 'completed'`

### "No sections found in analysis.json"
- Verify analysis.json exists in `shared-workspace/input/`
- Check that 'sections' key exists in analysis.json
- Validate section structure (must have 'start', 'end', 'label')

### "Section overlap detected"
- Review analysis.json section timing
- Small overlaps are logged as warnings
- Large overlaps may indicate analysis errors

## Future Enhancements

Planned improvements for Phase 2:

1. **Real AI Integration**: Replace mock with actual Claude API calls
2. **Prompt Template Loading**: Load director-specific prompts
3. **Emotion Target Builder**: Auto-trigger optimization
4. **Multi-Version Support**: Generate multiple section direction versions
5. **Visual References**: Include style frame suggestions

## References

- [Director Profiles](/home/user/test/core/director_profiles.py)
- [Shared State Management](/home/user/test/core/shared_state.py)
- [Phase 2 Prompts](/home/user/test/.claude/prompts_v2/phase2_*.md)
- [Config](/home/user/test/config.json)
