"""
Phase 6 Runner: CLIP Quality Evaluation

Evaluates generated clips using CLIP and provides feedback for regeneration.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from core import (
    SharedState,
    get_session_dir,
    ensure_dir,
    write_json,
    read_json,
    get_iso_timestamp,
    get_project_root
)
from core.clip_evaluator import CLIPEvaluator, EvaluationResult
from core.mcp_clip_generator import MCPClipGenerator


logger = logging.getLogger(__name__)


def run_phase6(
    session_id: str,
    clip_model: str = "ViT-B/32",
    similarity_threshold: float = 0.75,
    technical_threshold: float = 0.70,
    max_regeneration_attempts: int = 2,
    mock_mode: bool = True
) -> Dict[str, Any]:
    """
    Run Phase 6: Evaluate clips and regenerate failing ones.

    Args:
        session_id: Session identifier
        clip_model: CLIP model to use
        similarity_threshold: Minimum CLIP similarity score
        technical_threshold: Minimum technical quality score
        max_regeneration_attempts: Maximum regeneration attempts per clip
        mock_mode: If True, use mock evaluation

    Returns:
        Phase 6 results dictionary
    """
    logger.info("=" * 70)
    logger.info("PHASE 6: CLIP Quality Evaluation")
    logger.info("=" * 70)

    # Load session
    session = SharedState.load_session(session_id)
    session_dir = get_session_dir(session_id)

    # Get Phase 5 results
    phase5_data = session.get_phase_data(5)
    if not phase5_data or "clips" not in phase5_data:
        raise ValueError("Phase 5 data not found. Run Phase 5 first.")

    generated_clips = phase5_data["clips"]
    successful_clips = [c for c in generated_clips if c["success"]]

    if not successful_clips:
        raise ValueError("No successful clips from Phase 5 to evaluate")

    logger.info(f"Evaluating {len(successful_clips)} clips from Phase 5")

    # Get Phase 3 clip designs for context
    phase3_data = session.get_phase_data(3)
    clip_designs = phase3_data["winner"]["clips"]
    clip_designs_by_id = {c["clip_id"]: c for c in clip_designs}

    # Initialize CLIP evaluator
    evaluator = CLIPEvaluator(
        clip_model=clip_model,
        similarity_threshold=similarity_threshold,
        technical_threshold=technical_threshold
    )

    # Prepare clips for evaluation
    clips_to_evaluate = []
    for clip_data in successful_clips:
        clip_id = clip_data["clip_id"]
        clip_path = Path(clip_data["path"])

        # Get original design
        design = clip_designs_by_id.get(clip_id, {})
        prompt = design.get("prompt", "")

        clips_to_evaluate.append((clip_path, prompt, design))

    # Initial evaluation
    logger.info(f"\nInitial evaluation of {len(clips_to_evaluate)} clips...")
    results = evaluator.evaluate_all_clips(clips_to_evaluate, mock_mode=mock_mode)

    # Track regeneration history
    regeneration_history = []

    # Regenerate failing clips
    failing_clips = evaluator.get_failing_clips(results)

    if failing_clips and max_regeneration_attempts > 0:
        logger.info(f"\n{len(failing_clips)} clips below quality threshold")
        logger.info("Starting regeneration process...")

        results = _regenerate_failing_clips(
            session_id=session_id,
            failing_clips=failing_clips,
            evaluator=evaluator,
            clip_designs_by_id=clip_designs_by_id,
            max_attempts=max_regeneration_attempts,
            mock_mode=mock_mode,
            regeneration_history=regeneration_history
        )

    # Final statistics
    final_passing = sum(1 for r in results if r.meets_threshold)
    final_failing = len(results) - final_passing

    logger.info(f"\n{'=' * 70}")
    logger.info(f"FINAL EVALUATION RESULTS")
    logger.info(f"{'=' * 70}")
    logger.info(f"Total clips: {len(results)}")
    logger.info(f"Passing: {final_passing} ({final_passing/len(results)*100:.1f}%)")
    logger.info(f"Failing: {final_failing} ({final_failing/len(results)*100:.1f}%)")

    # Save results
    phase6_results = {
        "total_clips": len(results),
        "passing_clips": final_passing,
        "failing_clips": final_failing,
        "quality_rate": final_passing / len(results) if results else 0.0,
        "evaluations": [
            {
                "clip_id": r.clip_id,
                "clip_path": str(r.clip_path),
                "overall_score": r.overall_score,
                "clip_similarity": r.clip_similarity,
                "technical_quality": r.technical_quality,
                "meets_threshold": r.meets_threshold,
                "issues": r.issues,
                "timestamp": r.timestamp
            }
            for r in results
        ],
        "regeneration_history": regeneration_history,
        "thresholds": {
            "clip_similarity": similarity_threshold,
            "technical_quality": technical_threshold
        },
        "timestamp": get_iso_timestamp()
    }

    # Save to session
    result_file = session_dir / "phase6" / "results.json"
    ensure_dir(result_file.parent)
    write_json(result_file, phase6_results)

    # Update session state
    session.mark_phase_started(6)
    session.mark_phase_completed(6, phase6_results)

    logger.info(f"\n✓ Phase 6 completed")
    logger.info(f"  Results saved to: {result_file}")

    if final_failing > 0:
        logger.warning(f"  ⚠ {final_failing} clips still below quality threshold after regeneration")

    return phase6_results


def _regenerate_failing_clips(
    session_id: str,
    failing_clips: List[EvaluationResult],
    evaluator: CLIPEvaluator,
    clip_designs_by_id: Dict[int, Dict[str, Any]],
    max_attempts: int,
    mock_mode: bool,
    regeneration_history: List[Dict[str, Any]]
) -> List[EvaluationResult]:
    """
    Regenerate failing clips with feedback.

    Returns:
        Updated list of all evaluation results
    """
    session = SharedState.load_session(session_id)
    session_dir = get_session_dir(session_id)

    # Load MCP config
    config_file = get_project_root() / "config" / "orchestrator_config.json"
    if config_file.exists():
        full_config = read_json(config_file)
        mcp_config = full_config.get("mcp", {})
    else:
        mcp_config = {}

    # Get Phase 4 strategies
    phase4_data = session.get_phase_data(4)
    strategies = None
    if phase4_data and "winner" in phase4_data:
        strategies = phase4_data["winner"].get("clip_strategies", [])

    # Initialize generator
    output_dir = session_dir / "phase6" / "regenerated_clips"
    ensure_dir(output_dir)

    generator = MCPClipGenerator(
        mcp_config=mcp_config,
        output_dir=output_dir,
        max_parallel=1,  # Regenerate one at a time
        max_retries=2
    )

    # Track all results (passing + regenerated)
    all_results = []

    # Get all original results
    phase5_data = session.get_phase_data(5)
    generated_clips = phase5_data["clips"]
    successful_clips = [c for c in generated_clips if c["success"]]

    # Create initial evaluation mapping
    results_by_id = {r.clip_id: r for r in evaluator.evaluate_all_clips(
        [
            (Path(c["path"]), clip_designs_by_id[c["clip_id"]].get("prompt", ""),
             clip_designs_by_id[c["clip_id"]])
            for c in successful_clips
        ],
        mock_mode=mock_mode
    )}

    # Regenerate each failing clip
    for failing_result in failing_clips:
        clip_id = failing_result.clip_id
        design = clip_designs_by_id.get(clip_id, {})

        logger.info(f"\nRegenerating clip {clip_id} (score: {failing_result.overall_score:.2f})")

        # Generate feedback
        feedback = evaluator.generate_feedback(failing_result)

        # Find strategy for this clip
        strategy = None
        if strategies:
            strategy = next((s for s in strategies if s.get("clip_id") == clip_id), None)

        # Attempt regeneration
        best_result = failing_result

        for attempt in range(max_regeneration_attempts):
            logger.info(f"  Attempt {attempt + 1}/{max_regeneration_attempts}")

            # Regenerate
            if mock_mode:
                # Mock regeneration
                import time
                time.sleep(0.1)
                new_path = output_dir / f"clip_{clip_id:03d}_regen_{attempt}.mp4"
                from core.mcp_clip_generator import VideoClip, GenerationResult

                new_clip = VideoClip(
                    clip_id=clip_id,
                    path=new_path,
                    design=design,
                    mcp_server="mock_server",
                    generation_time=0.1,
                    metadata={"regeneration": True, "attempt": attempt, "feedback": feedback}
                )

                gen_result = GenerationResult(
                    clip_id=clip_id,
                    success=True,
                    clip=new_clip,
                    attempts=1,
                    total_time=0.1
                )
            else:
                # Real regeneration via MCP
                gen_result = asyncio.run(
                    generator.generate_clip(design, clip_id, strategy, feedback)
                )

            if not gen_result.success:
                logger.warning(f"  Regeneration failed: {gen_result.error}")
                continue

            # Evaluate new clip
            new_result = evaluator.evaluate_clip(
                gen_result.clip.path,
                design.get("prompt", ""),
                design,
                mock_mode=mock_mode
            )

            logger.info(f"  New score: {new_result.overall_score:.2f} (was {failing_result.overall_score:.2f})")

            # Track regeneration
            regeneration_history.append({
                "clip_id": clip_id,
                "attempt": attempt + 1,
                "old_score": failing_result.overall_score,
                "new_score": new_result.overall_score,
                "improvement": new_result.overall_score - failing_result.overall_score,
                "feedback": feedback,
                "timestamp": get_iso_timestamp()
            })

            # Keep best result
            if new_result.overall_score > best_result.overall_score:
                best_result = new_result

            # If meets threshold, stop regenerating
            if new_result.meets_threshold:
                logger.info(f"  ✓ Clip {clip_id} now meets quality threshold")
                break

        # Update result for this clip
        results_by_id[clip_id] = best_result

    # Return all results
    return list(results_by_id.values())
