#!/usr/bin/env python3
"""
MV Orchestra - Main Orchestrator

Coordinates the complete MP3 → MP4 pipeline:
1. Audio analysis (librosa)
2. Concept generation (Claude)
3. Asset generation (Stable Diffusion + LoRA)
4. Video composition (FFmpeg)
5. Quality assurance
6. Final rendering

Phase 0: Minimal prototype (10-second clips)
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.audio_analyzer import AudioAnalyzer
from tools.image_generator import ImageGenerator
from tools.video_composer import VideoComposer


class MVOrchestrator:
    """
    Main orchestrator for automated MV generation

    Phase 0 goals:
    - 10-second audio → MP4
    - Cost < $0.10
    - Time < 10 minutes
    - Verify all components work
    """

    def __init__(
        self,
        workspace_dir: str = "./workspace",
        max_cost: float = 2.0,
        max_time: int = 7200  # 2 hours in seconds
    ):
        """
        Initialize orchestrator

        Args:
            workspace_dir: Working directory for temp files
            max_cost: Maximum allowed cost in dollars
            max_time: Maximum execution time in seconds
        """
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.dirs = {
            'analysis': self.workspace / 'analysis',
            'scenes': self.workspace / 'scenes',
            'output': self.workspace / 'output',
            'logs': self.workspace / 'logs'
        }

        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)

        # Limits
        self.max_cost = max_cost
        self.max_time = max_time
        self.accumulated_cost = 0.0
        self.start_time = None

        # State
        self.state = {
            'phase': 'INIT',
            'iteration': 0,
            'analysis': None,
            'concept': None,
            'assets': None,
            'timeline': None,
            'output_path': None
        }

        print(f"{'='*70}")
        print("MV ORCHESTRA - Phase 0 Prototype")
        print(f"{'='*70}\n")
        print(f"Workspace: {self.workspace}")
        print(f"Max cost: ${self.max_cost:.2f}")
        print(f"Max time: {self.max_time}s ({self.max_time/60:.0f} minutes)\n")

    def generate_mv(
        self,
        audio_path: str,
        num_scenes: int = 10,
        output_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate complete music video from audio

        Args:
            audio_path: Path to MP3 file
            num_scenes: Number of scenes to generate
            output_name: Output filename (default: auto-generated)

        Returns:
            {
                'success': bool,
                'output_path': str,
                'cost': float,
                'duration': float,
                'stats': Dict
            }
        """
        self.start_time = time.time()

        print(f"{'='*70}")
        print("STARTING MV GENERATION")
        print(f"{'='*70}\n")
        print(f"Input: {audio_path}")
        print(f"Scenes: {num_scenes}\n")

        try:
            # Phase 1: Audio Analysis
            analysis = self._phase1_analyze_audio(audio_path)

            # Phase 2: Concept Generation (simplified for Phase 0)
            concept = self._phase2_generate_concept(analysis, num_scenes)

            # Phase 3: Generate Assets
            assets = self._phase3_generate_assets(concept)

            # Phase 4: Compose Video
            output_path = self._phase4_compose_video(
                assets,
                analysis,
                output_name or f"mv_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            )

            # Success
            elapsed = time.time() - self.start_time

            result = {
                'success': True,
                'output_path': str(output_path),
                'cost': self.accumulated_cost,
                'duration': elapsed,
                'stats': {
                    'audio_duration': analysis['duration'],
                    'num_scenes': len(assets),
                    'tempo': analysis['tempo'],
                    'beats': len(analysis['beat_times'])
                }
            }

            print(f"\n{'='*70}")
            print("MV GENERATION COMPLETE")
            print(f"{'='*70}\n")
            print(f"✓ Output: {output_path}")
            print(f"✓ Cost: ${self.accumulated_cost:.4f}")
            print(f"✓ Time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
            print(f"✓ Scenes: {len(assets)}")
            print(f"\n{'='*70}\n")

            return result

        except Exception as e:
            elapsed = time.time() - self.start_time

            print(f"\n{'='*70}")
            print("MV GENERATION FAILED")
            print(f"{'='*70}\n")
            print(f"✗ Error: {str(e)}")
            print(f"✗ Cost: ${self.accumulated_cost:.4f}")
            print(f"✗ Time: {elapsed:.1f}s")
            print(f"\n{'='*70}\n")

            raise

    def _phase1_analyze_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Phase 1: Analyze audio with librosa

        Cost: $0 (local processing)
        Time: ~2-5 minutes for 3-minute song
        """
        print(f"{'='*70}")
        print("PHASE 1: AUDIO ANALYSIS")
        print(f"{'='*70}\n")

        self.state['phase'] = 'ANALYZING'

        # Analyze
        analyzer = AudioAnalyzer(audio_path)
        analysis = analyzer.get_full_analysis()

        # Save analysis
        analysis_file = self.dirs['analysis'] / 'audio_analysis.json'
        analyzer.save_analysis(str(analysis_file))

        self.state['analysis'] = analysis

        print(f"\n✓ Phase 1 complete")
        print(f"  Duration: {analysis['duration']:.2f}s")
        print(f"  Tempo: {analysis['tempo']:.1f} BPM")
        print(f"  Beats: {len(analysis['beat_times'])}")
        print(f"  Key: {analysis['key']} {analysis['mode']}\n")

        return analysis

    def _phase2_generate_concept(
        self,
        analysis: Dict[str, Any],
        num_scenes: int
    ) -> Dict[str, Any]:
        """
        Phase 2: Generate creative concept

        For Phase 0: Simplified (no Claude integration yet)
        For Phase 1+: Full Claude integration

        Cost: $0 (Phase 0 simplified)
        Time: < 1 minute
        """
        print(f"{'='*70}")
        print("PHASE 2: CONCEPT GENERATION (Simplified)")
        print(f"{'='*70}\n")

        self.state['phase'] = 'CONCEPTUALIZING'

        # Simplified concept generation for Phase 0
        # In Phase 1, this will use Claude for creative conceptualization

        mood = analysis['mood']
        key = analysis['key']
        mode = analysis['mode']

        # Generate simple scene prompts based on mood
        base_style = self._mood_to_style(mood)

        scene_prompts = []
        for i in range(num_scenes):
            # Vary scenes slightly
            variation = self._get_scene_variation(i, num_scenes, mood)

            prompt = f"{base_style}, {variation}, {key} {mode} feeling"

            scene_prompts.append({
                'index': i,
                'prompt': prompt,
                'mood': mood,
                'energy': mood['energy'] + (i / num_scenes) * 0.2  # Gradual energy change
            })

        concept = {
            'overall_theme': base_style,
            'visual_style': f"{key} {mode} aesthetic",
            'color_palette': self._mood_to_colors(mood),
            'scene_prompts': scene_prompts,
            'num_scenes': len(scene_prompts)
        }

        # Save concept
        concept_file = self.dirs['analysis'] / 'concept.json'
        with open(concept_file, 'w') as f:
            json.dump(concept, f, indent=2)

        self.state['concept'] = concept

        print(f"✓ Phase 2 complete")
        print(f"  Theme: {concept['overall_theme']}")
        print(f"  Scenes: {len(scene_prompts)}")
        print(f"  Colors: {concept['color_palette']}\n")

        return concept

    def _phase3_generate_assets(self, concept: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Phase 3: Generate visual assets

        Cost: $0.0006 × num_scenes (Runware pricing)
        Time: ~30s × num_scenes
        """
        print(f"{'='*70}")
        print("PHASE 3: ASSET GENERATION")
        print(f"{'='*70}\n")

        self.state['phase'] = 'GENERATING_ASSETS'

        # Initialize generator
        generator = ImageGenerator()

        # Set style reference for consistency
        generator.set_style_reference(
            seed=42,  # Fixed seed for consistency
            color_palette=concept['color_palette']
        )

        # Generate scenes
        assets = generator.generate_scene_batch(
            scene_prompts=concept['scene_prompts'],
            output_dir=str(self.dirs['scenes']),
            use_controlnet=True
        )

        # Track cost
        cost_per_image = 0.0006
        phase_cost = len(assets) * cost_per_image
        self.accumulated_cost += phase_cost

        self.state['assets'] = assets

        print(f"\n✓ Phase 3 complete")
        print(f"  Images generated: {len(assets)}")
        print(f"  Cost: ${phase_cost:.4f}\n")

        return assets

    def _phase4_compose_video(
        self,
        assets: List[Dict[str, Any]],
        analysis: Dict[str, Any],
        output_name: str
    ) -> Path:
        """
        Phase 4: Compose final video

        Cost: $0 (local FFmpeg processing)
        Time: ~5-10 minutes
        """
        print(f"{'='*70}")
        print("PHASE 4: VIDEO COMPOSITION")
        print(f"{'='*70}\n")

        self.state['phase'] = 'COMPOSING'

        # Initialize composer
        composer = VideoComposer(fps=30, resolution=(1920, 1080))

        # Extract image paths
        image_paths = [asset['image_path'] for asset in assets]

        # Create timeline aligned to beats
        timeline = composer.create_timeline(
            images=image_paths,
            beat_times=analysis['beat_times'],
            duration=analysis['duration']
        )

        # Render video
        output_path = self.dirs['output'] / output_name

        composer.render_video(
            timeline=timeline,
            audio_path=analysis['audio_path'],
            output_path=str(output_path),
            transition='fade',
            transition_duration=0.3
        )

        self.state['output_path'] = str(output_path)

        print(f"\n✓ Phase 4 complete")
        print(f"  Output: {output_path}\n")

        return output_path

    def _mood_to_style(self, mood: Dict[str, float]) -> str:
        """Convert mood scores to visual style description"""
        energy = mood['energy']
        valence = mood['valence']

        if energy > 0.7 and valence > 0.6:
            return "vibrant, energetic, joyful visuals"
        elif energy > 0.7 and valence < 0.4:
            return "intense, dramatic, powerful imagery"
        elif energy < 0.3 and valence > 0.6:
            return "peaceful, serene, calm landscapes"
        elif energy < 0.3 and valence < 0.4:
            return "melancholic, introspective, moody scenes"
        else:
            return "balanced, contemplative visual journey"

    def _mood_to_colors(self, mood: Dict[str, float]) -> List[str]:
        """Convert mood to color palette"""
        energy = mood['energy']
        valence = mood['valence']

        if energy > 0.7 and valence > 0.6:
            return ["#FF6B6B", "#FFA500", "#FFD700", "#FF1493"]  # Vibrant
        elif energy > 0.7 and valence < 0.4:
            return ["#DC143C", "#8B0000", "#000000", "#FF4500"]  # Intense
        elif energy < 0.3 and valence > 0.6:
            return ["#87CEEB", "#98FB98", "#F0E68C", "#DDA0DD"]  # Peaceful
        elif energy < 0.3 and valence < 0.4:
            return ["#2F4F4F", "#708090", "#4B0082", "#191970"]  # Melancholic
        else:
            return ["#4ECDC4", "#45B7D1", "#6A5ACD", "#9370DB"]  # Balanced

    def _get_scene_variation(
        self,
        index: int,
        total: int,
        mood: Dict[str, float]
    ) -> str:
        """Generate variation for scene"""
        progress = index / total

        if progress < 0.33:
            return "opening scene, establishing atmosphere"
        elif progress < 0.66:
            return "dynamic middle section, building intensity"
        else:
            return "concluding scene, resolution"


def main():
    """
    Phase 0 test: 10-second audio clip

    Success criteria:
    - Generate MP4
    - Cost < $0.10
    - Time < 10 minutes
    """
    import sys

    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <audio_file.mp3> [num_scenes]")
        print("\nPhase 0 test: Use 10-second audio clip")
        sys.exit(1)

    audio_path = sys.argv[1]
    num_scenes = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    # Initialize orchestrator
    orchestrator = MVOrchestrator(
        workspace_dir="./mv_workspace",
        max_cost=0.10,  # Phase 0: $0.10 limit
        max_time=600     # Phase 0: 10 minutes
    )

    # Generate MV
    result = orchestrator.generate_mv(
        audio_path=audio_path,
        num_scenes=num_scenes
    )

    if result['success']:
        print(f"\n🎬 Success! Video generated: {result['output_path']}")
        print(f"💰 Cost: ${result['cost']:.4f}")
        print(f"⏱️  Time: {result['duration']:.1f}s")

        # Phase 0 success criteria
        if result['cost'] < 0.10 and result['duration'] < 600:
            print(f"\n✅ PHASE 0 SUCCESS CRITERIA MET")
        else:
            print(f"\n⚠️  Phase 0 criteria not met:")
            if result['cost'] >= 0.10:
                print(f"   Cost: ${result['cost']:.4f} >= $0.10")
            if result['duration'] >= 600:
                print(f"   Time: {result['duration']:.1f}s >= 600s")
    else:
        print(f"\n❌ Generation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
