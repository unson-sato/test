# Phase 0: Overall Design (全体設計)

## Overview

Phase 0 is the first phase of the MV Orchestra v2.8 multi-director competition system. In this phase, 5 directors with distinct personalities compete to propose the overall music video concept based on song analysis.

## Purpose

The goal of Phase 0 is to establish the high-level creative direction for the music video by:
- Analyzing song characteristics (BPM, energy, mood, lyrics)
- Developing creative concepts that match the song's essence
- Evaluating multiple creative approaches through multi-director competition
- Selecting the strongest overall vision to guide subsequent phases

## Workflow

1. **Input Loading**: Load song analysis data (BPM, sections, mood, lyrics)
2. **Proposal Generation**: Each of 5 directors generates a unique concept proposal
3. **Cross-Evaluation**: All directors evaluate all proposals (including their own)
4. **Score Aggregation**: Calculate weighted average scores
5. **Winner Selection**: Select the highest-scoring proposal as the winner
6. **State Persistence**: Save all proposals, evaluations, and winner to session state

## The Five Directors

### 1. CORPORATE (会社員クリエイター)
- **Focus**: Commercial viability, brand safety, broad appeal
- **Strengths**: Marketability, stakeholder management
- **Style**: Polished, professional, narrative-focused

### 2. FREELANCER (フリーランス)
- **Focus**: Artistic independence, creative experimentation
- **Strengths**: Innovation, unique vision, boundary-pushing
- **Style**: Unconventional, experimental, artistic

### 3. VETERAN (ベテラン)
- **Focus**: Traditional craftsmanship, timeless storytelling
- **Strengths**: Technical excellence, emotional depth
- **Style**: Refined, classic, emotionally impactful

### 4. AWARD_WINNER (受賞歴あり)
- **Focus**: Artistic excellence, critical acclaim
- **Strengths**: Sophisticated visuals, cultural relevance
- **Style**: Award-worthy, distinctive, culturally significant

### 5. NEWCOMER (駆け出しの新人)
- **Focus**: Fresh perspectives, viral potential
- **Strengths**: Contemporary trends, social media fluency
- **Style**: Trendy, energetic, meme-able

## Input Data

Phase 0 requires a song analysis JSON file containing:

```json
{
  "title": "Song Title",
  "artist": "Artist Name",
  "bpm": 120,
  "key": "C major",
  "duration": 180,
  "energy_profile": {
    "average": "high",
    "sections": {...}
  },
  "sections": [
    {"name": "intro", "start": 0, "end": 8},
    {"name": "verse1", "start": 8, "end": 24}
  ],
  "lyrics": {...},
  "mood": "upbeat"
}
```

## Output Data

Phase 0 produces:

### Proposals (5 total, one per director)
Each proposal includes:
- `concept_theme`: High-level creative concept
- `visual_style`: Visual aesthetic direction
- `narrative_structure`: Story/narrative approach
- `target_audience`: Intended audience
- `references`: Inspirational references

### Evaluations (5 evaluators × 5 proposals)
Each evaluation includes:
- `evaluator`: Director providing the evaluation
- `scores`: Numerical scores for each proposal (0-100)
- `feedback`: Detailed feedback for each proposal

### Winner
- `director`: Winning director
- `total_score`: Aggregated weighted score
- `proposal`: Full winning proposal
- `all_scores`: Scores for all proposals

## Usage

### Python API

```python
from phase0 import run_phase0

# Run Phase 0 with new session
results = run_phase0(
    session_id=None,  # Create new session
    analysis_path="/path/to/analysis.json",
    config_path="/home/user/test/config.json",
    mock_mode=True
)

print(f"Winner: {results['winner']['director']}")
print(f"Score: {results['winner']['total_score']:.2f}")
```

### With Existing Session

```python
from core import SharedState
from phase0 import Phase0Runner, read_json

# Load existing session
session = SharedState.load_session("session_id_here")

# Load config
config = read_json("/home/user/test/config.json")

# Create runner
runner = Phase0Runner(session, config, mock_mode=True)

# Run phase
results = runner.run("/path/to/analysis.json")
```

## Configuration

Phase 0 uses the following config settings from `config.json`:

```json
{
  "phases": {
    "0": {
      "name": "Overall Design",
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

## Mock Mode vs Real Mode

### Mock Mode (Default)
- Uses mock proposal generation
- Uses mock evaluations
- Fast execution for testing
- No external API calls

### Real Mode (Coming Soon)
- Calls Claude API with director-specific prompts
- Generates real AI-driven proposals
- Performs genuine evaluations
- Requires API credentials

## File Structure

```
phase0/
├── __init__.py          # Module exports
├── runner.py            # Phase0Runner implementation
├── README.md            # This file
└── test_phase0.py       # Test suite
```

## Error Handling

Phase 0 handles errors gracefully:

- **Missing Analysis File**: Raises `FileNotFoundError`
- **Invalid JSON**: Raises `json.JSONDecodeError`
- **Missing Prompt Template**: Raises `FileNotFoundError`
- **General Errors**: Marks phase as failed in session state

## Next Steps

After Phase 0 completes:
1. Phase 0 winner is saved to session state
2. Phase 1 (Character Design) uses the winner's concept
3. All subsequent phases build on Phase 0's foundation

## Testing

See `test_phase0.py` for examples and test cases.

## Dependencies

- Python 3.8+
- Core modules (SharedState, DirectorProfiles, CodexRunner)
- Standard library (json, logging, pathlib)

## Related Documentation

- [Core Modules README](/home/user/test/core/README.md)
- [Phase 1 README](/home/user/test/phase1/README.md)
- [CLAUDE.md](/home/user/test/CLAUDE.md)
- [Project Config](/home/user/test/config.json)
