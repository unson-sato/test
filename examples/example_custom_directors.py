#!/usr/bin/env python3
"""
Example: Working with Custom Directors

This example shows how to:
- Access and examine director profiles
- Understand director characteristics
- Manually select proposals from specific directors

Usage:
    python3 examples/example_custom_directors.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import (
    DirectorType,
    get_director_profile,
    get_all_profiles,
    get_profiles_dict
)


def display_director_profile(director_type: DirectorType):
    """Display detailed profile for a director."""
    profile = get_director_profile(director_type)

    print("\n" + "=" * 70)
    print(f"{profile.name_en} ({profile.name_ja})")
    print("=" * 70)

    print(f"\nType: {profile.director_type.value}")
    print(f"Organization: {profile.organization}")

    print("\n--- Characteristics ---")
    print(f"Risk Tolerance:     {'█' * profile.risk_tolerance}{'░' * (10 - profile.risk_tolerance)} {profile.risk_tolerance}/10")
    print(f"Commercial Focus:   {'█' * profile.commercial_focus}{'░' * (10 - profile.commercial_focus)} {profile.commercial_focus}/10")
    print(f"Artistic Focus:     {'█' * profile.artistic_focus}{'░' * (10 - profile.artistic_focus)} {profile.artistic_focus}/10")
    print(f"Innovation Focus:   {'█' * profile.innovation_focus}{'░' * (10 - profile.innovation_focus)} {profile.innovation_focus}/10")
    print(f"Budget Consciousness: {'█' * profile.budget_consciousness}{'░' * (10 - profile.budget_consciousness)} {profile.budget_consciousness}/10")

    print("\n--- Strengths ---")
    for i, strength in enumerate(profile.strengths, 1):
        print(f"{i}. {strength}")

    print("\n--- Creative Tendencies ---")
    for i, tendency in enumerate(profile.creative_tendencies, 1):
        print(f"{i}. {tendency}")

    print("\n--- Common Phrases ---")
    for i, phrase in enumerate(profile.common_phrases[:3], 1):
        print(f"{i}. \"{phrase}\"")


def compare_directors():
    """Compare all directors side by side."""
    print("\n" + "=" * 70)
    print("DIRECTOR COMPARISON")
    print("=" * 70)

    profiles = get_all_profiles()

    # Compare characteristics
    print("\n{:<15} {:>8} {:>8} {:>8} {:>8}".format(
        "Director", "Risk", "Commerc", "Art", "Innov"
    ))
    print("-" * 70)

    for profile in profiles:
        print("{:<15} {:>8} {:>8} {:>8} {:>8}".format(
            profile.name_en[:14],
            profile.risk_tolerance,
            profile.commercial_focus,
            profile.artistic_focus,
            profile.innovation_focus
        ))


def recommend_director_for_project(
    risk_level: str,
    budget_level: str,
    artistic_priority: str
) -> DirectorType:
    """
    Recommend a director based on project requirements.

    Args:
        risk_level: 'low', 'medium', 'high'
        budget_level: 'low', 'medium', 'high'
        artistic_priority: 'commercial', 'balanced', 'artistic'

    Returns:
        Recommended director type
    """
    profiles = get_all_profiles()

    # Score each director
    scores = {}

    for profile in profiles:
        score = 0

        # Risk matching
        if risk_level == 'low' and profile.risk_tolerance <= 4:
            score += 3
        elif risk_level == 'medium' and 4 < profile.risk_tolerance <= 7:
            score += 3
        elif risk_level == 'high' and profile.risk_tolerance > 7:
            score += 3

        # Budget matching
        if budget_level == 'low' and profile.budget_consciousness >= 7:
            score += 2
        elif budget_level == 'high' and profile.budget_consciousness <= 4:
            score += 2

        # Artistic priority matching
        if artistic_priority == 'commercial' and profile.commercial_focus >= 7:
            score += 3
        elif artistic_priority == 'artistic' and profile.artistic_focus >= 8:
            score += 3
        elif artistic_priority == 'balanced':
            if 5 <= profile.commercial_focus <= 7 and 5 <= profile.artistic_focus <= 7:
                score += 3

        scores[profile.director_type] = score

    # Return highest scoring director
    best_director = max(scores.items(), key=lambda x: x[1])
    return best_director[0]


def main():
    """Run custom directors example."""
    print("=" * 70)
    print("MV ORCHESTRA v2.8 - Custom Directors Example")
    print("=" * 70)

    # 1. Display all director profiles
    print("\n--- ALL DIRECTOR PROFILES ---")
    for director_type in DirectorType:
        display_director_profile(director_type)

    # 2. Compare directors
    compare_directors()

    # 3. Recommend director for different projects
    print("\n" + "=" * 70)
    print("DIRECTOR RECOMMENDATIONS")
    print("=" * 70)

    scenarios = [
        {
            'name': 'Safe Commercial Project',
            'risk': 'low',
            'budget': 'high',
            'artistic': 'commercial'
        },
        {
            'name': 'Experimental Art Piece',
            'risk': 'high',
            'budget': 'low',
            'artistic': 'artistic'
        },
        {
            'name': 'Balanced Mainstream MV',
            'risk': 'medium',
            'budget': 'medium',
            'artistic': 'balanced'
        }
    ]

    for scenario in scenarios:
        recommended = recommend_director_for_project(
            scenario['risk'],
            scenario['budget'],
            scenario['artistic']
        )
        profile = get_director_profile(recommended)

        print(f"\n{scenario['name']}:")
        print(f"  Requirements: Risk={scenario['risk']}, Budget={scenario['budget']}, Priority={scenario['artistic']}")
        print(f"  → Recommended: {profile.name_en} ({profile.director_type.value})")


if __name__ == "__main__":
    main()
