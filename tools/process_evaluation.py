#!/usr/bin/env python3
"""
Process Evaluation Helper Script

This script helps process evaluation prompts in Claude Code mode.
It shows pending evaluations and guides you through the workflow.

Usage:
    python3 tools/process_evaluation.py <session_id>
    python3 tools/process_evaluation.py <session_id> --validate

Examples:
    # List all pending evaluations
    python3 tools/process_evaluation.py my_session

    # Validate existing results
    python3 tools/process_evaluation.py my_session --validate

    # Show next evaluation to process
    python3 tools/process_evaluation.py my_session --next
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import get_evaluations_dir


def find_evaluations(session_id: str) -> Tuple[List[Path], List[Path], List[Path]]:
    """
    Find evaluation prompts and results for a session.

    Returns:
        (all_prompts, completed, pending)
    """
    eval_dir = get_evaluations_dir(session_id)
    prompts_dir = eval_dir / "prompts"
    results_dir = eval_dir / "results"

    if not prompts_dir.exists():
        return [], [], []

    all_prompts = list(prompts_dir.glob("*.txt"))
    completed = []
    pending = []

    for prompt_file in all_prompts:
        result_file = results_dir / prompt_file.name.replace("_prompt.txt", "_result.json")
        if result_file.exists():
            completed.append(prompt_file)
        else:
            pending.append(prompt_file)

    return all_prompts, completed, pending


def validate_result(result_file: Path) -> Tuple[bool, str]:
    """
    Validate a result JSON file.

    Returns:
        (is_valid, message)
    """
    required_fields = [
        'total_score',
        'recommendation',
        'summary',
        'what_works',
        'what_needs_work'
    ]

    try:
        with open(result_file) as f:
            data = json.load(f)

        # Check required fields
        missing = [f for f in required_fields if f not in data]
        if missing:
            return False, f"Missing fields: {', '.join(missing)}"

        # Check score range
        if not (0 <= data['total_score'] <= 10):
            return False, f"total_score must be 0-10, got: {data['total_score']}"

        # Check recommendation
        valid_recs = ['APPROVE', 'NEEDS REVISION', 'REJECT']
        if data['recommendation'] not in valid_recs:
            return False, f"recommendation must be one of {valid_recs}"

        return True, f"Valid (score: {data['total_score']}/10, {data['recommendation']})"

    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def print_evaluation_status(session_id: str):
    """Print status of all evaluations."""
    all_prompts, completed, pending = find_evaluations(session_id)

    if not all_prompts:
        print(f"No evaluation prompts found for session: {session_id}")
        print(f"Expected location: {get_evaluations_dir(session_id) / 'prompts'}")
        return

    print("=" * 70)
    print(f"EVALUATION STATUS: {session_id}")
    print("=" * 70)
    print(f"Total prompts: {len(all_prompts)}")
    print(f"Completed: {len(completed)}")
    print(f"Pending: {len(pending)}")
    print("=" * 70)

    if completed:
        print("\nCOMPLETED EVALUATIONS:")
        print("-" * 70)
        for i, prompt_file in enumerate(completed, 1):
            result_file = prompt_file.parent.parent / "results" / prompt_file.name.replace("_prompt.txt", "_result.json")
            is_valid, msg = validate_result(result_file)
            status = "✓" if is_valid else "✗"
            print(f"{i}. {status} {prompt_file.name}")
            print(f"   {msg}")

    if pending:
        print("\nPENDING EVALUATIONS:")
        print("-" * 70)
        for i, prompt_file in enumerate(pending, 1):
            result_file = prompt_file.parent.parent / "results" / prompt_file.name.replace("_prompt.txt", "_result.json")
            print(f"{i}. {prompt_file.name}")
            print(f"   Prompt: {prompt_file}")
            print(f"   Result: {result_file}")


def show_next_evaluation(session_id: str):
    """Show the next pending evaluation to process."""
    _, _, pending = find_evaluations(session_id)

    if not pending:
        print("✓ All evaluations completed!")
        return

    prompt_file = pending[0]
    result_file = prompt_file.parent.parent / "results" / prompt_file.name.replace("_prompt.txt", "_result.json")

    print("=" * 70)
    print("NEXT EVALUATION TO PROCESS")
    print("=" * 70)
    print(f"File: {prompt_file.name}")
    print(f"\n1. Read prompt:")
    print(f"   {prompt_file}")
    print(f"\n2. Process in Claude Code (see CLAUDE_CODE_GUIDE.md)")
    print(f"\n3. Save result to:")
    print(f"   {result_file}")
    print("=" * 70)
    print("\nPrompt preview:")
    print("-" * 70)

    with open(prompt_file) as f:
        content = f.read()
        # Show first 500 chars
        preview = content[:500]
        if len(content) > 500:
            preview += f"\n\n... ({len(content) - 500} more characters) ..."
        print(preview)

    print("-" * 70)


def validate_all_results(session_id: str):
    """Validate all result files."""
    _, completed, _ = find_evaluations(session_id)

    if not completed:
        print("No completed evaluations to validate.")
        return

    print("=" * 70)
    print("VALIDATING RESULTS")
    print("=" * 70)

    valid_count = 0
    invalid_count = 0

    for prompt_file in completed:
        result_file = prompt_file.parent.parent / "results" / prompt_file.name.replace("_prompt.txt", "_result.json")
        is_valid, msg = validate_result(result_file)

        if is_valid:
            valid_count += 1
            print(f"✓ {result_file.name}")
            print(f"  {msg}")
        else:
            invalid_count += 1
            print(f"✗ {result_file.name}")
            print(f"  {msg}")

    print("=" * 70)
    print(f"Valid: {valid_count}")
    print(f"Invalid: {invalid_count}")
    print("=" * 70)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Process evaluation prompts for MV Orchestra",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show evaluation status
  python3 tools/process_evaluation.py my_session

  # Show next evaluation to process
  python3 tools/process_evaluation.py my_session --next

  # Validate all results
  python3 tools/process_evaluation.py my_session --validate
        """
    )

    parser.add_argument(
        'session_id',
        help='Session ID to process'
    )
    parser.add_argument(
        '--next',
        action='store_true',
        help='Show next pending evaluation'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate all result files'
    )

    args = parser.parse_args()

    if args.validate:
        validate_all_results(args.session_id)
    elif args.next:
        show_next_evaluation(args.session_id)
    else:
        print_evaluation_status(args.session_id)


if __name__ == "__main__":
    main()
