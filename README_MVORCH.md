# MV Orchestra v2.8

Multi-director AI competition system for music video generation.

## Overview

MV Orchestra v2.8 is a sophisticated framework for generating music videos through a multi-director AI competition approach. Five different AI "directors" with distinct personalities and creative approaches compete and collaborate to create compelling music video concepts.

## Core Concept

The system simulates a creative competition where five directors evaluate and propose ideas:

1. **Corporate Creator (会社員クリエイター)** - Safe, commercial approach
2. **Freelancer (フリーランス)** - Experimental, boundary-pushing
3. **Veteran (ベテラン)** - Traditional craftsmanship
4. **Award Winner (受賞歴あり)** - Artistic excellence
5. **Newcomer (駆け出しの新人)** - Fresh, bold ideas

## Project Structure

```
/home/user/test/
├── core/                      # Core functionality
│   ├── shared_state.py       # Session state management
│   ├── director_profiles.py  # Director personality definitions
│   ├── codex_runner.py       # AI evaluation execution
│   ├── utils.py              # Utility functions
│   └── __init__.py           # Module exports
├── phase0/                    # Phase 0: Overall design
├── phase1/                    # Phase 1: Character design
├── phase2/                    # Phase 2: Section direction
├── phase3/                    # Phase 3: Clip division
├── phase4/                    # Phase 4: Generation strategy
├── phase5/                    # Phase 5: Real Claude review (optional)
├── tools/
│   ├── optimization/          # Optimization tools
│   └── validators/            # Validation tools
├── shared-workspace/
│   ├── input/                 # Input files (MP3, lyrics, analysis)
│   └── sessions/              # Session data
├── .claude/
│   └── prompts_v2/
│       └── evaluations/       # Evaluation prompt templates
├── config.json                # Configuration settings
├── requirements.txt           # Python dependencies
└── .gitignore                # Git ignore rules
```

## The 6-Phase Pipeline

### Phase 0: Overall Design
High-level creative direction and concept development for the music video.

### Phase 1: Character Design
Character concepts, visual identity, and persona development.

### Phase 2: Section Direction
Direction for individual music sections (intro, verse, chorus, bridge, etc.).

### Phase 3: Clip Division
Breaking down sections into individual clips/shots with timing.

### Phase 4: Generation Strategy
Technical parameters and generation approach for each clip.

### Phase 5: Real Claude Review (Optional)
Final quality control review by actual Claude AI.

## Quick Start

### Installation

```bash
# Clone the repository
cd /home/user/test

# Install dependencies (when needed)
pip install -r requirements.txt
```

### Basic Usage

```python
from core import SharedState, DirectorType, CodexRunner, EvaluationRequest

# Create a new session
session = SharedState.create_session(
    input_files={
        'mp3': 'shared-workspace/input/song.mp3',
        'lyrics': 'shared-workspace/input/lyrics.txt'
    }
)

# Start Phase 0
session.start_phase(0)

# Set some design data
session.set_phase_data(0, {
    'concept': 'Futuristic cyberpunk narrative',
    'mood': 'energetic, mysterious',
    'color_palette': ['neon blue', 'deep purple', 'electric pink']
})

# Run an evaluation
runner = CodexRunner(mock_mode=True)
request = EvaluationRequest(
    session_id=session.session_id,
    phase_number=0,
    director_type=DirectorType.FREELANCER,
    evaluation_type="overall_design",
    context={'proposal': 'Concept details here...'}
)

result = runner.execute_evaluation(request)
print(f"Score: {result.score}")
print(f"Feedback: {result.feedback}")

# Complete the phase
session.complete_phase(0)
```

## Director Profiles

Each director has unique characteristics that influence their evaluations:

### Corporate Creator
- **Risk Tolerance:** Low (0.3)
- **Commercial Focus:** High (0.9)
- **Artistic Focus:** Medium (0.4)
- **Innovation Focus:** Medium (0.4)

### Freelancer
- **Risk Tolerance:** High (0.8)
- **Commercial Focus:** Medium (0.4)
- **Artistic Focus:** High (0.8)
- **Innovation Focus:** Very High (0.9)

### Veteran
- **Risk Tolerance:** Medium (0.4)
- **Commercial Focus:** Medium (0.6)
- **Artistic Focus:** High (0.7)
- **Innovation Focus:** Low (0.3)

### Award Winner
- **Risk Tolerance:** Medium-High (0.6)
- **Commercial Focus:** Medium (0.6)
- **Artistic Focus:** Very High (0.9)
- **Innovation Focus:** High (0.7)

### Newcomer
- **Risk Tolerance:** Very High (0.9)
- **Commercial Focus:** Medium (0.5)
- **Artistic Focus:** Medium-High (0.6)
- **Innovation Focus:** Very High (0.9)

## Configuration

Edit `config.json` to customize:
- Phase settings and timeouts
- Director weights and enabled directors
- Evaluation criteria and scoring
- Optimization parameters
- File paths and generation settings

## Development Status

**Current Version:** 2.8 (Foundation)

This is the foundational infrastructure implementation. Future waves will add:
- Phase-specific implementations (Wave 2)
- Audio analysis integration
- Visual generation pipelines
- Real AI integration
- Optimization algorithms
- Web UI / CLI tools

## License

[To be determined]

## Contributing

[To be determined]

---

**Last Updated:** 2025-11-14
