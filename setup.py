#!/usr/bin/env python3
"""
Setup script for MV Orchestra v2.8

Installation:
    pip install -e .                    # Development mode
    pip install -e ".[audio]"           # With audio analysis
    pip install -e ".[ai]"              # With real AI
    pip install -e ".[all]"             # All optional features
    pip install -e ".[dev]"             # Development tools
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read version from core module
version = "2.8.0"

setup(
    name="mv-orchestra",
    version=version,
    description="Multi-Director AI Competition System for Music Video Generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="MV Orchestra Team",
    author_email="support@example.com",
    url="https://github.com/yourrepo/mv-orchestra",
    project_urls={
        "Bug Tracker": "https://github.com/yourrepo/mv-orchestra/issues",
        "Documentation": "https://github.com/yourrepo/mv-orchestra#readme",
        "Source Code": "https://github.com/yourrepo/mv-orchestra",
    },
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Video",
        "Topic :: Artistic Software",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[
        "music-video",
        "ai",
        "video-generation",
        "creative-tools",
        "multimedia",
        "automation",
        "claude",
        "anthropic"
    ],
    python_requires=">=3.9",
    packages=find_packages(exclude=["tests", "examples", "docs"]),
    include_package_data=True,
    install_requires=[
        # No required dependencies - runs on Python standard library!
    ],
    extras_require={
        # Audio analysis features
        "audio": [
            "librosa>=0.10.0",
            "scipy>=1.11.0",
            "numpy>=1.24.0",
            "soundfile>=0.12.0",
        ],
        # Real AI evaluations
        "ai": [
            "anthropic>=0.18.0",
        ],
        # Advanced audio features
        "audio_advanced": [
            "librosa>=0.10.0",
            "scipy>=1.11.0",
            "numpy>=1.24.0",
            "soundfile>=0.12.0",
            "aeneas",
            "openai-whisper>=20230314",
        ],
        # All optional features
        "all": [
            "librosa>=0.10.0",
            "scipy>=1.11.0",
            "numpy>=1.24.0",
            "soundfile>=0.12.0",
            "anthropic>=0.18.0",
        ],
        # Development tools
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "isort>=5.12.0",
        ],
        # Documentation
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
            "myst-parser>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mv-orchestra=run_all_phases:main",
            "mv-test=test_e2e:main",
        ],
    },
    package_data={
        "": [
            "*.json",
            "*.txt",
            "*.md",
            "README*",
            "LICENSE*",
        ],
    },
    zip_safe=False,
)
