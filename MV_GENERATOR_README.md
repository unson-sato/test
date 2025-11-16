# 🎬 Music Video Shot Generator

AI-powered music video shot list generation using comprehensive cinematography grammar.

## Overview

This tool generates detailed, professional shot lists for music videos by combining:
- **Comprehensive shot grammar** - 19 categories of cinematography knowledge
- **AI generation** - Claude/GPT-4 powered intelligent shot selection
- **Customizable constraints** - Budget, equipment, environment, performers
- **Multiple output formats** - JSON, Markdown, CSV

## Features

- ✨ **AI-Powered Generation**: Uses Anthropic Claude or OpenAI GPT-4 to intelligently compose shot sequences
- 🎯 **Context-Aware**: Matches shots to song mood, BPM, structure, and emotional arc
- 🎨 **Comprehensive Grammar**: 19 categories including lenses, movements, lighting, composition, and more
- 📊 **Multiple Outputs**: JSON for APIs, Markdown for humans, CSV for spreadsheets
- 🛠️ **Flexible**: Works with or without AI (falls back to sample generation)
- 🔌 **Pluggable**: Supports multiple AI providers (Anthropic, OpenAI, or mock)

## Installation

### Requirements

- Python 3.8+
- (Optional) Anthropic API key for Claude integration
- (Optional) OpenAI API key for GPT integration

### Install Dependencies

```bash
# For Anthropic Claude (recommended)
pip install anthropic

# For OpenAI GPT
pip install openai

# Both are optional - tool works without AI in sample mode
```

### Setup API Keys

```bash
# For Anthropic Claude
export ANTHROPIC_API_KEY="your-api-key-here"

# For OpenAI
export OPENAI_API_KEY="your-api-key-here"
```

## Quick Start

### Basic Usage

```bash
python3 mv_shot_generator.py \
  --title "Midnight Runner" \
  --artist "The Echoes" \
  --genre "Alternative Rock" \
  --bpm 120 \
  --duration 180 \
  --structure "intro,verse,chorus,verse,chorus,bridge,chorus" \
  --mood "melancholy,urban,introspective"
```

### With AI Generation (Anthropic Claude)

```bash
# Make sure ANTHROPIC_API_KEY is set
python3 mv_shot_generator.py \
  --title "Neon Dreams" \
  --artist "Synthwave City" \
  --genre "Synthwave" \
  --bpm 128 \
  --duration 200 \
  --structure "intro,verse,chorus,verse,chorus,bridge,chorus,outro" \
  --mood "nostalgic,futuristic,energetic" \
  --budget high \
  --environment "urban,night,neon" \
  --performers 1 \
  --equipment "gimbal,drone,crane" \
  --ai-provider anthropic \
  --output-format markdown \
  --output-file my_video_shots.md
```

### Using Mock AI (for testing)

```bash
python3 mv_shot_generator.py \
  --title "Test Song" \
  --artist "Test Artist" \
  --genre "Pop" \
  --bpm 120 \
  --duration 180 \
  --structure "intro,verse,chorus" \
  --mood "happy" \
  --ai-provider mock \
  --output-format json
```

### Without AI (Sample Mode)

```bash
python3 mv_shot_generator.py \
  --title "Sample Song" \
  --artist "Artist" \
  --genre "Rock" \
  --bpm 120 \
  --duration 180 \
  --structure "intro,verse,chorus" \
  --mood "energetic" \
  --no-ai
```

## Command Line Options

### Required Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--title` | Song title | "Midnight Runner" |
| `--artist` | Artist name | "The Echoes" |
| `--genre` | Music genre | "Alternative Rock" |
| `--bpm` | Beats per minute | 120 |
| `--duration` | Song length in seconds | 180 |
| `--structure` | Song sections (comma-separated) | "intro,verse,chorus,verse,chorus,bridge,chorus" |
| `--mood` | Mood/emotions (comma-separated) | "melancholy,urban,introspective" |

### Production Constraints

| Argument | Default | Description |
|----------|---------|-------------|
| `--budget` | medium | Budget level: low, medium, high |
| `--environment` | urban,night | Environment types (comma-separated) |
| `--performers` | 1 | Number of performers |
| `--performer-type` | solo | Type: solo, duo, group, ensemble |
| `--equipment` | gimbal,drone | Available equipment (comma-separated) |

### AI Options

| Argument | Default | Description |
|----------|---------|-------------|
| `--ai-provider` | anthropic | AI provider: anthropic, openai, mock |
| `--no-ai` | False | Disable AI, use sample generation |
| `--show-prompt` | False | Show the prompt sent to AI |

### Output Options

| Argument | Default | Description |
|----------|---------|-------------|
| `--output-format` | markdown | Format: json, markdown, csv |
| `--output-file` | stdout | Output file path |
| `--grammar-file` | shot-grammar.json | Path to grammar file |

## Shot Grammar

The system uses a comprehensive cinematography grammar with 19 categories:

1. **lens_types** - 7 types (ultra_wide, wide, standard, portrait, telephoto, macro, anamorphic)
2. **shot_sizes** - 8 sizes (EWS, WS, MWS, MS, MCU, CU, ECU, insert)
3. **camera_movements** - 17 movements (static, pan, tilt, dolly, crane, drone, etc.)
4. **movement_intensity_grid** - 5 intensity levels (calm to extreme)
5. **composition_rules** - 12 rules (rule of thirds, negative space, symmetry, etc.)
6. **lighting_archetypes** - 12 lighting setups
7. **editing_transitions** - 15 transition types
8. **environment_modifiers** - 16 environment types
9. **shot_function_roles** - 10 shot purposes
10. **scene_templates** - 10 pre-designed scene types
11. **fx_and_treatments** - 16 visual effects
12. **multi_actor_patterns** - 10 patterns for multiple performers
13. **camera_motion_grammar** - 10 motion patterns with emotional meaning
14. **emotional_camera_mapping** - 10 emotion-to-camera mappings
15. **scene_archetypes** - 10 archetypal scenes
16. **temporal_techniques** - 10 time manipulation techniques
17. **symbolic_motifs** - 8 symbolic visual elements
18. **scene_transition_logic** - 7 transition rules
19. **camera_choreo_sync** - Camera-choreography synchronization patterns

All grammar details are in `shot-grammar.json`.

## Output Formats

### JSON Format

```json
[
  {
    "shot_number": 1,
    "section": "intro",
    "duration_seconds": 5.0,
    "shot_size": "extreme_wide_shot",
    "lens_type": "wide",
    "camera_movement": "drone_aerial",
    "composition": "rule_of_thirds",
    "lighting": "blue_hour_melancholy",
    "emotional_tone": "mysterious",
    "description": "Aerial establishing shot of the city at twilight",
    "technical_notes": "Use ND filter for proper exposure"
  }
]
```

### Markdown Format

```markdown
# Music Video Shot List

## Song Information
- **Title**: Midnight Runner
- **Artist**: The Echoes
...

## Shot List

### INTRO

#### Shot 1
- **Duration**: 5.0s
- **Shot Size**: extreme_wide_shot
- **Lens**: wide
- **Movement**: drone_aerial
...
```

### CSV Format

Standard CSV with all shot fields, importable into spreadsheets.

## Examples

### Example 1: Melancholic Urban Night Video

```bash
python3 mv_shot_generator.py \
  --title "City Lights" \
  --artist "Midnight Collective" \
  --genre "Electronic" \
  --bpm 90 \
  --duration 240 \
  --structure "intro,verse,chorus,verse,chorus,bridge,chorus,outro" \
  --mood "melancholy,urban,introspective,lonely" \
  --budget medium \
  --environment "urban,night,neon,rain" \
  --performers 1 \
  --performer-type solo \
  --equipment "gimbal,drone" \
  --output-format markdown \
  --output-file city_lights_shotlist.md
```

### Example 2: High-Energy Dance Video

```bash
python3 mv_shot_generator.py \
  --title "Electric Pulse" \
  --artist "The Movement" \
  --genre "EDM" \
  --bpm 128 \
  --duration 180 \
  --structure "intro,buildup,drop,verse,buildup,drop,outro" \
  --mood "energetic,euphoric,powerful" \
  --budget high \
  --environment "warehouse,studio,lights" \
  --performers 8 \
  --performer-type ensemble \
  --equipment "gimbal,crane,steadicam,strobe" \
  --output-format json \
  --output-file electric_pulse_shots.json
```

### Example 3: Intimate Acoustic Performance

```bash
python3 mv_shot_generator.py \
  --title "Whisper" \
  --artist "Sarah Rivers" \
  --genre "Folk" \
  --bpm 72 \
  --duration 210 \
  --structure "intro,verse,chorus,verse,chorus,bridge,chorus" \
  --mood "intimate,vulnerable,peaceful,nostalgic" \
  --budget low \
  --environment "bedroom,window,natural_light" \
  --performers 1 \
  --performer-type solo \
  --equipment "gimbal" \
  --output-format markdown \
  --output-file whisper_shots.md
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│  mv_shot_generator.py (Main CLI)                │
│  - Parses arguments                             │
│  - Orchestrates generation                      │
└──────────────┬──────────────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
┌──────────────┐  ┌──────────────────┐
│ Shot Grammar │  │  AI Integration  │
│    Loader    │  │  (ai_integration.py) │
│              │  │  - Anthropic     │
│ Reads JSON   │  │  - OpenAI        │
│ Provides     │  │  - Mock          │
│ Context      │  └──────────────────┘
└──────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│  Prompt Builder                      │
│  - Constructs AI prompt              │
│  - Includes relevant grammar         │
│  - Formats requirements              │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│  Shot List Generator                 │
│  - Calls AI or generates samples     │
│  - Parses responses                  │
│  - Validates shot data               │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│  Output Formatter                    │
│  - JSON / Markdown / CSV             │
│  - File or stdout                    │
└──────────────────────────────────────┘
```

## API Integration

### Using Anthropic Claude

```python
from ai_integration import get_ai_provider

# Get provider (reads ANTHROPIC_API_KEY from environment)
provider = get_ai_provider("anthropic")

# Generate
response = provider.generate_shot_list(prompt)
```

### Using OpenAI

```python
from ai_integration import get_ai_provider

# Get provider (reads OPENAI_API_KEY from environment)
provider = get_ai_provider("openai")

# Generate
response = provider.generate_shot_list(prompt)
```

### Programmatic Usage

```python
from mv_shot_generator import (
    ShotGrammarLoader,
    ShotListGenerator,
    SongInfo,
    ProductionConstraints
)

# Load grammar
grammar = ShotGrammarLoader("shot-grammar.json")

# Create generator
generator = ShotListGenerator(
    grammar,
    ai_provider="anthropic",
    use_ai=True
)

# Define song
song = SongInfo(
    title="My Song",
    artist="Artist Name",
    genre="Pop",
    bpm=120,
    duration_seconds=180,
    structure=["intro", "verse", "chorus"],
    mood=["happy", "energetic"]
)

# Define constraints
constraints = ProductionConstraints(
    budget_level="medium",
    environment=["studio"],
    num_performers=1,
    performer_type="solo",
    available_equipment=["gimbal"]
)

# Generate
shots = generator.generate(song, constraints)

# Use shots
for shot in shots:
    print(f"Shot {shot.shot_number}: {shot.description}")
```

## Troubleshooting

### "AI integration not available"

Install the required package:
```bash
pip install anthropic  # for Anthropic
# or
pip install openai     # for OpenAI
```

### "API key not found"

Set the environment variable:
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### AI generation fails

The tool automatically falls back to sample generation. Use `--show-prompt` to debug:
```bash
python3 mv_shot_generator.py ... --show-prompt
```

### Want more control?

- Modify `shot-grammar.json` to customize the vocabulary
- Edit `PromptBuilder` in `mv_shot_generator.py` to change how prompts are constructed
- Adjust temperature in `ai_integration.py` for more/less creative outputs

## Contributing

To extend the grammar:

1. Edit `shot-grammar.json`
2. Add new categories or expand existing ones
3. Follow the existing structure
4. Test with `--show-prompt` to see how it affects generation

## License

MIT

## Credits

Created with Claude Code 🤖

---

**Pro Tip**: Start with `--ai-provider mock` to understand the output format, then switch to real AI providers for production use.
