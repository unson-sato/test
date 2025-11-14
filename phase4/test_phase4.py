#!/usr/bin/env python3
"""
Test Suite for Phase 4: Generation Strategy

This module tests the generation strategy phase functionality.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core import SharedState
from phase4 import (
    run_phase4,
    Phase4Runner,
    GenerationMode,
    get_mode_spec,
    recommend_mode,
    PromptBuilder,
    create_character_prompt,
    AssetManager,
    AssetType
)


def test_generation_modes():
    """Test generation mode specifications"""
    print("\n" + "="*60)
    print("Test: Generation Modes")
    print("="*60)

    # Test mode specs
    veo2_spec = get_mode_spec(GenerationMode.VEO2)
    print(f"\nVeo2 Spec:")
    print(f"  Name: {veo2_spec.name}")
    print(f"  Quality: {veo2_spec.quality_level}/10")
    print(f"  Cost: {veo2_spec.typical_cost_per_clip}")

    sora_spec = get_mode_spec(GenerationMode.SORA)
    print(f"\nSora Spec:")
    print(f"  Name: {sora_spec.name}")
    print(f"  Quality: {sora_spec.quality_level}/10")
    print(f"  Cost: {sora_spec.typical_cost_per_clip}")

    print("\n✓ Generation mode specs loaded successfully")


def test_mode_recommendation():
    """Test generation mode recommendation"""
    print("\n" + "="*60)
    print("Test: Mode Recommendation")
    print("="*60)

    # Test recommendations
    test_cases = [
        ("performance", "high", True, True),
        ("establishing", "medium", True, False),
        ("transition", "low", False, False),
        ("stylized", "medium", True, False),
    ]

    for clip_type, budget, quality_priority, char_focused in test_cases:
        mode = recommend_mode(clip_type, budget, quality_priority, char_focused)
        print(f"\n{clip_type.upper()} (budget={budget}, quality={quality_priority}, character={char_focused})")
        print(f"  → Recommended: {mode.value}")

    print("\n✓ Mode recommendation working")


def test_prompt_builder():
    """Test prompt building utilities"""
    print("\n" + "="*60)
    print("Test: Prompt Builder")
    print("="*60)

    # Test character prompt
    char_prompt = create_character_prompt(
        character_name="Young woman",
        action="dancing energetically",
        setting="neon-lit club",
        emotion="joyful",
        clothing="modern streetwear",
        camera_angle="medium shot"
    )

    print(f"\nCharacter Prompt:")
    print(f"  Base: {char_prompt.base_prompt}")
    print(f"  Full: {char_prompt.build()[:100]}...")

    # Test builder pattern
    builder = PromptBuilder()
    custom_prompt = (builder
        .set_base("A futuristic cityscape")
        .add_style("cyberpunk aesthetic", "neon colors")
        .add_technical("wide angle", "8K resolution")
        .add_quality("photorealistic", "highly detailed")
        .set_negative("blur, distortion")
        .build())

    print(f"\nCustom Prompt:")
    print(f"  Full: {custom_prompt.build()[:100]}...")

    print("\n✓ Prompt building working")


def test_asset_manager():
    """Test asset management"""
    print("\n" + "="*60)
    print("Test: Asset Manager")
    print("="*60)

    # Create asset manager
    manager = AssetManager("test_session_123")

    # Add global asset
    from phase4.asset_manager import create_style_guide_asset
    style_asset = create_style_guide_asset(
        style_name="Cyberpunk",
        color_palette=["#00FFFF", "#FF00FF", "#000000"]
    )
    manager.add_global_asset(style_asset)

    # Add clip assets
    char_asset = manager.create_asset(
        asset_type=AssetType.CHARACTER_REFERENCE,
        description="Main character reference",
        source="Phase 1 design"
    )
    manager.add_clip_asset("clip_001", char_asset, required=True)

    audio_asset = manager.create_asset(
        asset_type=AssetType.AUDIO_SEGMENT,
        description="Audio for clip_001",
        source="Original track"
    )
    manager.add_clip_asset("clip_001", audio_asset, required=False)

    # Get summary
    summary = manager.get_asset_summary()
    print(f"\nAsset Summary:")
    print(f"  Total assets: {summary['total_assets']}")
    print(f"  Global assets: {summary['global_assets']}")
    print(f"  Clips with assets: {summary['clips_with_assets']}")
    print(f"  Assets by type: {summary['assets_by_type']}")

    print("\n✓ Asset management working")


def test_phase4_runner():
    """Test Phase 4 runner with mock session"""
    print("\n" + "="*60)
    print("Test: Phase 4 Runner")
    print("="*60)

    # Create a test session
    session = SharedState.create_session()
    session_id = session.session_id
    print(f"\nCreated test session: {session_id}")

    # Set up minimal data for previous phases
    session.start_phase(0)
    session.set_phase_data(0, {
        'concept': 'Test MV concept',
        'color_palette': ['blue', 'purple', 'black']
    })
    session.complete_phase(0)

    session.start_phase(1)
    session.set_phase_data(1, {
        'characters': [
            {'name': 'Main Character', 'description': 'A young performer'}
        ]
    })
    session.complete_phase(1)

    session.start_phase(2)
    session.set_phase_data(2, {
        'sections': [
            {'section_name': 'Intro', 'mood': 'mysterious'}
        ]
    })
    session.complete_phase(2)

    session.start_phase(3)
    session.set_phase_data(3, {
        'winner': {
            'proposal': {
                'sections': [
                    {
                        'section_name': 'Intro',
                        'mood': 'mysterious',
                        'clips': [
                            {
                                'clip_id': 'clip_001',
                                'start_time': 0.0,
                                'end_time': 3.0,
                                'duration': 3.0,
                                'description': 'Opening shot',
                                'clip_type': 'establishing'
                            },
                            {
                                'clip_id': 'clip_002',
                                'start_time': 3.0,
                                'end_time': 6.0,
                                'duration': 3.0,
                                'description': 'Character intro',
                                'clip_type': 'performance'
                            }
                        ]
                    }
                ]
            }
        }
    })
    session.complete_phase(3)

    # Run Phase 4
    print("\nRunning Phase 4...")
    results = run_phase4(session_id, mock_mode=True)

    # Verify results
    print(f"\n✓ Phase 4 completed")
    print(f"  Proposals: {len(results['proposals'])}")
    print(f"  Evaluations: {len(results['evaluations'])}")
    print(f"  Winner: {results['winner']['director']}")
    print(f"  Winner Score: {results['winner']['total_score']:.1f}/100")

    # Check generation strategies
    winner_strategies = results['winner']['proposal']['generation_strategies']
    print(f"  Generation strategies: {len(winner_strategies)}")

    for strategy in winner_strategies[:2]:  # Show first 2
        print(f"\n  Clip: {strategy['clip_id']}")
        print(f"    Mode: {strategy['generation_mode']}")
        print(f"    Type: {strategy['clip_type']}")
        print(f"    Prompt: {strategy['prompt_template']['full_prompt'][:80]}...")

    # Check asset pipeline
    asset_pipeline = results['asset_pipeline']
    print(f"\n  Asset Pipeline:")
    print(f"    Total assets: {asset_pipeline['summary']['total_assets']}")
    print(f"    Global assets: {asset_pipeline['summary']['global_assets']}")

    print("\n✓ Phase 4 runner test passed")

    return session_id


def test_full_integration():
    """Test full Phase 4 integration"""
    print("\n" + "="*60)
    print("Test: Full Integration")
    print("="*60)

    try:
        # Run all component tests
        test_generation_modes()
        test_mode_recommendation()
        test_prompt_builder()
        test_asset_manager()
        session_id = test_phase4_runner()

        print("\n" + "="*60)
        print("All Phase 4 tests passed! ✓")
        print("="*60)

        return True

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_full_integration()
    sys.exit(0 if success else 1)
