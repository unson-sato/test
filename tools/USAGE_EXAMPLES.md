# Audio Analysis Tools - Usage Examples

This document provides practical examples for using the MV Orchestra v2.8 audio analysis tools.

## Prerequisites

### System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Verify installation
ffmpeg -version
ffprobe -version
```

### Optional Dependencies (for better alignment)

```bash
# For aeneas forced alignment
sudo apt-get install espeak libespeak-dev
pip install aeneas

# For Whisper alignment (requires PyTorch)
pip install git+https://github.com/openai/whisper.git
```

## Basic Workflow

### Step 1: Prepare Your Files

Organize your audio and lyrics files:

```
my-song/
├── audio.mp3          # Your music file
└── lyrics.txt         # Plain text lyrics (one line per phrase)
```

**Example lyrics.txt:**
```
In the neon glow of city lights
I'm searching for a sign tonight
Electric dreams and endless nights
Your memory shining bright
```

### Step 2: Generate Initial Analysis

```bash
# Basic analysis
python3 tools/build_analysis.py \
    --mp3 my-song/audio.mp3 \
    --lyrics my-song/lyrics.txt \
    --output my-song/analysis.json

# With metadata
python3 tools/build_analysis.py \
    --mp3 my-song/audio.mp3 \
    --lyrics my-song/lyrics.txt \
    --output my-song/analysis.json \
    --title "Electric Dreams" \
    --artist "Neon Pulse"
```

**Output:** `analysis.json` with sections, beats, energy profile, and lyrics (without timestamps)

### Step 3: Generate Lyrics Timestamps (SRC)

```bash
# Auto mode (recommended - tries aeneas, falls back to heuristic)
python3 tools/build_src.py \
    --mp3 my-song/audio.mp3 \
    --lyrics my-song/lyrics.txt \
    --output my-song/src.json

# Force heuristic mode (no dependencies)
python3 tools/build_src.py \
    --mp3 my-song/audio.mp3 \
    --lyrics my-song/lyrics.txt \
    --output my-song/src.json \
    --mode heuristic

# Use aeneas for better quality (requires aeneas installed)
python3 tools/build_src.py \
    --mp3 my-song/audio.mp3 \
    --lyrics my-song/lyrics.txt \
    --output my-song/src.json \
    --mode aeneas

# Use Whisper (may fail in sandboxes)
python3 tools/build_src.py \
    --mp3 my-song/audio.mp3 \
    --lyrics my-song/lyrics.txt \
    --output my-song/src.json \
    --mode whisper \
    --whisper-model base
```

**Output:** `src.json` with timed lyrics

### Step 4: Merge SRC into Analysis (Optional)

Create a Python script to merge the timecodes:

```python
#!/usr/bin/env python3
"""merge_src.py - Merge SRC timecodes into analysis.json"""

import json
import sys

def merge_src(analysis_file, src_file, output_file):
    """Merge SRC timecodes into analysis."""

    # Load files
    with open(analysis_file, 'r') as f:
        analysis = json.load(f)

    with open(src_file, 'r') as f:
        src = json.load(f)

    # Update lyrics timestamps
    for i, src_line in enumerate(src['lines']):
        if i < len(analysis['lyrics']['lines']):
            analysis['lyrics']['lines'][i]['start_time'] = src_line['start_time']
            analysis['lyrics']['lines'][i]['end_time'] = src_line['end_time']

    # Save merged analysis
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"✓ Merged {src['total_lines']} lyrics timecodes")
    print(f"✓ Written to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: merge_src.py <analysis.json> <src.json> <output.json>")
        sys.exit(1)

    merge_src(sys.argv[1], sys.argv[2], sys.argv[3])
```

Run it:
```bash
python3 merge_src.py my-song/analysis.json my-song/src.json my-song/analysis_final.json
```

### Step 5: Use with MV Orchestra

```bash
python3 run_all_phases.py --analysis my-song/analysis_final.json
```

## Advanced Usage

### Batch Processing Multiple Songs

```bash
#!/bin/bash
# batch_analyze.sh - Process multiple songs

for dir in songs/*/; do
    name=$(basename "$dir")
    echo "Processing: $name"

    # Generate analysis
    python3 tools/build_analysis.py \
        --mp3 "$dir/audio.mp3" \
        --lyrics "$dir/lyrics.txt" \
        --output "$dir/analysis.json" \
        --title "$name"

    # Generate SRC
    python3 tools/build_src.py \
        --mp3 "$dir/audio.mp3" \
        --lyrics "$dir/lyrics.txt" \
        --output "$dir/src.json" \
        --mode auto

    echo "✓ Completed: $name"
done
```

### Custom BPM Detection

For more accurate BPM detection, integrate librosa:

```python
import librosa

def detect_bpm_librosa(audio_path):
    """Detect BPM using librosa."""
    y, sr = librosa.load(audio_path)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return int(tempo)
```

### Custom Section Detection

For better section detection, use structural analysis:

```python
import librosa
import numpy as np

def detect_sections_librosa(audio_path):
    """Detect sections using librosa structural analysis."""
    y, sr = librosa.load(audio_path)

    # Compute chroma features
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

    # Compute recurrence matrix
    rec = librosa.segment.recurrence_matrix(chroma, mode='affinity')

    # Detect boundaries
    boundaries = librosa.segment.agglomerative(rec, k=8)
    boundary_times = librosa.frames_to_time(boundaries, sr=sr)

    return boundary_times
```

## Troubleshooting

### Issue: "ffmpeg not found"

**Solution:**
```bash
# Install ffmpeg
sudo apt-get install ffmpeg  # Ubuntu/Debian
brew install ffmpeg          # macOS

# Verify
which ffmpeg
ffprobe -version
```

### Issue: Poor lyrics alignment with heuristic mode

**Solution:** Install aeneas for better alignment:
```bash
sudo apt-get install espeak libespeak-dev ffmpeg
pip install aeneas

# Use aeneas mode
python3 tools/build_src.py --mp3 audio.mp3 --lyrics lyrics.txt --output src.json --mode aeneas
```

### Issue: Whisper fails with OpenMP error

**Error:** `libgomp: Thread creation failed: Resource temporarily unavailable`

**Solution:** This is a sandbox limitation. Use heuristic or aeneas mode instead:
```bash
python3 tools/build_src.py --mp3 audio.mp3 --lyrics lyrics.txt --output src.json --mode heuristic
```

### Issue: Lyrics don't match audio duration

**Solution:** Check your lyrics file:
- Remove empty lines
- Ensure each line represents one sung phrase
- Match the actual sung lyrics exactly

### Issue: Sections don't match song structure

**Solution:** The heuristic section detection is basic. For production:
1. Manually edit sections in analysis.json
2. Or integrate librosa structural analysis
3. Or use annotation tools like Sonic Visualiser

## Output Format Reference

### analysis.json Structure

```json
{
  "metadata": {
    "title": "Song Title",
    "artist": "Artist Name",
    "duration": 180.5,
    "bpm": 120,
    "key": "C major",
    "created_at": "2025-11-14T10:30:00Z",
    "source_audio": "/path/to/audio.mp3",
    "analyzer_version": "2.8.0",
    "analysis_method": "heuristic"
  },
  "sections": [
    {
      "name": "intro",
      "start_time": 0.0,
      "end_time": 15.0,
      "type": "intro",
      "mood": "mysterious",
      "energy": 0.3
    }
    // ... more sections
  ],
  "beats": [
    {"time": 0.0, "bar": 0, "beat": 0},
    {"time": 0.5, "bar": 0, "beat": 1}
    // ... hundreds of beats
  ],
  "lyrics": {
    "lines": [
      {
        "index": 0,
        "text": "First line",
        "start_time": 5.2,    // null if not merged with SRC
        "end_time": 7.8       // null if not merged with SRC
      }
      // ... more lines
    ],
    "total_lines": 42
  },
  "energy_profile": [
    {"time": 0.0, "energy": 0.3},
    {"time": 10.0, "energy": 0.5}
    // ... sampled every 10s
  ]
}
```

### src.json Structure

```json
{
  "metadata": {
    "mode_used": "aeneas",
    "created_at": "2025-11-14T10:35:00Z",
    "source_audio": "/path/to/audio.mp3",
    "source_lyrics": "/path/to/lyrics.txt",
    "duration": 180.5
  },
  "lines": [
    {
      "index": 0,
      "text": "First line of lyrics",
      "start_time": 5.2,
      "end_time": 7.8,
      "duration": 2.6
    }
    // ... more lines
  ],
  "total_lines": 42,
  "coverage": {
    "first_line_start": 5.2,
    "last_line_end": 175.3,
    "total_duration": 180.5
  }
}
```

## Integration with MV Orchestra

### Using Generated Analysis

Once you have `analysis.json` (with merged SRC timecodes), use it with MV Orchestra:

```bash
# Run all phases
python3 run_all_phases.py --analysis my-song/analysis.json

# Run specific phase
python3 phase0/creative_brief.py --analysis my-song/analysis.json

# Run with custom config
python3 run_all_phases.py --analysis my-song/analysis.json --config custom_config.json
```

### Validating Analysis Files

Use the validation tools:

```bash
# Validate analysis.json structure
python3 tools/validators/validate_analysis.py my-song/analysis.json

# Validate SRC structure
python3 tools/validators/validate_src.py my-song/src.json
```

## Best Practices

1. **Lyrics Preparation:**
   - One line per sung phrase (not per sentence)
   - Match sung lyrics exactly (including repetitions)
   - Remove empty lines
   - Use UTF-8 encoding

2. **Audio Quality:**
   - Use high-quality MP3 (192 kbps or higher)
   - Ensure audio is not corrupted
   - Trim silence at start/end if needed

3. **Alignment Mode Selection:**
   - Use `auto` mode for best automatic result
   - Use `aeneas` for best quality (if available)
   - Use `heuristic` for guaranteed functionality
   - Avoid `whisper` in sandboxed environments

4. **Manual Review:**
   - Always review generated analysis
   - Adjust section boundaries if needed
   - Verify lyrics timing makes sense
   - Check energy profile matches song feel

5. **Version Control:**
   - Keep original audio and lyrics in git
   - Version control analysis.json files
   - Document any manual adjustments

## Further Reading

- [MV Orchestra Documentation](/home/user/test/README_MVORCH.md)
- [Tools README](/home/user/test/tools/README.md)
- [ffmpeg Documentation](https://ffmpeg.org/documentation.html)
- [aeneas Documentation](https://github.com/readbeyond/aeneas)
- [Whisper Documentation](https://github.com/openai/whisper)
- [librosa Documentation](https://librosa.org/doc/latest/index.html)
