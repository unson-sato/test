"""
Phase 8 Runner: Effects Code Generation

Generates Remotion effects code using 3 agents with different approaches.
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
from core.effects_generator import EffectsGenerator, EffectsCode, EffectsEvaluation
from core.agent_executor import AgentExecutor


logger = logging.getLogger(__name__)


# Phase 8 uses 3 effect agents
EFFECT_AGENTS = ["minimalist", "creative", "balanced"]


def run_phase8(
    session_id: str,
    mock_mode: bool = False
) -> Dict[str, Any]:
    """
    Run Phase 8: Generate Remotion effects code.

    Args:
        session_id: Session identifier
        mock_mode: If True, use mock effects code without running agents

    Returns:
        Phase 8 results dictionary
    """
    logger.info("=" * 70)
    logger.info("PHASE 8: Effects Code Generation")
    logger.info("=" * 70)

    # Load session
    session = SharedState.load_session(session_id)
    session_dir = get_session_dir(session_id)

    # Get context from previous phases
    phase1_data = session.get_phase_data(1)
    phase2_data = session.get_phase_data(2)
    phase3_data = session.get_phase_data(3)
    phase7_data = session.get_phase_data(7)

    if not all([phase1_data, phase2_data, phase3_data, phase7_data]):
        raise ValueError("Required phase data not found. Run phases 1-3 and 7 first.")

    # Build context for agents
    context = {
        "story": phase1_data.get("winner", {}),
        "sections": phase2_data.get("winner", {}).get("sections", []),
        "clips": phase3_data.get("winner", {}).get("clips", []),
        "video_sequence": phase7_data.get("final_sequence", {}),
        "total_duration": phase7_data.get("final_sequence", {}).get("duration", 0.0)
    }

    logger.info(f"Generating effects for {context['total_duration']:.1f}s video")
    logger.info(f"Sections: {len(context['sections'])}, Clips: {len(context['clips'])}")

    # Create output directory
    output_dir = session_dir / "phase8"
    ensure_dir(output_dir)

    # Initialize effects generator
    generator = EffectsGenerator()

    if mock_mode:
        logger.info("Running in MOCK MODE - using placeholder effects code")
        effects_codes = _generate_mock_effects()
        evaluation = _mock_evaluation(effects_codes)
    else:
        # Run 3 effect agents in parallel
        logger.info(f"\nGenerating effects code with {len(EFFECT_AGENTS)} agents...")

        agent_executor = AgentExecutor()
        agent_results = asyncio.run(
            _run_all_effect_agents(agent_executor, context, output_dir)
        )

        # Parse agent outputs into EffectsCode objects
        effects_codes = []
        for agent_name, result in agent_results.items():
            try:
                effects_code = generator.parse_agent_output(agent_name, result)
                effects_codes.append(effects_code)
                logger.info(f"  ✓ {agent_name}: {len(effects_code.effects_list)} effects")
            except Exception as e:
                logger.error(f"  ✗ {agent_name}: Failed to parse output - {e}")

        if not effects_codes:
            raise ValueError("No valid effects code generated")

        # Run evaluation agent
        logger.info(f"\nEvaluating {len(effects_codes)} effects code submissions...")

        evaluation_result = asyncio.run(
            _run_evaluation_agent(agent_executor, effects_codes, context, output_dir)
        )

        evaluation = generator.select_best_effects(effects_codes, evaluation_result)

    # Log results
    logger.info(f"\n{'=' * 70}")
    logger.info(f"EFFECTS CODE EVALUATION")
    logger.info(f"{'=' * 70}")
    logger.info(f"Winner: {evaluation.winner}")
    logger.info(f"Effects: {len(evaluation.winner_code.effects_list)}")
    logger.info(f"Scores:")
    for agent, score in evaluation.scores.items():
        logger.info(f"  {agent}: {score}/100")

    if evaluation.partial_adoptions:
        logger.info(f"\nPartial adoptions: {len(evaluation.partial_adoptions)}")
        for adoption in evaluation.partial_adoptions:
            logger.info(f"  - {adoption.get('feature', 'unknown')} from {adoption.get('from', 'unknown')}")

    # Merge effects code with partial adoptions
    final_code = generator.merge_effects_code(
        evaluation.winner_code,
        evaluation.partial_adoptions
    )

    # Save effects code to file
    effects_file = output_dir / "effects.tsx"
    with open(effects_file, 'w') as f:
        f.write(final_code)

    logger.info(f"\n✓ Effects code saved to: {effects_file}")

    # Save all submissions for reference
    submissions_dir = output_dir / "submissions"
    ensure_dir(submissions_dir)

    for code in effects_codes:
        submission_file = submissions_dir / f"{code.agent_name}.tsx"
        with open(submission_file, 'w') as f:
            f.write(code.code)

    # Prepare results
    phase8_results = {
        "winner": evaluation.winner,
        "winner_effects": evaluation.winner_code.effects_list,
        "scores": evaluation.scores,
        "reasoning": evaluation.reasoning,
        "partial_adoptions": evaluation.partial_adoptions,
        "submissions": [
            {
                "agent": code.agent_name,
                "effects_count": len(code.effects_list),
                "effects": code.effects_list,
                "complexity_score": code.complexity_score,
                "creativity_score": code.creativity_score,
                "performance_score": code.performance_score,
                "code_file": str(submissions_dir / f"{code.agent_name}.tsx")
            }
            for code in effects_codes
        ],
        "final_code_file": str(effects_file),
        "timestamp": get_iso_timestamp()
    }

    # Save results
    result_file = output_dir / "results.json"
    write_json(result_file, phase8_results)

    # Update session state
    session.mark_phase_started(8)
    session.mark_phase_completed(8, phase8_results)

    logger.info(f"\n✓ Phase 8 completed")
    logger.info(f"  Results saved to: {result_file}")

    return phase8_results


async def _run_all_effect_agents(
    agent_executor: AgentExecutor,
    context: Dict[str, Any],
    output_dir: Path
) -> Dict[str, Dict[str, Any]]:
    """Run all 3 effect agents in parallel"""

    async def run_agent(agent_name: str) -> tuple:
        logger.info(f"  Starting {agent_name} agent...")

        result = await agent_executor.run_director_async(
            director_type=agent_name,
            phase_num=8,
            context=context,
            output_dir=output_dir
        )

        logger.info(f"  ✓ {agent_name} completed")
        return (agent_name, result)

    # Run all agents in parallel
    tasks = [run_agent(agent) for agent in EFFECT_AGENTS]
    results = await asyncio.gather(*tasks)

    # Convert to dictionary
    return {agent_name: result for agent_name, result in results}


async def _run_evaluation_agent(
    agent_executor: AgentExecutor,
    effects_codes: List[EffectsCode],
    context: Dict[str, Any],
    output_dir: Path
) -> Dict[str, Any]:
    """Run evaluation agent to select winner"""

    # Prepare evaluation context
    eval_context = {
        **context,
        "submissions": [
            {
                "agent": code.agent_name,
                "effects": code.effects_list,
                "reasoning": code.reasoning,
                "complexity": code.complexity_score,
                "creativity": code.creativity_score,
                "performance": code.performance_score,
                "code_preview": code.code[:500] + "..." if len(code.code) > 500 else code.code
            }
            for code in effects_codes
        ]
    }

    result = await agent_executor.run_director_async(
        director_type="evaluation",
        phase_num=8,
        context=eval_context,
        output_dir=output_dir
    )

    return result


def _generate_mock_effects() -> List[EffectsCode]:
    """Generate mock effects code for testing"""
    mock_codes = []

    # Minimalist
    minimalist_code = """import React from 'react';
import { useCurrentFrame, interpolate } from 'remotion';

export const FadeIn: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 30], [0, 1], { extrapolateRight: 'clamp' });
  return <div style={{ opacity }}>{children}</div>;
};

export const FadeOut: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 30], [1, 0], { extrapolateRight: 'clamp' });
  return <div style={{ opacity }}>{children}</div>;
};
"""

    mock_codes.append(EffectsCode(
        agent_name="minimalist",
        code=minimalist_code,
        effects_list=["FadeIn", "FadeOut"],
        reasoning="Simple, clean effects for smooth transitions",
        complexity_score=0.3,
        creativity_score=0.4,
        performance_score=0.9
    ))

    # Creative
    creative_code = """import React from 'react';
import { useCurrentFrame, interpolate, spring } from 'remotion';

export const KaleidoscopeEffect: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const rotation = spring({ frame, fps: 30 }) * 360;
  return <div style={{ transform: `rotate(${rotation}deg)` }}>{children}</div>;
};

export const GlitchTransition: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const offset = Math.random() * 10 - 5;
  return <div style={{ transform: `translateX(${offset}px)` }}>{children}</div>;
};
"""

    mock_codes.append(EffectsCode(
        agent_name="creative",
        code=creative_code,
        effects_list=["KaleidoscopeEffect", "GlitchTransition"],
        reasoning="Bold, experimental effects for visual impact",
        complexity_score=0.8,
        creativity_score=0.9,
        performance_score=0.6
    ))

    # Balanced
    balanced_code = """import React, { useMemo } from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';

export const SmoothFadeSlide: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.ease)
  });
  const translateX = interpolate(frame, [0, 30], [-50, 0], {
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.ease)
  });
  return <div style={{ opacity, transform: `translateX(${translateX}px)` }}>{children}</div>;
};
"""

    mock_codes.append(EffectsCode(
        agent_name="balanced",
        code=balanced_code,
        effects_list=["SmoothFadeSlide"],
        reasoning="Professional effects balancing creativity and performance",
        complexity_score=0.6,
        creativity_score=0.7,
        performance_score=0.8
    ))

    return mock_codes


def _mock_evaluation(effects_codes: List[EffectsCode]) -> EffectsEvaluation:
    """Generate mock evaluation for testing"""
    return EffectsEvaluation(
        winner="balanced",
        winner_code=effects_codes[2],  # Balanced
        scores={
            "minimalist": 75,
            "creative": 82,
            "balanced": 88
        },
        reasoning="Balanced approach provides professional effects with good performance",
        partial_adoptions=[
            {
                "from": "creative",
                "feature": "KaleidoscopeEffect",
                "justification": "Adds visual interest to intro"
            }
        ]
    )
