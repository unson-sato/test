"""
System-wide constants for MV Orchestra v3.0

This module defines all magic numbers, thresholds, and configuration values
used throughout the system.
"""

# Quality thresholds
DEFAULT_QUALITY_THRESHOLD = 70.0
CLIP_SCORE_THRESHOLD = 0.7
TECHNICAL_SCORE_THRESHOLD = 0.8

# Iteration limits
DEFAULT_MAX_ITERATIONS = 3
DEFAULT_MAX_REGENERATION_ATTEMPTS = 3

# Concurrency limits
DEFAULT_MAX_PARALLEL_AGENTS = 5
DEFAULT_AGENT_TIMEOUT_SECONDS = 300

# File size limits (in bytes)
MAX_AUDIO_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
MAX_VIDEO_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5 GB
MAX_JSON_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Session limits
MAX_SESSION_ID_LENGTH = 255
MAX_SESSIONS = 1000

# Phase configuration
PHASE_0_AUDIO_ANALYSIS = 0
PHASE_1_STORY_MESSAGE = 1
PHASE_2_SECTION_BREAKDOWN = 2
PHASE_3_CLIP_DESIGN = 3
PHASE_4_REFINEMENT = 4
PHASE_5_MCP_GENERATION = 5
PHASE_6_CLIP_EVALUATION = 6
PHASE_7_VIDEO_EDITING = 7
PHASE_8_EFFECTS_CODE = 8
PHASE_9_REMOTION_RENDERING = 9

ALL_PHASES = list(range(10))
DESIGN_PHASES = list(range(1, 5))
GENERATION_PHASES = list(range(5, 10))

# Director types
DIRECTOR_CORPORATE = "corporate"
DIRECTOR_FREELANCER = "freelancer"
DIRECTOR_VETERAN = "veteran"
DIRECTOR_AWARD_WINNER = "award_winner"
DIRECTOR_NEWCOMER = "newcomer"

PHASE_1_4_DIRECTORS = [
    DIRECTOR_CORPORATE,
    DIRECTOR_FREELANCER,
    DIRECTOR_VETERAN,
    DIRECTOR_AWARD_WINNER,
    DIRECTOR_NEWCOMER,
]

# Effects generator types
EFFECTS_MINIMALIST = "minimalist"
EFFECTS_CREATIVE = "creative"
EFFECTS_BALANCED = "balanced"

PHASE_8_AGENTS = [
    EFFECTS_MINIMALIST,
    EFFECTS_CREATIVE,
    EFFECTS_BALANCED,
]

# File system safety
ALLOWED_EXTENSIONS = {
    "audio": {".mp3", ".wav", ".flac", ".m4a", ".ogg"},
    "video": {".mp4", ".mov", ".avi", ".mkv"},
    "image": {".jpg", ".jpeg", ".png", ".gif", ".webp"},
    "json": {".json"},
}

FORBIDDEN_PATH_CHARS = {".", "\\", "|", "<", ">", '"', "?", "*"}
FORBIDDEN_PATH_SEQUENCES = {"..", "~", "$"}

# Timeouts (in seconds)
SUBPROCESS_TIMEOUT = 300
MCP_GENERATION_TIMEOUT = 120
FFMPEG_TIMEOUT = 300
REMOTION_RENDER_TIMEOUT = 600

# Retry configuration
MAX_RETRIES = 4
RETRY_BACKOFF_BASE = 2.0  # seconds
RETRY_BACKOFF_MULTIPLIER = 2.0

# Video settings
DEFAULT_VIDEO_WIDTH = 1920
DEFAULT_VIDEO_HEIGHT = 1080
DEFAULT_VIDEO_FPS = 30
DEFAULT_VIDEO_CODEC = "libx264"
DEFAULT_VIDEO_CRF = 18

# Transition settings
DEFAULT_TRANSITION_DURATION = 1.0
MIN_TRANSITION_DURATION = 0.0
MAX_TRANSITION_DURATION = 5.0

TRANSITION_TYPES = {"crossfade", "fade", "none"}

# Logging
LOG_MAX_LENGTH = 10000
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Session directory structure
SESSION_DIR_NAME = "sessions"
OUTPUT_DIR_NAME = "output"
TEMP_DIR_NAME = "temp"
PROMPTS_DIR_NAME = ".claude/prompts"
CONFIG_DIR_NAME = "config"
