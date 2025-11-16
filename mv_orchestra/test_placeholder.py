#!/usr/bin/env python3
"""
Test script for placeholder image generation

Tests the image generator without requiring API keys or audio files.
Simply generates sample placeholder images to verify the system works.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.image_generator import ImageGenerator


def test_placeholder_generation():
    """Test placeholder image generation"""

    print("=" * 70)
    print("PLACEHOLDER IMAGE GENERATION TEST")
    print("=" * 70)
    print()

    # Initialize generator
    generator = ImageGenerator()

    # Set style reference
    print("Setting style reference...")
    generator.set_style_reference(
        seed=42,
        color_palette=["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#96CEB4"]
    )
    print()

    # Create test scenes
    test_scenes = [
        {
            'prompt': 'Opening scene: Sunrise over mountains, peaceful atmosphere',
            'mood': 'peaceful'
        },
        {
            'prompt': 'Dynamic scene: Energy builds, vibrant colors swirling',
            'mood': 'energetic'
        },
        {
            'prompt': 'Intense scene: Dramatic lighting, powerful emotions',
            'mood': 'intense'
        },
        {
            'prompt': 'Calm scene: Gentle waves, serene landscape',
            'mood': 'calm'
        },
        {
            'prompt': 'Closing scene: Starry night sky, contemplative mood',
            'mood': 'contemplative'
        }
    ]

    print(f"Generating {len(test_scenes)} test images...\n")

    # Generate batch
    results = generator.generate_scene_batch(
        scene_prompts=test_scenes,
        output_dir="./test_output/scenes",
        use_controlnet=False
    )

    # Summary
    print("\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print(f"\n✓ Generated: {len(results)} images")
    print(f"✓ Output directory: ./test_output/scenes/")
    print(f"✓ Total cost: $0.00 (Placeholder mode)")
    print()

    # List generated files
    print("Generated files:")
    for i, result in enumerate(results):
        print(f"  {i+1}. {result['image_path']}")
    print()

    # Verify files exist
    all_exist = all(Path(r['image_path']).exists() for r in results)

    if all_exist:
        print("✅ All files verified successfully!")
        print()
        print("Next steps:")
        print("  1. Check the images in: ./test_output/scenes/")
        print("  2. Install librosa: pip install librosa soundfile")
        print("  3. Install FFmpeg: sudo apt install ffmpeg")
        print("  4. Get a test MP3 file (10 seconds)")
        print("  5. Run full test: python core/orchestrator.py test.mp3 10")
        return 0
    else:
        print("❌ Some files were not created")
        return 1


if __name__ == "__main__":
    exit_code = test_placeholder_generation()
    sys.exit(exit_code)
