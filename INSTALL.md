# Installation Guide - MV Orchestra v2.8

This guide covers installation and configuration of MV Orchestra.

---

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Installation](#quick-installation)
- [Detailed Installation](#detailed-installation)
- [Optional Dependencies](#optional-dependencies)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements

- **Python**: 3.9 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 100MB for installation, 1GB for sessions
- **OS**: Linux, macOS, or Windows

### Recommended Requirements

- **Python**: 3.10 or higher
- **RAM**: 8GB
- **Storage**: SSD with 5GB free space
- **OS**: Linux or macOS

---

## Quick Installation

For most users, installation is simple:

```bash
# 1. Clone the repository
git clone https://github.com/yourrepo/mv-orchestra.git
cd mv-orchestra

# 2. Verify Python version
python3 --version  # Should be 3.9+

# 3. Test installation
python3 run_all_phases.py test_session

# Done! No additional dependencies needed for basic usage.
```

---

## Detailed Installation

### Step 1: Clone Repository

```bash
# Using HTTPS
git clone https://github.com/yourrepo/mv-orchestra.git

# Or using SSH
git clone git@github.com:yourrepo/mv-orchestra.git

# Navigate to directory
cd mv-orchestra
```

### Step 2: Verify Python

```bash
# Check Python version
python3 --version

# Should output: Python 3.9.x or higher
# If not, install/upgrade Python:
#   Ubuntu/Debian: sudo apt-get install python3.10
#   macOS: brew install python@3.10
#   Windows: Download from python.org
```

### Step 3: Verify Installation

```bash
# List directory contents
ls -la

# Expected files/directories:
#   - core/
#   - phase0/ through phase5/
#   - tools/
#   - run_all_phases.py
#   - sample_analysis.json
```

### Step 4: Run Test

```bash
# Run with test session
python3 run_all_phases.py test_install

# Should complete in 5-10 seconds
# Check for "Pipeline completed successfully!"
```

---

## Optional Dependencies

MV Orchestra runs with Python standard library only, but optional features require additional packages:

### Audio Analysis (Recommended)

To analyze your own MP3 files:

```bash
# Install audio processing libraries
pip install librosa scipy numpy

# Ubuntu/Debian: Also install ffmpeg
sudo apt-get install ffmpeg

# macOS: Install ffmpeg with Homebrew
brew install ffmpeg

# Windows: Download ffmpeg from https://ffmpeg.org/
```

Test audio analysis:

```bash
python3 tools/build_analysis.py --help
```

### Real AI Evaluations (Optional)

To use actual Claude API instead of mock evaluations:

```bash
# Install Anthropic SDK
pip install anthropic

# Set API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Or add to ~/.bashrc or ~/.zshrc
echo 'export ANTHROPIC_API_KEY="your-api-key"' >> ~/.bashrc
```

Test real evaluations:

```bash
python3 run_all_phases.py test_real --real-mode
```

### Advanced Audio Features (Optional)

For lyrics-to-audio alignment:

```bash
# Install aeneas (requires ffmpeg)
pip install aeneas

# Test alignment
python3 -c "import aeneas; print('Aeneas installed successfully')"
```

For speech-to-text (Whisper):

```bash
# Install OpenAI Whisper
pip install openai-whisper

# Test Whisper
python3 -c "import whisper; print('Whisper installed successfully')"
```

### Development Tools (Optional)

For development and testing:

```bash
# Install development dependencies
pip install pytest pytest-cov black flake8 mypy isort

# Run tests
python3 test_e2e.py

# Run linting
black --check .
flake8 .
mypy core/
```

---

## Configuration

### Basic Configuration

Configuration is stored in `config.json`:

```json
{
  "version": "2.8",
  "mock_mode": true,
  "default_evaluator": "codex",
  "session_storage": "shared-workspace/sessions",
  "evaluation_storage": "shared-workspace/evaluations",
  "optimization": {
    "clip_optimizer": {
      "enabled": true,
      "min_clip_duration": 1.0,
      "max_clip_duration": 10.0
    },
    "emotion_target_builder": {
      "enabled": true
    }
  },
  "validation": {
    "clip_division": {
      "enabled": true,
      "strict_mode": false
    },
    "phase4_strategies": {
      "enabled": true
    }
  }
}
```

### Environment Variables

Set these in your shell or `.env` file:

```bash
# Required for real Claude API usage
export ANTHROPIC_API_KEY="your-api-key"

# Optional: Custom session directory
export MV_ORCHESTRA_SESSION_DIR="/path/to/sessions"

# Optional: Custom configuration file
export MV_ORCHESTRA_CONFIG="/path/to/config.json"

# Optional: Logging level
export MV_ORCHESTRA_LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
```

### Input Directory Setup

Place your input files in `shared-workspace/input/`:

```bash
# Create input directory if needed
mkdir -p shared-workspace/input

# Add your files
cp your_song.mp3 shared-workspace/input/
cp your_lyrics.txt shared-workspace/input/lyrics.txt
```

---

## Verification

### Verify Core Installation

```bash
# Test imports
python3 -c "from core import SharedState; print('Core OK')"
python3 -c "from phase0 import run_phase0; print('Phase 0 OK')"
python3 -c "from phase1 import run_phase1; print('Phase 1 OK')"

# Run quick test
python3 test_e2e.py -q
```

### Verify Optional Dependencies

```bash
# Test audio analysis
python3 -c "import librosa; print('Librosa OK')"

# Test Anthropic SDK
python3 -c "import anthropic; print('Anthropic SDK OK')"
```

### Run Full Test Suite

```bash
# Run all tests
python3 test_e2e.py -v

# Expected output:
#   test_full_pipeline_mock_mode ... ok
#   test_pipeline_with_optimization ... ok
#   test_pipeline_with_validation ... ok
#   ...
#   ALL TESTS PASSED
```

---

## Troubleshooting

### Common Issues

#### Issue: "Python version too old"

**Error**: `SyntaxError` or import errors

**Solution**:
```bash
# Check Python version
python3 --version

# Install Python 3.10+
# Ubuntu/Debian
sudo apt-get install python3.10

# macOS
brew install python@3.10

# Update python3 symlink if needed
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
```

#### Issue: "Module 'librosa' not found"

**Error**: `ModuleNotFoundError: No module named 'librosa'`

**Solution**:
```bash
# Install audio dependencies
pip install librosa scipy numpy

# If pip not found
sudo apt-get install python3-pip  # Ubuntu/Debian
brew install python3  # macOS (includes pip)
```

#### Issue: "ffmpeg not found"

**Error**: `FileNotFoundError: ffmpeg`

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
# Add to PATH
```

#### Issue: "Permission denied" when running scripts

**Error**: `PermissionError` or `-bash: permission denied`

**Solution**:
```bash
# Make scripts executable
chmod +x run_all_phases.py
chmod +x test_e2e.py
chmod +x examples/*.py

# Or run with python3
python3 run_all_phases.py test_session
```

#### Issue: "ANTHROPIC_API_KEY not set"

**Error**: `ValueError: ANTHROPIC_API_KEY environment variable not set`

**Solution**:
```bash
# Set API key
export ANTHROPIC_API_KEY="your-api-key"

# Or use mock mode
python3 run_all_phases.py test_session --mock-mode

# Or add to shell config
echo 'export ANTHROPIC_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc
```

#### Issue: "Session directory already exists"

**Error**: `ValueError: Session already exists`

**Solution**:
```bash
# Use a different session ID
python3 run_all_phases.py my_session_v2

# Or delete old session
rm -rf shared-workspace/sessions/my_session

# Or load existing session
# (Session will be reused/updated)
```

### Getting Help

If you encounter issues not covered here:

1. Check the [USER_GUIDE.md](USER_GUIDE.md) for usage questions
2. Check the [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for development issues
3. Open an issue on [GitHub](https://github.com/yourrepo/mv-orchestra/issues)
4. Email support at support@example.com

---

## Platform-Specific Notes

### Linux (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3.10 python3-pip ffmpeg

# Install Python dependencies
pip install librosa scipy numpy anthropic
```

### macOS

```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.10 ffmpeg

# Install Python packages
pip3 install librosa scipy numpy anthropic
```

### Windows

1. Install Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. Install ffmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
3. Add ffmpeg to PATH
4. Open Command Prompt or PowerShell:

```powershell
# Install Python packages
pip install librosa scipy numpy anthropic

# Set API key (PowerShell)
$env:ANTHROPIC_API_KEY="your-api-key"

# Or set permanently in System Environment Variables
```

---

## Next Steps

After successful installation:

1. Read the [USER_GUIDE.md](USER_GUIDE.md) for usage instructions
2. Try the examples in the `examples/` directory
3. Run the end-to-end tests to verify functionality
4. Start creating your first music video design!

---

**Last Updated**: 2025-11-14
