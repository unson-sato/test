# Phase 1: Character Design (キャラクター設計)

## Overview

Phase 1 is the second phase of the MV Orchestra v2.8 multi-director competition system. In this phase, 5 directors compete to design main characters, costumes, and visual consistency based on the winning concept from Phase 0.

## Purpose

The goal of Phase 1 is to establish the character visual identity by:
- Building upon Phase 0's winning overall concept
- Designing main character appearances, costumes, and styling
- Developing visual consistency strategies
- Planning character arcs through the song
- Evaluating multiple character design approaches
- Selecting the strongest character design to guide production

## Workflow

1. **Load Phase 0 Concept**: Retrieve winning concept from Phase 0
2. **Design Generation**: Each of 5 directors creates character design proposal
3. **Cross-Evaluation**: All directors evaluate all character designs
4. **Score Aggregation**: Calculate weighted average scores
5. **Winner Selection**: Select the highest-scoring design
6. **State Persistence**: Save all designs, evaluations, and winner

## Prerequisites

**Phase 1 requires Phase 0 to be completed first.**

The Phase 0 winner's concept provides:
- Overall creative direction
- Visual style guidelines
- Narrative structure
- Target audience definition

## Input Data

Phase 1 loads from session state:
- Phase 0 winner's concept
- Song analysis data (from Phase 0)
- Overall creative direction

## Output Data

Phase 1 produces:

### Character Design Proposals (5 total, one per director)
Each design includes:
- `characters`: Array of character descriptions
  - `name`: Character name/role
  - `appearance`: Physical description
  - `personality`: Character personality
  - `costume`: Costume/styling details
  - `role`: Narrative role
- `visual_consistency_strategy`: Approach to maintaining visual coherence
- `character_arc`: How character evolves through the song
- `concept_alignment`: How design matches Phase 0 concept

### Evaluations (5 evaluators × 5 designs)
Each evaluation includes:
- `evaluator`: Director providing the evaluation
- `scores`: Numerical scores for each design (0-100)
- `feedback`: Detailed feedback for each design

### Winner
- `director`: Winning director
- `total_score`: Aggregated weighted score
- `proposal`: Full winning character design
- `all_scores`: Scores for all designs

## Director Approaches

### 1. CORPORATE
- **Character Style**: Clean, professional, broad appeal
- **Costume**: Contemporary, brand-safe wardrobe
- **Strategy**: Professional styling guides, tested palettes

### 2. FREELANCER
- **Character Style**: Unconventional, artistic, unique
- **Costume**: Experimental fashion, bold colors
- **Strategy**: Fluid visual language, artistic inconsistency

### 3. VETERAN
- **Character Style**: Timeless features, refined presence
- **Costume**: Cinematic tailoring, quality fabrics
- **Strategy**: Masterful cinematographic consistency

### 4. AWARD_WINNER
- **Character Style**: Striking, memorable, award-worthy
- **Costume**: Artistically excellent with symbolic meaning
- **Strategy**: Sophisticated visual language with symbolism

### 5. NEWCOMER
- **Character Style**: Fresh, trendy, Gen-Z aesthetic
- **Costume**: Trending streetwear, social-media-ready
- **Strategy**: Flexible for trending formats, social optimization

## Usage

### Python API

```python
from phase1 import run_phase1

# Run Phase 1 (requires existing session with Phase 0 complete)
results = run_phase1(
    session_id="session_20251114_153045_abc123",
    config_path="/home/user/test/config.json",
    mock_mode=True
)

print(f"Winner: {results['winner']['director']}")
print(f"Score: {results['winner']['total_score']:.2f}")
print(f"Main Character: {results['winner']['proposal']['characters'][0]['name']}")
```

### With Existing Session Object

```python
from core import SharedState
from phase1 import Phase1Runner, read_json

# Load session (must have Phase 0 completed)
session = SharedState.load_session("session_id_here")

# Verify Phase 0 is complete
phase0_data = session.get_phase_data(0)
if phase0_data.status != "completed":
    raise ValueError("Phase 0 must be completed first")

# Load config
config = read_json("/home/user/test/config.json")

# Create runner
runner = Phase1Runner(session, config, mock_mode=True)

# Run phase
results = runner.run()
```

## Configuration

Phase 1 uses the following config settings from `config.json`:

```json
{
  "phases": {
    "1": {
      "name": "Character Design",
      "enabled": true,
      "timeout_seconds": 300
    }
  },
  "directors": {
    "weights": {
      "corporate": 1.0,
      "freelancer": 1.0,
      "veteran": 1.0,
      "award_winner": 1.0,
      "newcomer": 1.0
    },
    "competition_mode": "weighted_average"
  }
}
```

## Character Design Components

### Appearance
Physical characteristics, features, styling that define visual identity

### Personality
Character traits that influence performance, expression, and emotional arc

### Costume
Clothing, accessories, styling choices that support character and concept

### Visual Consistency
Strategy for maintaining coherent character appearance throughout MV:
- Color palettes and guidelines
- Styling references
- Continuity management
- Adaptability to different scenes/lighting

### Character Arc
How the character evolves visually and emotionally through the song:
- Opening state
- Transformation moments
- Final state
- Alignment with song structure

## Mock Mode vs Real Mode

### Mock Mode (Default)
- Uses mock character design generation
- Uses mock evaluations
- Fast execution for testing
- No external API calls
- Director-specific design templates

### Real Mode (Coming Soon)
- Calls Claude API with Phase 1 director prompts
- Generates real AI-driven character designs
- Performs genuine evaluations
- Requires API credentials

## File Structure

```
phase1/
├── __init__.py          # Module exports
├── runner.py            # Phase1Runner implementation
├── README.md            # This file
└── test_phase1.py       # Test suite
```

## Error Handling

Phase 1 handles errors gracefully:

- **Phase 0 Not Complete**: Raises `ValueError`
- **No Phase 0 Winner**: Raises `ValueError`
- **Session Not Found**: Raises `FileNotFoundError`
- **Missing Prompt Template**: Raises `FileNotFoundError`
- **General Errors**: Marks phase as failed in session state

## Integration with Phase 0

Phase 1 is tightly coupled to Phase 0:

```python
# Phase 0 output becomes Phase 1 input
phase0_winner = {
    "director": "freelancer",
    "total_score": 85.5,
    "proposal": {
        "concept_theme": "Experimental vision...",
        "visual_style": "Unconventional, artistic...",
        "narrative_structure": "Non-linear...",
        ...
    }
}

# Phase 1 uses this to inform character design
# All Phase 1 designs must align with Phase 0 winner's concept
```

## Next Steps

After Phase 1 completes:
1. Phase 1 winner is saved to session state
2. Phase 2 (Section Direction) uses character design + overall concept
3. Subsequent phases continue building on this foundation

## Testing

See `test_phase1.py` for examples and test cases.

## Example Character Design Output

```json
{
  "director": "veteran",
  "director_name": "Veteran",
  "characters": [
    {
      "name": "クラシックヒーロー (Classic Hero)",
      "appearance": "Timeless features, classic proportions, refined presence",
      "personality": "Depth, gravitas, emotional complexity",
      "costume": "Cinematic tailoring, quality fabrics, timeless silhouettes",
      "role": "Traditional protagonist with universal appeal"
    }
  ],
  "visual_consistency_strategy": "Masterful cinematographic consistency, meticulous continuity",
  "character_arc": "Classic three-act structure, profound emotional depth",
  "concept_alignment": "Designed to match: [Phase 0 concept theme]"
}
```

## Dependencies

- Python 3.8+
- Core modules (SharedState, DirectorProfiles, CodexRunner)
- Phase 0 (must be completed)
- Standard library (json, logging, pathlib)

## Related Documentation

- [Phase 0 README](/home/user/test/phase0/README.md)
- [Core Modules README](/home/user/test/core/README.md)
- [Phase 2 README](/home/user/test/phase2/README.md)
- [CLAUDE.md](/home/user/test/CLAUDE.md)
- [Project Config](/home/user/test/config.json)
