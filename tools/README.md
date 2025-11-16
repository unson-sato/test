# MV Orchestra v2.8 - Audio Analysis Tools

This directory contains tools for audio analysis and lyrics synchronization used by the MV Orchestra v2.8 multi-director AI competition system.

## Tools Overview

### 1. build_analysis.py

Generate `analysis.json` from MP3 + lyrics for use by `run_all_phases.py`.

**Features:**
- Audio duration extraction (via ffprobe)
- BPM estimation (heuristic)
- Key detection (heuristic)
- Section detection (intro, verse, chorus, bridge, outro)
- Beat timestamp generation
- Energy profile generation
- Lyrics loading

**Usage:**
```bash
python3 tools/build_analysis.py --mp3 <audio.mp3> --lyrics <lyrics.txt> --output <analysis.json>
```

**Options:**
- `--mp3`: Path to MP3 audio file (required)
- `--lyrics`: Path to lyrics text file (required)
- `--output`: Path where analysis.json will be written (required)
- `--title`: Song title (optional, defaults to filename)
- `--artist`: Artist name (optional, defaults to "Unknown Artist")
- `--verbose, -v`: Enable verbose logging

**Example:**
```bash
python3 tools/build_analysis.py \
    --mp3 songs/electric_dreams.mp3 \
    --lyrics songs/electric_dreams.txt \
    --output analysis.json \
    --title "Electric Dreams" \
    --artist "Neon Pulse"
```

**Requirements:**
- ffmpeg/ffprobe (must be installed on system)
- Python 3.9+

### 2. build_src.py

Generate SRC (lyrics timecode) from MP3 + lyrics using forced alignment or heuristics.

**Features:**
- Multiple alignment modes (auto, aeneas, whisper, heuristic)
- Graceful fallback when dependencies unavailable
- Word-level or line-level timestamps
- Sandbox-safe heuristic mode

**Usage:**
```bash
python3 tools/build_src.py --mp3 <audio.mp3> --lyrics <lyrics.txt> --output <src.json>
```

**Options:**
- `--mp3`: Path to MP3 audio file (required)
- `--lyrics`: Path to lyrics text file (required)
- `--output`: Path where src.json will be written (required)
- `--mode`: Alignment mode - auto, aeneas, whisper, heuristic (default: auto)
- `--whisper-model`: Whisper model to use if mode=whisper (default: base)
- `--verbose, -v`: Enable verbose logging

**Modes:**

| Mode | Description | Dependencies | Quality |
|------|-------------|--------------|---------|
| `auto` | Try aeneas first, fall back to heuristic | None required | Best available |
| `aeneas` | Forced alignment using aeneas | aeneas, ffmpeg, espeak | High |
| `whisper` | Speech recognition with Whisper | whisper | High (may fail in sandboxes) |
| `heuristic` | Equal-interval distribution | None | Basic |

**Examples:**
```bash
# Auto mode (recommended)
python3 tools/build_src.py --mp3 song.mp3 --lyrics lyrics.txt --output src.json

# Force heuristic (no dependencies)
python3 tools/build_src.py --mp3 song.mp3 --lyrics lyrics.txt --output src.json --mode heuristic

# Use aeneas
python3 tools/build_src.py --mp3 song.mp3 --lyrics lyrics.txt --output src.json --mode aeneas

# Use Whisper with base model
python3 tools/build_src.py --mp3 song.mp3 --lyrics lyrics.txt --output src.json --mode whisper
```

**Requirements:**
- **Minimal (heuristic mode):** Python 3.9+
- **For aeneas mode:** `pip install aeneas` + ffmpeg + espeak
- **For whisper mode:** `pip install git+https://github.com/openai/whisper.git`

### 3. audio_utils.py

Shared utility functions for audio processing.

**Functions:**
- `get_audio_duration()` - Extract duration using ffprobe
- `estimate_bpm_heuristic()` - Simple BPM estimation
- `detect_key_heuristic()` - Musical key detection
- `generate_beats()` - Beat timestamp generation
- `detect_sections_heuristic()` - Song section detection
- `generate_energy_profile()` - Energy profile generation
- `load_lyrics_lines()` - Load and parse lyrics
- `check_ffmpeg_available()` - Check for ffmpeg
- `check_aeneas_available()` - Check for aeneas
- `check_whisper_available()` - Check for whisper

## Installation

### Minimal Installation (heuristic mode only)

```bash
# System dependencies
sudo apt-get install ffmpeg  # Ubuntu/Debian
# or
brew install ffmpeg          # macOS

# No Python packages needed for heuristic mode
```

### Full Installation (all modes)

```bash
# System dependencies
sudo apt-get install ffmpeg espeak libespeak-dev  # Ubuntu/Debian

# Python packages
pip install aeneas
pip install git+https://github.com/openai/whisper.git

# Note: Whisper may require additional setup for GPU support
```

### Verifying Installation

```bash
# Check ffmpeg
ffmpeg -version

# Check espeak (for aeneas)
espeak --version

# Check Python packages
python3 -c "import aeneas; print('aeneas OK')"
python3 -c "import whisper; print('whisper OK')"
```

## Output Formats

### analysis.json Format

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
      "end_time": 8.5,
      "type": "intro",
      "mood": "mysterious",
      "energy": 0.3
    }
  ],
  "beats": [
    {"time": 0.0, "bar": 0, "beat": 0},
    {"time": 0.5, "bar": 0, "beat": 1}
  ],
  "lyrics": {
    "lines": [
      {"index": 0, "text": "First line", "start_time": null, "end_time": null}
    ],
    "total_lines": 42
  },
  "energy_profile": [
    {"time": 0.0, "energy": 0.3},
    {"time": 10.0, "energy": 0.5}
  ]
}
```

### src.json Format

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
  ],
  "total_lines": 42,
  "coverage": {
    "first_line_start": 5.2,
    "last_line_end": 175.3,
    "total_duration": 180.5
  }
}
```

## Workflow

### Complete Analysis Pipeline

1. **Generate initial analysis:**
   ```bash
   python3 tools/build_analysis.py \
       --mp3 song.mp3 \
       --lyrics lyrics.txt \
       --output analysis.json \
       --title "My Song" \
       --artist "My Artist"
   ```

2. **Generate lyrics timecode (SRC):**
   ```bash
   python3 tools/build_src.py \
       --mp3 song.mp3 \
       --lyrics lyrics.txt \
       --output src.json
   ```

3. **Merge SRC into analysis (manual or scripted):**
   ```python
   import json

   # Load files
   with open('analysis.json') as f:
       analysis = json.load(f)
   with open('src.json') as f:
       src = json.load(f)

   # Update lyrics timestamps
   for i, line in enumerate(src['lines']):
       if i < len(analysis['lyrics']['lines']):
           analysis['lyrics']['lines'][i]['start_time'] = line['start_time']
           analysis['lyrics']['lines'][i]['end_time'] = line['end_time']

   # Save updated analysis
   with open('analysis_with_timecodes.json', 'w') as f:
       json.dump(analysis, f, indent=2)
   ```

4. **Use with MV Orchestra:**
   ```bash
   python3 run_all_phases.py --analysis analysis_with_timecodes.json
   ```

## Troubleshooting

### ffmpeg not found

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Verify
ffmpeg -version
```

### aeneas import error

```bash
# Install system dependencies first
sudo apt-get install espeak libespeak-dev ffmpeg

# Then install aeneas
pip install aeneas

# Verify
python3 -c "import aeneas; print('OK')"
```

### Whisper OpenMP error

Whisper may fail in sandboxed environments with OpenMP/libgomp errors. This is a known limitation. Solutions:

1. Use `--mode heuristic` for guaranteed functionality
2. Use `--mode aeneas` if available
3. Run outside sandbox environment

### Poor alignment quality

If heuristic mode produces poor results:

1. Install aeneas for better alignment: `pip install aeneas`
2. Ensure lyrics match actual sung lyrics exactly
3. Remove instrumental sections from lyrics
4. Split long lines into shorter phrases

## Development

### Running Tests

```bash
# Test build_analysis.py
python3 tools/test_build_analysis.py

# Test build_src.py
python3 tools/test_build_src.py
```

### Adding New Features

When extending these tools:

1. Add new functions to `audio_utils.py` for shared functionality
2. Maintain backward compatibility with existing output formats
3. Add graceful fallbacks for optional dependencies
4. Update this README with new features

## Known Limitations

### Current Implementation

- **BPM Detection:** Uses heuristic (fixed 120 BPM). For production, integrate librosa or essentia.
- **Key Detection:** Returns placeholder ("C major"). Integrate librosa for actual detection.
- **Section Detection:** Uses time-based heuristics. For production, use structural analysis.
- **Beat Generation:** Regular intervals based on BPM. For production, use madmom or librosa.
- **Lyrics Alignment:** Heuristic mode distributes evenly. Use aeneas or whisper for accurate timing.

### Future Enhancements

- Integrate librosa for BPM and key detection
- Add essentia for advanced music analysis
- Implement madmom for accurate beat tracking
- Add MIDI extraction support
- Support for multiple audio formats (WAV, FLAC, etc.)
- Batch processing for multiple songs
- GUI interface for manual timing adjustment

## References

- **ffmpeg:** https://ffmpeg.org/
- **aeneas:** https://github.com/readbeyond/aeneas
- **Whisper:** https://github.com/openai/whisper
- **librosa:** https://librosa.org/
- **essentia:** https://essentia.upf.edu/
- **madmom:** https://github.com/CPJKU/madmom

## Support

For issues or questions:
1. Check this README for common solutions
2. Review the tool's help: `python3 tools/build_analysis.py --help`
3. Check the main MV Orchestra documentation
4. Review example usage in test files

## License

Part of MV Orchestra v2.8 project.
