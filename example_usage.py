#!/usr/bin/env python3
"""
Example Usage of MV Orchestra v2.8 Core Functionality

This script demonstrates basic usage of the core components:
- Creating and managing sessions
- Working with director profiles
- Running evaluations
- Storing and retrieving phase data
"""

from core import (
    SharedState,
    DirectorType,
    CodexRunner,
    EvaluationRequest,
    get_director_profile,
    get_all_profiles
)


def example_session_management():
    """Demonstrate session creation and management"""
    print("=" * 60)
    print("Example 1: Session Management")
    print("=" * 60)

    # Create a new session
    print("\n1. Creating a new session...")
    session = SharedState.create_session(
        input_files={
            'mp3': 'shared-workspace/input/example_song.mp3',
            'lyrics': 'shared-workspace/input/example_lyrics.txt'
        }
    )
    print(f"   Session ID: {session.session_id}")
    print(f"   Created at: {session.metadata.created_at}")

    # Start Phase 0
    print("\n2. Starting Phase 0: Overall Design...")
    session.start_phase(0)
    print(f"   Phase status: {session.phases[0].status}")

    # Set phase data
    print("\n3. Setting phase data...")
    session.set_phase_data(0, {
        'concept': 'A futuristic cyberpunk narrative following a lone hacker',
        'mood': 'energetic, mysterious, hopeful',
        'visual_style': 'neon-lit cityscapes, digital glitches, rain-soaked streets',
        'color_palette': ['neon blue', 'deep purple', 'electric pink', 'noir black'],
        'narrative_arc': 'Discovery -> Conflict -> Resolution -> Transcendence'
    })
    print("   Phase data stored")

    # Add optimization log
    print("\n4. Adding optimization log entry...")
    session.add_optimization_log({
        'phase': 0,
        'message': 'Initial concept proposal generated',
        'details': 'Combining cyberpunk aesthetics with emotional narrative'
    })
    print("   Log entry added")

    # Get session summary
    print("\n5. Session summary:")
    summary = session.get_session_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")

    # Complete the phase
    print("\n6. Completing Phase 0...")
    session.complete_phase(0)
    print(f"   Phase status: {session.phases[0].status}")

    return session


def example_director_profiles():
    """Demonstrate working with director profiles"""
    print("\n" + "=" * 60)
    print("Example 2: Director Profiles")
    print("=" * 60)

    # Get all profiles
    profiles = get_all_profiles()
    print(f"\nTotal directors: {len(profiles)}")

    # Display each director
    for profile in profiles:
        print(f"\n{profile.name_en} ({profile.name_ja}):")
        print(f"  Risk Tolerance: {profile.risk_tolerance}")
        print(f"  Commercial Focus: {profile.commercial_focus}")
        print(f"  Artistic Focus: {profile.artistic_focus}")
        print(f"  Innovation Focus: {profile.innovation_focus}")
        print(f"  Top Strengths:")
        for strength in profile.strengths[:2]:
            print(f"    - {strength}")

    # Get specific director
    print("\n" + "-" * 60)
    freelancer = get_director_profile(DirectorType.FREELANCER)
    print(f"\nFreelancer Creative Tendencies:")
    for tendency in freelancer.creative_tendencies:
        print(f"  - {tendency}")


def example_evaluation_execution():
    """Demonstrate running evaluations"""
    print("\n" + "=" * 60)
    print("Example 3: Evaluation Execution")
    print("=" * 60)

    # Create a session
    session = SharedState.create_session()
    print(f"\nSession ID: {session.session_id}")

    # Set up some proposal data
    proposal = {
        'title': 'Neon Dreams',
        'concept': 'A cyberpunk love story told through dance and light',
        'visual_elements': [
            'Holographic rain',
            'Neon-lit alleyways',
            'Digital butterflies',
            'Glitch effects during emotional peaks'
        ],
        'narrative': 'Two souls connect through a virtual reality interface'
    }

    # Create evaluation request
    print("\n1. Creating evaluation request for Freelancer director...")
    request = EvaluationRequest(
        session_id=session.session_id,
        phase_number=0,
        director_type=DirectorType.FREELANCER,
        evaluation_type="overall_design",
        context={'proposal': proposal}
    )

    # Execute evaluation (mock mode)
    print("\n2. Executing evaluation (mock mode)...")
    runner = CodexRunner(mock_mode=True)
    result = runner.execute_evaluation(request)

    # Display results
    print("\n3. Evaluation Results:")
    print(f"   Director: {result.director_type.value}")
    print(f"   Score: {result.score:.1f}/100")
    print(f"   Feedback: {result.feedback}")
    print(f"\n   Highlights:")
    for highlight in result.highlights:
        print(f"     + {highlight}")
    print(f"\n   Suggestions:")
    for suggestion in result.suggestions:
        print(f"     → {suggestion}")
    if result.concerns:
        print(f"\n   Concerns:")
        for concern in result.concerns:
            print(f"     ! {concern}")

    # Run evaluations from all directors
    print("\n" + "-" * 60)
    print("\n4. Running evaluations from all directors...")
    all_results = []
    for director_type in DirectorType:
        request = EvaluationRequest(
            session_id=session.session_id,
            phase_number=0,
            director_type=director_type,
            evaluation_type="overall_design",
            context={'proposal': proposal}
        )
        result = runner.execute_evaluation(request)
        all_results.append(result)
        print(f"   {director_type.value}: {result.score:.1f}/100")

    # Aggregate scores
    print("\n5. Aggregated scores:")
    aggregated = runner.aggregate_scores(all_results)
    print(f"   Average: {aggregated['average_score']:.1f}")
    print(f"   Min: {aggregated['min_score']:.1f}")
    print(f"   Max: {aggregated['max_score']:.1f}")
    print(f"   Count: {aggregated['count']}")


def example_loading_session():
    """Demonstrate loading an existing session"""
    print("\n" + "=" * 60)
    print("Example 4: Loading Existing Session")
    print("=" * 60)

    # Create and save a session
    print("\n1. Creating a new session...")
    session = SharedState.create_session()
    session_id = session.session_id
    print(f"   Session ID: {session_id}")

    # Add some data
    session.start_phase(0)
    session.set_phase_data(0, {'test': 'data'})
    session.complete_phase(0)
    print("   Added data and completed Phase 0")

    # Load the session
    print(f"\n2. Loading session {session_id}...")
    loaded_session = SharedState.load_session(session_id)
    print(f"   Session loaded successfully")
    print(f"   Phase 0 status: {loaded_session.phases[0].status}")
    print(f"   Phase 0 data: {loaded_session.phases[0].data}")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("MV Orchestra v2.8 - Core Functionality Examples")
    print("=" * 60)

    try:
        # Run examples
        example_session_management()
        example_director_profiles()
        example_evaluation_execution()
        example_loading_session()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
