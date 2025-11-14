# Phase 4: Generation Mode & Prompt Strategy

## Overview

Phase 4 is responsible for selecting appropriate AI video generation modes and developing detailed prompt strategies for each clip in the music video. This phase translates creative direction into technical execution plans.

## Key Responsibilities

1. **Generation Mode Selection**: Choose the most appropriate generation method for each clip (Veo2, Sora, Runway Gen-3, Pika, Traditional, or Hybrid)
2. **Prompt Engineering**: Develop detailed prompts that will guide AI generation
3. **Asset Management**: Identify and track required assets (reference images, style guides, audio segments)
4. **Consistency Planning**: Define consistency requirements across clips
5. **Budget & Timeline Estimation**: Estimate costs and production timeline

## Available Generation Modes

### Veo2 (Google)
- **Best for**: Realistic human motion, complex camera work
- **Quality**: 9/10
- **Cost**: $50-150 per clip
- **Turnaround**: 1-3 days

### Sora (OpenAI)
- **Best for**: Cinematic quality, longer clips (up to 20s)
- **Quality**: 10/10
- **Cost**: $100-300 per clip
- **Turnaround**: 2-5 days

### Runway Gen-3
- **Best for**: Fast iteration, experimental visuals
- **Quality**: 7/10
- **Cost**: $20-60 per clip
- **Turnaround**: 12-48 hours

### Pika
- **Best for**: Stylized anime/cartoon aesthetics
- **Quality**: 7/10
- **Cost**: $15-50 per clip
- **Turnaround**: 12-36 hours

### Traditional Shooting
- **Best for**: High-budget productions, character performances
- **Quality**: 10/10
- **Cost**: $500-5000+ per clip
- **Turnaround**: 1-4 weeks

### Hybrid Approach
- **Best for**: Balance of quality and cost optimization
- **Quality**: 9/10
- **Cost**: $100-1000 per clip
- **Turnaround**: 1-3 weeks

## Input Data

Phase 4 requires data from all previous phases:

- **Phase 0**: Overall creative direction, color palette, mood
- **Phase 1**: Character designs and visual identity
- **Phase 2**: Section-by-section direction (intro, verse, chorus, etc.)
- **Phase 3**: Clip division with timing and descriptions

## Output Data

Phase 4 produces:

```json
{
  "proposals": [
    {
      "director": "corporate",
      "generation_strategies": [
        {
          "clip_id": "clip_001",
          "generation_mode": "veo2",
          "prompt_template": {...},
          "prompt_strategy": "...",
          "assets_required": [...],
          "consistency_requirements": {...},
          "variance_params": {...}
        }
      ],
      "overall_strategy": "...",
      "budget_estimate": {...},
      "timeline_estimate": "..."
    }
  ],
  "evaluations": [...],
  "winner": {
    "director": "corporate",
    "total_score": 85.5,
    "proposal": {...}
  },
  "asset_pipeline": {...}
}
```

## Module Structure

### `runner.py`
Main orchestrator for Phase 4. Manages the multi-director competition and winner selection.

**Key Classes:**
- `Phase4Runner`: Main runner class

**Key Functions:**
- `run_phase4(session_id, mock_mode)`: Entry point for Phase 4

### `generation_modes.py`
Defines available video generation modes and their specifications.

**Key Classes:**
- `GenerationMode`: Enum of available modes
- `GenerationModeSpec`: Detailed specification for each mode

**Key Functions:**
- `get_mode_spec(mode)`: Get specification for a mode
- `recommend_mode(clip_type, budget_level, quality_priority)`: Recommend mode based on requirements

### `prompt_builder.py`
Utilities for building and managing generation prompts.

**Key Classes:**
- `PromptTemplate`: Template for video generation prompts
- `PromptBuilder`: Builder pattern for constructing prompts

**Key Functions:**
- `create_character_prompt(...)`: Create character-focused prompts
- `create_establishing_prompt(...)`: Create establishing shot prompts
- `create_transition_prompt(...)`: Create transition prompts
- `enhance_prompt_for_consistency(...)`: Add consistency parameters

### `asset_manager.py`
Manages assets required for generation.

**Key Classes:**
- `AssetManager`: Central asset management
- `Asset`: Individual asset representation
- `ClipAssets`: Assets for a specific clip

**Key Functions:**
- `create_character_consistency_asset(...)`: Create character reference
- `create_style_guide_asset(...)`: Create style guide
- `create_audio_segment_asset(...)`: Create audio segment reference

## Usage Example

```python
from phase4 import run_phase4

# Run Phase 4 for a session
results = run_phase4(session_id="mvorch_20250114_abc123", mock_mode=True)

# Access winning strategy
winner = results['winner']
print(f"Winner: {winner['director']}")
print(f"Score: {winner['total_score']}")

# Access generation strategies
for strategy in winner['proposal']['generation_strategies']:
    print(f"Clip {strategy['clip_id']}: {strategy['generation_mode']}")
    print(f"  Prompt: {strategy['prompt_template']['full_prompt']}")
    print(f"  Cost: {strategy['estimated_cost']}")
```

## Director Perspectives

### Corporate Director
- Prioritizes brand safety and reliability
- Prefers **Traditional** or **Hybrid** approaches
- Uses detailed prompts for control
- Conservative tool choices

### Freelancer Director
- Experiments with cutting-edge AI
- Willing to use **Veo2**, **Sora**, **Runway**
- Creative prompt strategies
- Higher risk tolerance

### Veteran Director
- Favors traditional methods
- Uses **Traditional** or **Hybrid** extensively
- Emphasizes timeless craftsmanship
- Translates cinematography principles to AI

### Award Winner Director
- Balances artistic excellence with innovation
- Strategic use of all modes
- Sophisticated prompt engineering
- Quality-first approach

### Newcomer Director
- Embraces experimental AI tools
- Heavy use of **Veo2**, **Runway**, **Pika**
- Bold, unconventional strategies
- Fresh perspectives on prompt design

## Best Practices

1. **Mode Selection**
   - Use Traditional/Hybrid for character performances
   - Use AI for establishing shots and transitions
   - Consider budget constraints
   - Prioritize consistency for character-focused clips

2. **Prompt Engineering**
   - Be specific and detailed
   - Include technical specifications (camera, lighting)
   - Use negative prompts to avoid unwanted elements
   - Add quality enhancement tags

3. **Asset Management**
   - Track all required assets
   - Create character consistency references early
   - Maintain style guides
   - Plan for lip sync audio if needed

4. **Consistency**
   - Define consistency requirements per clip
   - Use reference images for characters
   - Maintain visual coherence across clips
   - Balance consistency with creative variance

## Testing

See `test_phase4.py` for testing examples.

```bash
# Run Phase 4 tests
python -m pytest phase4/test_phase4.py -v
```

## Related Phases

- **Phase 3** (Clip Division): Provides clip timing and descriptions
- **Phase 5** (Claude Review): Optional review and refinement of strategies

## Notes

- Phase 4 is computationally intensive due to multi-director evaluation
- Mock mode is recommended for development and testing
- Real API costs can add up quickly; use cost estimation features
- Asset pipeline helps ensure all necessary resources are identified before generation

## Version

Phase 4 Module v2.8 - Part of MV Orchestra v2.8
