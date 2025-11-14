# Input Files Directory

This directory contains input files for MV Orchestra v2.8 sessions.

## Expected Files

For each music video generation session, place the following files here:

### Required Files

1. **Audio File** (`.mp3`, `.wav`, `.m4a`, or `.flac`)
   - The music track for which the video will be generated
   - Recommended: High-quality audio (320kbps MP3 or lossless formats)

2. **Lyrics File** (`.txt` or `.json`)
   - Song lyrics with timing information (if available)
   - Format options:
     - Plain text: One line per lyric line
     - JSON: `{"time": "00:12.5", "text": "lyric line"}`

### Optional Files

3. **Analysis File** (`analysis.json`)
   - Pre-computed audio analysis data
   - If not provided, will be generated automatically
   - Contains: tempo, beats, sections, mood, key, etc.

4. **Reference Images** (`.jpg`, `.png`)
   - Visual references for style, characters, mood
   - Place in a subdirectory named after your session

## File Naming Convention

Use descriptive names that help identify the session:

```
song_title_artist.mp3
song_title_lyrics.txt
song_title_analysis.json
```

## Example Structure

```
shared-workspace/input/
├── mysong_audio.mp3
├── mysong_lyrics.txt
├── mysong_analysis.json
└── mysong_references/
    ├── style_ref_01.jpg
    ├── character_ref_01.jpg
    └── mood_ref_01.jpg
```

## Security Note

- Audio files are excluded from git by default (see `.gitignore`)
- Do not commit copyrighted material without proper authorization
- Keep personal/sensitive content out of this directory if sharing the repository
