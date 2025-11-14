# MV Orchestra v2.8 - Validation Tools

Technical validators for ensuring quality and correctness of MV Orchestra phase outputs.

## Overview

The validation tools provide automated quality checks for different phases of the MV Orchestra pipeline:

- **validate_clip_division.py** - Validates Phase 3 clip division output
- **validate_phase4_strategies.py** - Validates Phase 4 generation strategies
- **validation_utils.py** - Shared utilities for validators

## Installation

No additional dependencies required beyond the core MV Orchestra requirements.

## Usage

### Standalone Validation

Run validators directly from the command line:

```bash
# Validate Phase 3 clip division
python3 tools/validators/validate_clip_division.py <session_id>

# Validate Phase 4 generation strategies
python3 tools/validators/validate_phase4_strategies.py <session_id>
```

### Programmatic Usage

Import and use in Python code:

```python
from tools.validators.validate_clip_division import validate_clip_division
from tools.validators.validate_phase4_strategies import validate_phase4_strategies

# Validate Phase 3
report = validate_clip_division("mvorch_20251114_163545_d1c7c8d0")
if report['summary']['overall_status'] == "PASS":
    print("Phase 3 validation passed!")

# Validate Phase 4
report = validate_phase4_strategies("mvorch_20251114_163545_d1c7c8d0")
```

### Integration with run_all_phases.py

Add automatic validation after each phase:

```python
from tools.validators.validate_clip_division import validate_clip_division
from tools.validators.validate_phase4_strategies import validate_phase4_strategies

# After Phase 3
validation_results = validate_clip_division(session_id)
if not validation_results["summary"]["overall_status"] == "PASS":
    logger.warning("Phase 3 validation found issues")

# After Phase 4
validation_results = validate_phase4_strategies(session_id)
```

## Validators

### validate_clip_division.py

Validates Phase 3 clip division output.

**Checks:**

1. **Clip ID Uniqueness** - All clip IDs are unique
2. **Timing Consistency** - start_time < end_time, duration matches
3. **Section Coverage** - All clips assigned to valid sections
4. **Timeline Coverage** - Full timeline covered without gaps/overlaps
5. **Beat Alignment** - Clips align to beat boundaries
6. **Base Allocation** - All clips have base_allocation field
7. **Creative Adjustments** - Creative adjustments properly structured
8. **Duration Sanity** - Durations within reasonable bounds (0.5s - 30s)

**Output:**

- Console report with check results
- JSON report saved to `<session_dir>/validation_clip_division.json`
- Exit code 0 (pass) or 1 (fail)

**Example Output:**

```
======================================================================
=== MV Orchestra v2.8 - Phase 3 Clip Division Validation ===
======================================================================
Session: mvorch_20251114_163545_d1c7c8d0
Total Clips: 69

[✓] Clip ID Uniqueness: PASS
    All clip IDs are unique

[✓] Timing Consistency: PASS
    All clip timings are consistent

[✓] Section Coverage: PASS
    All clips properly assigned to sections

[✓] Timeline Coverage: PASS (99.8%)
    Timeline fully covered

[!] Beat Alignment: PASS (94.2%)
    94% of clips aligned to beats
    ! Misaligned: clip_023, clip_045

[✓] Base Allocation: PASS
    All clips have base_allocation

[✓] Creative Adjustments: PASS
    15 clips have creative adjustments

[✓] Duration Sanity: PASS
    Min: 1.2s, Max: 5.8s, Avg: 2.61s

======================================================================
Summary
======================================================================
Overall Status: PASS
Passed: 8/8 checks
Warnings: 2

Validation complete. Report saved to:
shared-workspace/sessions/mvorch_20251114_163545_d1c7c8d0/validation_clip_division.json
```

### validate_phase4_strategies.py

Validates Phase 4 generation strategies output.

**Checks:**

1. **Strategy Completeness** - All Phase 3 clips have strategies
2. **Generation Mode Validity** - All modes are valid
3. **Prompt Quality** - Prompts are non-empty and reasonable length
4. **Asset Requirements** - Required assets specified
5. **Consistency Requirements** - Consistency fields present and valid
6. **Variance Parameters** - Parameters within valid ranges (0.0-1.0)
7. **Creative Adjustments** - Adjustments properly integrated
8. **Budget/Timeline Estimates** - Estimates present and reasonable

**Valid Generation Modes:**

- `veo2` - Google Veo 2
- `sora` - OpenAI Sora
- `runway_gen3` - Runway Gen-3
- `pika` - Pika Labs
- `traditional` - Traditional shooting
- `hybrid` - Hybrid approach
- `image_to_video` - I2V generation
- `video_to_video` - V2V generation

**Output:**

- Console report with check results
- JSON report saved to `<session_dir>/validation_phase4_strategies.json`
- Exit code 0 (pass) or 1 (fail)

## Output Format

### Validation Report JSON

```json
{
  "session_id": "mvorch_20251114_163545_d1c7c8d0",
  "validated_at": "2025-11-14T11:00:00.000000",
  "phase": 3,
  "total_clips": 69,
  "validation_results": {
    "clip_id_uniqueness": {
      "passed": true,
      "duplicate_ids": [],
      "message": "All clip IDs are unique"
    },
    "timing_consistency": {
      "passed": true,
      "issues": [],
      "message": "All clip timings are consistent"
    },
    ...
  },
  "summary": {
    "total_checks": 8,
    "passed_checks": 8,
    "failed_checks": 0,
    "warnings": 2,
    "overall_status": "PASS"
  }
}
```

## Validation Utilities

The `validation_utils.py` module provides shared functionality:

### Functions

- `print_header()` - Print formatted header
- `print_check()` - Print formatted check result
- `print_summary()` - Print validation summary
- `validate_unique_ids()` - Check ID uniqueness
- `validate_timing_consistency()` - Check timing values
- `validate_timeline_coverage()` - Check timeline coverage
- `validate_duration_sanity()` - Check duration ranges
- `parse_cost_range()` - Parse cost strings
- `load_analysis_metadata()` - Load analysis.json metadata
- `extract_clips_from_phase3()` - Extract clips from Phase 3 data
- `build_validation_summary()` - Build summary from results

## Exit Codes

- `0` - Validation passed (all checks passed)
- `1` - Validation failed (one or more checks failed)

## Configuration

### Tolerances and Thresholds

Edit the validator files to adjust thresholds:

**validate_clip_division.py:**
```python
gap_tolerance = 0.5        # Max gap size (seconds)
beat_tolerance = 0.3       # Beat alignment tolerance (seconds)
min_duration = 0.5         # Minimum clip duration
max_duration = 30.0        # Maximum clip duration
```

**validate_phase4_strategies.py:**
```python
MIN_PROMPT_LENGTH = 20     # Minimum prompt characters
MAX_PROMPT_LENGTH = 1000   # Maximum prompt characters
```

## Known Limitations

1. **Beat Alignment**: Requires beat data in analysis.json. If not available, check is skipped.

2. **Section Validation**: Requires section definitions in analysis.json. If not available, only checks for presence of section field.

3. **Generation Mode Names**: Case-insensitive matching, normalizes spaces/dashes to underscores.

4. **Creative Adjustments**: Optional field - presence is checked but not required.

5. **Budget Parsing**: Simple string parsing - may not handle all cost formats.

## Error Handling

Validators handle common errors gracefully:

- Missing session → Exit with error message
- Incomplete phase data → Warning + continue
- Missing analysis.json → Use defaults + warning
- Empty clip lists → Error and exit

## Development

### Adding New Validators

1. Create new validator file in `tools/validators/`
2. Import shared utilities from `validation_utils.py`
3. Implement validation checks
4. Follow existing patterns for output formatting
5. Add tests in `test_*.py`
6. Update this README

### Testing

Run validator tests:

```bash
python3 -m pytest tools/validators/test_validate_clip_division.py
python3 -m pytest tools/validators/test_validate_phase4_strategies.py
```

## Troubleshooting

### "Session not found" error

Ensure the session ID is correct and the session exists:

```bash
ls shared-workspace/sessions/ | grep <session_id>
```

### "No clips found" error

Check that Phase 3 completed successfully:

```bash
python3 -c "from core import SharedState; s = SharedState.load_session('<session_id>'); print(s.get_phase_data(3).status)"
```

### Validation report not saved

Ensure session directory has write permissions:

```bash
ls -la shared-workspace/sessions/<session_id>/
```

## Integration Examples

### CI/CD Pipeline

```yaml
# .github/workflows/validate.yml
- name: Validate Phase 3
  run: |
    python3 tools/validators/validate_clip_division.py $SESSION_ID

- name: Validate Phase 4
  run: |
    python3 tools/validators/validate_phase4_strategies.py $SESSION_ID
```

### Pre-Phase Hook

```python
def validate_before_next_phase(session_id: str, phase: int) -> bool:
    """Validate phase before proceeding to next phase."""
    if phase == 3:
        result = validate_clip_division(session_id)
    elif phase == 4:
        result = validate_phase4_strategies(session_id)
    else:
        return True

    return result['summary']['overall_status'] == 'PASS'
```

## Contributing

When adding new validation checks:

1. Add check function to appropriate validator
2. Add to validation_results dict
3. Call print_check() for console output
4. Update summary builder to include new check
5. Add test cases
6. Document in this README

## License

Part of the MV Orchestra v2.8 project.

## Support

For issues or questions:
- Check existing session data structure
- Review validation report JSON
- Consult CLAUDE.md for project guidelines
