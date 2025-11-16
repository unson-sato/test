"""
Phase 4: Generation Mode & Prompt Strategy Runner

This module implements the generation strategy phase where directors
select AI generation modes and develop prompt strategies for each clip.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from core import (
    SharedState,
    DirectorType,
    CodexRunner,
    EvaluationRequest,
    get_director_profile,
    read_json,
    write_json,
    ensure_dir,
    get_iso_timestamp
)
from .generation_modes import (
    GenerationMode,
    get_mode_spec,
    recommend_mode,
    get_all_modes_dict
)
from .prompt_builder import (
    PromptBuilder,
    create_character_prompt,
    create_establishing_prompt,
    create_transition_prompt,
    get_default_negative_prompts,
    get_quality_presets
)
from .asset_manager import (
    AssetManager,
    AssetType,
    create_character_consistency_asset,
    create_style_guide_asset,
    create_audio_segment_asset
)


class Phase4Runner:
    """
    Runner for Phase 4: Generation Mode & Prompt Strategy.

    This class orchestrates the multi-director competition for
    generation strategy planning.
    """

    def __init__(self, session_id: str, mock_mode: bool = True):
        """
        Initialize Phase 4 runner.

        Args:
            session_id: Session identifier
            mock_mode: Whether to use mock evaluations
        """
        self.session_id = session_id
        self.mock_mode = mock_mode
        self.session = SharedState.load_session(session_id)
        self.codex_runner = CodexRunner(mock_mode=mock_mode)
        self.asset_manager = AssetManager(session_id)

        # Load previous phase data
        self.phase0_data = self.session.get_phase_data(0).data
        self.phase1_data = self.session.get_phase_data(1).data
        self.phase2_data = self.session.get_phase_data(2).data
        self.phase3_data = self.session.get_phase_data(3).data

    def run(self) -> Dict[str, Any]:
        """
        Execute Phase 4: Generation Strategy.

        Returns:
            Phase 4 results including proposals, evaluations, and winner
        """
        print(f"\n{'='*60}")
        print("Phase 4: Generation Mode & Prompt Strategy")
        print(f"{'='*60}")
        print(f"Session ID: {self.session_id}")
        print(f"Mode: {'Mock' if self.mock_mode else 'Real'}")

        # Mark phase as started
        self.session.start_phase(4)

        try:
            # Step 1: Extract clips from Phase 3
            print("\n[1/6] Extracting clips from Phase 3...")
            clips = self._extract_clips()
            print(f"      Found {len(clips)} clips to process")

            # Step 2: Generate proposals from each director
            print("\n[2/6] Generating generation strategies from 5 directors...")
            proposals = self._generate_proposals(clips)
            print(f"      Generated {len(proposals)} proposals")

            # Step 3: Directors evaluate each other's proposals
            print("\n[3/6] Directors evaluating all proposals...")
            evaluations = self._evaluate_proposals(proposals)
            print(f"      Collected {len(evaluations)} evaluations")

            # Step 4: Select winner
            print("\n[4/6] Selecting winning generation strategy...")
            winner = self._select_winner(proposals, evaluations)
            print(f"      Winner: {winner['director'].upper()}")
            print(f"      Score: {winner['total_score']:.1f}/100")

            # Step 5: Build asset pipeline
            print("\n[5/6] Building asset pipeline...")
            asset_pipeline = self._build_asset_pipeline(winner['proposal'], clips)
            print(f"      Total assets: {asset_pipeline['summary']['total_assets']}")

            # Step 6: Save results
            print("\n[6/6] Saving Phase 4 results...")
            results = {
                'phase': 4,
                'phase_name': 'Generation Strategy',
                'timestamp': get_iso_timestamp(),
                'clips': clips,
                'proposals': proposals,
                'evaluations': evaluations,
                'winner': winner,
                'asset_pipeline': asset_pipeline,
                'generation_modes_available': get_all_modes_dict()
            }

            self.session.set_phase_data(4, results)
            self.session.complete_phase(4)

            print("\n" + "="*60)
            print("Phase 4 completed successfully!")
            print("="*60)

            return results

        except Exception as e:
            print(f"\nError in Phase 4: {e}")
            self.session.fail_phase(4, {'error': str(e)})
            raise

    def _extract_clips(self) -> List[Dict[str, Any]]:
        """
        Extract clips from Phase 3 data.

        Returns:
            List of clip dictionaries
        """
        # Get winner's clip division from Phase 3
        if 'winner' in self.phase3_data and 'proposal' in self.phase3_data['winner']:
            winner_proposal = self.phase3_data['winner']['proposal']

            # Phase 3 stores clips directly in proposal
            if 'clips' in winner_proposal:
                return winner_proposal['clips']

        # Fallback: create sample clips if Phase 3 data unavailable
        return self._create_sample_clips()

    def _create_sample_clips(self) -> List[Dict[str, Any]]:
        """
        Create sample clips for testing/demo.

        Returns:
            List of sample clip dictionaries
        """
        return [
            {
                'clip_id': 'clip_001',
                'start_time': 0.0,
                'end_time': 3.0,
                'duration': 3.0,
                'description': 'Opening establishing shot',
                'section_name': 'Intro',
                'section_mood': 'mysterious',
                'clip_type': 'establishing'
            },
            {
                'clip_id': 'clip_002',
                'start_time': 3.0,
                'end_time': 6.0,
                'duration': 3.0,
                'description': 'Character introduction',
                'section_name': 'Verse 1',
                'section_mood': 'energetic',
                'clip_type': 'performance'
            },
            {
                'clip_id': 'clip_003',
                'start_time': 6.0,
                'end_time': 8.0,
                'duration': 2.0,
                'description': 'Abstract transition',
                'section_name': 'Verse 1',
                'section_mood': 'energetic',
                'clip_type': 'transition'
            }
        ]

    def _generate_proposals(self, clips: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate generation strategy proposals from all directors.

        Args:
            clips: List of clips to process

        Returns:
            List of director proposals
        """
        proposals = []

        for director_type in DirectorType:
            print(f"      - {director_type.value.upper()}...", end=" ")

            proposal = self._generate_director_proposal(director_type, clips)
            proposals.append(proposal)

            print(f"✓ ({len(proposal['generation_strategies'])} strategies)")

        return proposals

    def _generate_director_proposal(
        self,
        director_type: DirectorType,
        clips: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a proposal from a specific director.

        Args:
            director_type: Type of director
            clips: List of clips

        Returns:
            Director's generation strategy proposal
        """
        profile = get_director_profile(director_type)

        # Load director's Phase 4 prompt (if available)
        prompt_path = Path(f".claude/prompts_v2/phase4_{director_type.value}.md")
        director_guidance = ""
        if prompt_path.exists():
            with open(prompt_path, 'r') as f:
                director_guidance = f.read()

        # Generate strategies for each clip
        generation_strategies = []
        for clip in clips:
            strategy = self._create_clip_strategy(director_type, clip)
            generation_strategies.append(strategy)

        # Create overall proposal
        proposal = {
            'director': director_type.value,
            'director_profile': profile.to_dict(),
            'generation_strategies': generation_strategies,
            'overall_strategy': self._summarize_strategy(director_type, generation_strategies),
            'budget_estimate': self._estimate_budget(generation_strategies),
            'timeline_estimate': self._estimate_timeline(generation_strategies)
        }

        return proposal

    def _create_clip_strategy(
        self,
        director_type: DirectorType,
        clip: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create generation strategy for a single clip.

        Args:
            director_type: Type of director
            clip: Clip information

        Returns:
            Generation strategy for the clip
        """
        profile = get_director_profile(director_type)
        clip_id = clip.get('clip_id', 'unknown')
        clip_type = clip.get('clip_type', 'general')

        # Recommend generation mode based on director and clip
        if director_type == DirectorType.CORPORATE:
            # Corporate prefers traditional or hybrid
            mode = GenerationMode.HYBRID if clip_type != 'performance' else GenerationMode.TRADITIONAL
        elif director_type == DirectorType.FREELANCER:
            # Freelancer experiments with AI
            mode = recommend_mode(clip_type, budget_level="medium", quality_priority=False)
        elif director_type == DirectorType.VETERAN:
            # Veteran prefers traditional
            mode = GenerationMode.TRADITIONAL if clip_type in ['performance', 'emotional'] else GenerationMode.HYBRID
        elif director_type == DirectorType.AWARD_WINNER:
            # Award winner balances quality and innovation
            mode = recommend_mode(clip_type, budget_level="high", quality_priority=True)
        else:  # NEWCOMER
            # Newcomer tries cutting-edge AI
            mode = GenerationMode.VEO2 if clip_type != 'transition' else GenerationMode.RUNWAY_GEN3

        mode_spec = get_mode_spec(mode)

        # Build prompt based on clip type
        if clip_type == 'performance' or clip_type == 'character':
            prompt_template = create_character_prompt(
                character_name="Main character",
                action=clip.get('description', 'performing'),
                setting=clip.get('section_name', 'scene'),
                emotion=clip.get('section_mood'),
                camera_angle="medium shot"
            )
        elif clip_type == 'establishing':
            prompt_template = create_establishing_prompt(
                location=clip.get('description', 'urban landscape'),
                time_of_day="golden hour",
                mood=clip.get('section_mood', 'cinematic'),
                camera_movement="slow push in"
            )
        elif clip_type == 'transition':
            prompt_template = create_transition_prompt(
                transition_type="abstract",
                from_scene="previous scene",
                to_scene="next scene",
                style=clip.get('section_mood', 'smooth')
            )
        else:
            # Generic prompt
            builder = PromptBuilder()
            builder.set_base(clip.get('description', 'cinematic shot'))
            builder.add_quality("high quality", "cinematic")
            prompt_template = builder.build()

        # Create strategy
        strategy = {
            'clip_id': clip_id,
            'clip_type': clip_type,
            'start_time': clip.get('start_time', 0),
            'end_time': clip.get('end_time', 0),
            'duration': clip.get('duration', 0),
            'generation_mode': mode.value,
            'generation_mode_spec': mode_spec.to_dict(),
            'prompt_template': prompt_template.to_dict(),
            'prompt_strategy': self._get_prompt_strategy(director_type, mode),
            'assets_required': self._get_required_assets(clip_id, mode, clip_type),
            'consistency_requirements': {
                'character_consistency': 'high' if clip_type in ['performance', 'character'] else 'medium',
                'background_consistency': 'medium',
                'style_consistency': 'high',
                'method': 'visual_reference'
            },
            'variance_params': {
                'camera_angle_variance': 0.2 if director_type != DirectorType.VETERAN else 0.1,
                'lighting_variance': 0.3,
                'motion_variance': 0.15
            },
            'estimated_cost': mode_spec.typical_cost_per_clip,
            'estimated_time': mode_spec.typical_turnaround
        }

        return strategy

    def _get_prompt_strategy(self, director_type: DirectorType, mode: GenerationMode) -> str:
        """Get prompt strategy description based on director and mode."""
        if director_type == DirectorType.CORPORATE:
            return "Highly detailed, specific prompts to minimize variation and ensure brand safety"
        elif director_type == DirectorType.FREELANCER:
            return "Creative prompts with room for AI interpretation and artistic variance"
        elif director_type == DirectorType.VETERAN:
            return "Traditional cinematography principles translated to AI prompts"
        elif director_type == DirectorType.AWARD_WINNER:
            return "Sophisticated prompts balancing artistic vision with technical precision"
        else:  # NEWCOMER
            return "Experimental prompts pushing AI capabilities and exploring new aesthetics"

    def _get_required_assets(
        self,
        clip_id: str,
        mode: GenerationMode,
        clip_type: str
    ) -> List[Dict[str, str]]:
        """Get list of required assets for a clip."""
        assets = []

        # Character reference for character-focused clips
        if clip_type in ['performance', 'character']:
            assets.append({
                'type': 'character_reference',
                'description': 'Character appearance and consistency reference',
                'source': 'Phase 1 character design'
            })

        # Style guide for all clips
        assets.append({
            'type': 'style_guide',
            'description': 'Color palette and visual style guide',
            'source': 'Phase 0 overall design'
        })

        # Mode-specific assets
        if mode == GenerationMode.IMAGE_TO_VIDEO:
            assets.append({
                'type': 'reference_image',
                'description': 'Starting frame for image-to-video generation',
                'source': 'Generated or photographed'
            })

        if mode == GenerationMode.VIDEO_TO_VIDEO:
            assets.append({
                'type': 'source_video',
                'description': 'Source footage for style transfer',
                'source': 'Traditional shooting'
            })

        return assets

    def _summarize_strategy(
        self,
        director_type: DirectorType,
        strategies: List[Dict[str, Any]]
    ) -> str:
        """Create overall strategy summary."""
        mode_counts = {}
        for strategy in strategies:
            mode = strategy['generation_mode']
            mode_counts[mode] = mode_counts.get(mode, 0) + 1

        summary_parts = []
        for mode, count in sorted(mode_counts.items(), key=lambda x: x[1], reverse=True):
            pct = (count / len(strategies)) * 100
            summary_parts.append(f"{mode}: {count} clips ({pct:.1f}%)")

        return f"{director_type.value.upper()} strategy - " + ", ".join(summary_parts)

    def _estimate_budget(self, strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate total budget for generation strategies."""
        # Simple estimation based on mode specs
        total_min = 0
        total_max = 0

        for strategy in strategies:
            cost_range = strategy.get('estimated_cost', '$0-0')
            # Parse cost range (e.g., "$50-150")
            try:
                costs = cost_range.replace('$', '').replace('+', '').split('-')
                if len(costs) == 2:
                    total_min += float(costs[0])
                    total_max += float(costs[1])
                elif len(costs) == 1:
                    total_min += float(costs[0])
                    total_max += float(costs[0])
            except:
                pass

        return {
            'estimated_range': f"${total_min:.0f}-${total_max:.0f}",
            'minimum': total_min,
            'maximum': total_max,
            'currency': 'USD'
        }

    def _estimate_timeline(self, strategies: List[Dict[str, Any]]) -> str:
        """Estimate timeline for generation."""
        # Find longest turnaround time
        max_days = 0
        for strategy in strategies:
            turnaround = strategy.get('estimated_time', '1 day')
            # Simple parsing
            if 'week' in turnaround.lower():
                days = 7
            elif 'day' in turnaround.lower():
                try:
                    days = int(''.join(filter(str.isdigit, turnaround.split('-')[0])))
                except:
                    days = 1
            else:
                days = 1
            max_days = max(max_days, days)

        if max_days >= 7:
            weeks = max_days // 7
            return f"{weeks}-{weeks+1} weeks (parallel generation)"
        else:
            return f"{max_days}-{max_days+3} days (parallel generation)"

    def _evaluate_proposals(self, proposals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Have all directors evaluate all proposals.

        Args:
            proposals: List of director proposals

        Returns:
            List of evaluations
        """
        evaluations = []

        for evaluator_type in DirectorType:
            for proposal in proposals:
                print(f"      - {evaluator_type.value} evaluating {proposal['director']}...", end=" ")

                # Create evaluation request
                request = EvaluationRequest(
                    session_id=self.session_id,
                    phase_number=4,
                    director_type=evaluator_type,
                    evaluation_type="generation_strategy",
                    context={
                        'proposal': proposal,
                        'phase0_data': self.phase0_data,
                        'phase1_data': self.phase1_data,
                        'phase2_data': self.phase2_data,
                        'phase3_data': self.phase3_data
                    }
                )

                # Execute evaluation
                result = self.codex_runner.execute_evaluation(request)

                evaluation = {
                    'evaluator': evaluator_type.value,
                    'proposal_director': proposal['director'],
                    'score': result.score,
                    'feedback': result.feedback,
                    'highlights': result.highlights,
                    'concerns': result.concerns,
                    'suggestions': result.suggestions
                }

                evaluations.append(evaluation)
                print(f"{result.score:.1f}/100")

        return evaluations

    def _select_winner(
        self,
        proposals: List[Dict[str, Any]],
        evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Select winning proposal based on evaluations.

        Args:
            proposals: List of proposals
            evaluations: List of evaluations

        Returns:
            Winner information
        """
        # Aggregate scores for each proposal
        scores_by_director = {}

        for proposal in proposals:
            director = proposal['director']
            proposal_evals = [e for e in evaluations if e['proposal_director'] == director]

            if proposal_evals:
                avg_score = sum(e['score'] for e in proposal_evals) / len(proposal_evals)
                scores_by_director[director] = {
                    'director': director,
                    'total_score': avg_score,
                    'evaluation_count': len(proposal_evals),
                    'proposal': proposal
                }

        # Find winner (highest average score)
        winner = max(scores_by_director.values(), key=lambda x: x['total_score'])

        return winner

    def _build_asset_pipeline(
        self,
        winning_proposal: Dict[str, Any],
        clips: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build asset pipeline based on winning proposal.

        Args:
            winning_proposal: Winning generation strategy proposal
            clips: List of clips

        Returns:
            Asset pipeline information
        """
        # Create character reference assets
        if self.phase1_data and 'characters' in self.phase1_data:
            for char in self.phase1_data.get('characters', []):
                asset = create_character_consistency_asset(
                    character_name=char.get('name', 'Character'),
                    reference_images=[],
                    source="Phase 1 character design"
                )
                self.asset_manager.add_global_asset(asset)

        # Create style guide asset
        if self.phase0_data and 'color_palette' in self.phase0_data:
            asset = create_style_guide_asset(
                style_name="Overall MV Style",
                color_palette=self.phase0_data.get('color_palette', []),
                visual_references=[]
            )
            self.asset_manager.add_global_asset(asset)

        # Add clip-specific assets
        for strategy in winning_proposal.get('generation_strategies', []):
            clip_id = strategy['clip_id']

            for asset_req in strategy.get('assets_required', []):
                asset = self.asset_manager.create_asset(
                    asset_type=AssetType(asset_req.get('type', 'reference_image')),
                    description=asset_req.get('description', ''),
                    source=asset_req.get('source', ''),
                )
                self.asset_manager.add_clip_asset(clip_id, asset, required=True)

            # Set consistency requirements
            self.asset_manager.set_consistency_requirements(
                clip_id,
                strategy.get('consistency_requirements', {})
            )

        return self.asset_manager.to_dict()


def run_phase4(session_id: str, mock_mode: bool = True) -> Dict[str, Any]:
    """
    Run Phase 4 for a session.

    Args:
        session_id: Session identifier
        mock_mode: Whether to use mock evaluations

    Returns:
        Phase 4 results
    """
    runner = Phase4Runner(session_id, mock_mode=mock_mode)
    return runner.run()
