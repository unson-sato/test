#!/usr/bin/env python3
"""
Example: Programmatic Control

This example demonstrates full programmatic control over the pipeline:
- Manual phase execution
- Custom evaluation logic
- Direct access to session state
- Filtering and analyzing results

Usage:
    python3 examples/example_programmatic.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import (
    SharedState,
    DirectorType,
    CodexRunner,
    EvaluationRequest,
    read_json,
    write_json,
    get_session_dir
)


def run_custom_phase0(session_id: str, analysis_path: str):
    """
    Run Phase 0 with custom logic.

    Instead of using the standard run_phase0, this demonstrates
    how to manually control the evaluation process.
    """
    print("\n" + "=" * 70)
    print("CUSTOM PHASE 0 EXECUTION")
    print("=" * 70)

    # Load session and analysis
    session = SharedState.load_session(session_id)
    analysis = read_json(analysis_path)

    # Start Phase 0
    session.start_phase(0)

    # Create evaluation context
    context = {
        'song_analysis': analysis,
        'target': 'overall_mv_concept'
    }

    # Run evaluations from each director
    runner = CodexRunner(mock_mode=True)
    results = []

    print("\n→ Running evaluations from all directors...")

    for director_type in DirectorType:
        print(f"  Evaluating: {director_type.value}")

        request = EvaluationRequest(
            session_id=session_id,
            phase_number=0,
            director_type=director_type,
            evaluation_type="overall_design",
            context=context
        )

        result = runner.execute_evaluation(request)
        results.append(result)

        print(f"    Score: {result.score:.1f}/100")

    # Custom winner selection: prefer innovative directors
    print("\n→ Selecting winner with custom criteria...")

    # Filter to high-scoring proposals
    high_scores = [r for r in results if r.score >= 75]

    if high_scores:
        # Among high scores, prefer more innovative directors
        from core import get_director_profile

        winner = max(
            high_scores,
            key=lambda r: (
                r.score * 0.7 +  # 70% score weight
                get_director_profile(r.director_type).innovation_focus * 3  # 30% innovation weight
            )
        )
    else:
        # Fallback to highest score
        winner = max(results, key=lambda r: r.score)

    print(f"  Winner: {winner.director_type.value}")
    print(f"  Score: {winner.score:.1f}/100")

    # Save winner to session
    session.set_phase_data(0, {
        'winner': {
            'director': winner.director_type.value,
            'score': winner.score,
            'concept': winner.feedback,
            'highlights': winner.highlights,
            'suggestions': winner.suggestions
        },
        'all_results': [
            {
                'director': r.director_type.value,
                'score': r.score
            }
            for r in results
        ]
    })

    session.complete_phase(0)

    return winner, results


def analyze_results(results: list):
    """Analyze evaluation results."""
    print("\n" + "=" * 70)
    print("RESULTS ANALYSIS")
    print("=" * 70)

    # Score distribution
    scores = [r.score for r in results]
    print(f"\nScore Statistics:")
    print(f"  Average: {sum(scores) / len(scores):.1f}")
    print(f"  Min: {min(scores):.1f}")
    print(f"  Max: {max(scores):.1f}")
    print(f"  Range: {max(scores) - min(scores):.1f}")

    # Sort by score
    sorted_results = sorted(results, key=lambda r: r.score, reverse=True)

    print("\n Ranking:")
    for i, result in enumerate(sorted_results, 1):
        print(f"  {i}. {result.director_type.value:12} - {result.score:.1f}/100")

    # Common themes in highlights
    print("\nCommon Highlights:")
    all_highlights = []
    for r in results:
        all_highlights.extend(r.highlights)

    # Simple frequency analysis
    from collections import Counter
    words = ' '.join(all_highlights).lower().split()
    common_words = Counter(words).most_common(10)

    for word, count in common_words:
        if len(word) > 4:  # Only significant words
            print(f"  '{word}': {count} mentions")


def export_results_to_report(session_id: str):
    """Export session results to a formatted report."""
    print("\n" + "=" * 70)
    print("EXPORTING RESULTS")
    print("=" * 70)

    session = SharedState.load_session(session_id)
    session_dir = get_session_dir(session_id)

    # Create report
    report = {
        'session_id': session_id,
        'summary': session.get_session_summary(),
        'phases': {}
    }

    for phase_num, phase_data in session.phases.items():
        report['phases'][f'phase_{phase_num}'] = {
            'status': phase_data.status,
            'started_at': phase_data.started_at,
            'completed_at': phase_data.completed_at,
            'data': phase_data.data
        }

    # Save report
    report_path = session_dir / 'custom_report.json'
    write_json(report_path, report)

    print(f"  ✓ Report saved to: {report_path}")

    return report


def main():
    """Run programmatic control example."""
    print("=" * 70)
    print("MV ORCHESTRA v2.8 - Programmatic Control Example")
    print("=" * 70)

    # 1. Create session
    session_id = "example_programmatic"
    print(f"\n1. Creating session: {session_id}")

    from core import ensure_dir
    session = SharedState(session_id=session_id)
    ensure_dir(session.session_dir)
    session.save_session()

    # 2. Run custom Phase 0
    analysis_path = "sample_analysis.json"
    winner, all_results = run_custom_phase0(session_id, analysis_path)

    # 3. Analyze results
    analyze_results(all_results)

    # 4. Export custom report
    report = export_results_to_report(session_id)

    # 5. Summary
    print("\n" + "=" * 70)
    print("PROGRAMMATIC CONTROL COMPLETE")
    print("=" * 70)
    print("\nThis example demonstrated:")
    print("  ✓ Manual phase execution")
    print("  ✓ Custom winner selection logic")
    print("  ✓ Results analysis")
    print("  ✓ Custom report generation")
    print(f"\nSession saved to: {get_session_dir(session_id)}")


if __name__ == "__main__":
    main()
