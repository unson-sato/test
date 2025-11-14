# MV Orchestra v2.8 - Quick Start Guide

## Installation

```bash
cd /home/user/test
# No dependencies needed for core functionality yet
# Install when needed: pip install -r requirements.txt
```

## Running the Example

```bash
python3 example_usage.py
```

This will demonstrate:
- Session creation and management
- Director profile access
- Running evaluations from all 5 directors
- Score aggregation
- Data persistence

## Basic Usage

### 1. Create a Session

```python
from core import SharedState

# Create new session
session = SharedState.create_session(
    input_files={
        'mp3': 'shared-workspace/input/song.mp3',
        'lyrics': 'shared-workspace/input/lyrics.txt'
    }
)
print(f"Session ID: {session.session_id}")
```

### 2. Work with Phases

```python
# Start Phase 0
session.start_phase(0)

# Add phase data
session.set_phase_data(0, {
    'concept': 'Your creative concept here',
    'mood': 'energetic, mysterious',
    'color_palette': ['blue', 'purple', 'pink']
})

# Complete phase
session.complete_phase(0)
```

### 3. Run Evaluations

```python
from core import CodexRunner, EvaluationRequest, DirectorType

# Create evaluation request
runner = CodexRunner(mock_mode=True)
request = EvaluationRequest(
    session_id=session.session_id,
    phase_number=0,
    director_type=DirectorType.FREELANCER,
    evaluation_type="overall_design",
    context={'proposal': 'Your proposal data'}
)

# Execute evaluation
result = runner.execute_evaluation(request)
print(f"Score: {result.score}")
print(f"Feedback: {result.feedback}")
```

### 4. Get All Director Evaluations

```python
# Evaluate from all directors
all_results = []
for director_type in DirectorType:
    request = EvaluationRequest(
        session_id=session.session_id,
        phase_number=0,
        director_type=director_type,
        evaluation_type="overall_design",
        context={'proposal': 'Your proposal'}
    )
    result = runner.execute_evaluation(request)
    all_results.append(result)

# Aggregate scores
aggregated = runner.aggregate_scores(all_results)
print(f"Average Score: {aggregated['average_score']:.1f}")
```

### 5. Load Existing Session

```python
# Load by session ID
loaded = SharedState.load_session("mvorch_20251114_123456_abc123")
print(loaded.get_session_summary())
```

## Director Profiles

Access pre-configured director profiles:

```python
from core import DirectorType, get_director_profile, get_all_profiles

# Get specific director
freelancer = get_director_profile(DirectorType.FREELANCER)
print(f"Risk Tolerance: {freelancer.risk_tolerance}")
print(f"Strengths: {freelancer.strengths}")

# Get all directors
all_directors = get_all_profiles()
for director in all_directors:
    print(f"{director.name_en}: {director.description}")
```

## File Locations

- **Sessions:** `shared-workspace/sessions/<session_id>/`
- **Evaluations:** `shared-workspace/sessions/<session_id>/evaluations/`
- **Configuration:** `config.json`
- **Input Files:** `shared-workspace/input/`

## Next Steps

1. Review the full documentation in `README_MVORCH.md`
2. Read the implementation report: `IMPLEMENTATION_REPORT.md`
3. Explore the example code: `example_usage.py`
4. Check configuration options: `config.json`

## Troubleshooting

**Q: Where is my session data?**
A: Sessions are stored in `shared-workspace/sessions/<session_id>/`

**Q: How do I change director weights?**
A: Edit `config.json` → `directors.weights`

**Q: Can I add custom director profiles?**
A: Yes! Edit `core/director_profiles.py` and add new profiles

**Q: How do I switch from mock to real AI?**
A: Set `CodexRunner(mock_mode=False)` and implement real API calls in `_real_evaluation()`

## Resources

- Full README: `README_MVORCH.md`
- Implementation Report: `IMPLEMENTATION_REPORT.md`
- Example Code: `example_usage.py`
- Configuration: `config.json`
