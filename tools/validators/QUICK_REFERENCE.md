# Validation Tools - Quick Reference

## Command-Line Usage

```bash
# Phase 3 Validation
python3 tools/validators/validate_clip_division.py <session_id>

# Phase 4 Validation
python3 tools/validators/validate_phase4_strategies.py <session_id>
```

## Python Usage

```python
from tools.validators import validate_clip_division, validate_phase4_strategies

# Validate Phase 3
report = validate_clip_division(session_id)

# Validate Phase 4
report = validate_phase4_strategies(session_id)

# Check status
if report['summary']['overall_status'] == 'PASS':
    print("Validation passed!")
```

## Phase 3 Checks (8 total)

| Check | Critical | Description |
|-------|----------|-------------|
| Clip ID Uniqueness | ✓ | All IDs unique |
| Timing Consistency | ✓ | Valid start/end/duration |
| Section Coverage | - | Clips assigned to sections |
| Timeline Coverage | - | Full timeline covered |
| Beat Alignment | - | Clips align to beats |
| Base Allocation | - | Budget allocated |
| Creative Adjustments | - | Adjustments valid |
| Duration Sanity | - | Reasonable durations |

## Phase 4 Checks (8 total)

| Check | Critical | Description |
|-------|----------|-------------|
| Strategy Completeness | ✓ | All clips covered |
| Generation Mode Validity | ✓ | Valid modes only |
| Prompt Quality | - | Well-formed prompts |
| Asset Requirements | - | Assets specified |
| Consistency Requirements | - | Consistency params set |
| Variance Parameters | - | Valid variance values |
| Creative Adjustments | - | Adjustments integrated |
| Budget/Timeline | - | Estimates present |

## Valid Generation Modes

- `veo2` - Google Veo 2
- `sora` - OpenAI Sora
- `runway_gen3` - Runway Gen-3
- `pika` - Pika Labs
- `traditional` - Traditional shooting
- `hybrid` - Hybrid approach
- `image_to_video` - I2V generation
- `video_to_video` - V2V generation

## Output Files

- **Phase 3:** `<session_dir>/validation_clip_division.json`
- **Phase 4:** `<session_dir>/validation_phase4_strategies.json`

## Exit Codes

- `0` - PASS (all checks passed)
- `1` - FAIL (one or more checks failed)

## Integration Example

```python
# After running a phase
from phase3.runner import run_phase3
from tools.validators import validate_clip_division

# Run phase
results = run_phase3(session_id)

# Validate
report = validate_clip_division(session_id)

# Check critical failures
if report['summary']['failed_checks'] > 0:
    for check, result in report['validation_results'].items():
        if not result['passed']:
            print(f"Failed: {check} - {result['message']}")
```

## Common Issues

### Session Not Found
```bash
# Check session exists
ls shared-workspace/sessions/ | grep <session_id>
```

### No Clips Found
```bash
# Check Phase 3 status
python3 -c "from core import SharedState; print(SharedState.load_session('<session_id>').get_phase_data(3).status)"
```

### Missing Beat Data
- Beat alignment check will skip with warning
- Ensure analysis.json has "beats" field

## Configuration

Edit validator files to adjust:

```python
# validate_clip_division.py
gap_tolerance = 0.5        # Timeline gap tolerance
beat_tolerance = 0.3       # Beat alignment tolerance
min_duration = 0.5         # Minimum clip duration
max_duration = 30.0        # Maximum clip duration

# validate_phase4_strategies.py
MIN_PROMPT_LENGTH = 20     # Minimum prompt chars
MAX_PROMPT_LENGTH = 1000   # Maximum prompt chars
```

## See Also

- **README.md** - Complete documentation
- **integration_example.py** - Integration patterns
- **VALIDATION_TOOLS_REPORT.md** - Implementation details
