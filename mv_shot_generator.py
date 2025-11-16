#!/usr/bin/env python3
"""
Music Video Shot Generator
AI-powered shot list generation using the shot grammar system
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Import AI integration
try:
    from ai_integration import get_ai_provider, AIProvider
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠ AI integration not available. Running in sample mode only.")


@dataclass
class SongInfo:
    """Song information for generation"""
    title: str
    artist: str
    genre: str
    bpm: int
    duration_seconds: int
    structure: List[str]  # e.g., ["intro", "verse", "chorus", "verse", "chorus", "bridge", "chorus"]
    mood: List[str]  # e.g., ["melancholy", "urban", "introspective"]


@dataclass
class ProductionConstraints:
    """Production constraints and preferences"""
    budget_level: str  # "low", "medium", "high"
    environment: List[str]  # e.g., ["urban", "indoor", "night"]
    num_performers: int
    performer_type: str  # "solo", "duo", "group", "ensemble"
    available_equipment: List[str]  # e.g., ["gimbal", "drone", "crane"]


@dataclass
class Shot:
    """Individual shot specification"""
    shot_number: int
    section: str  # which part of the song
    duration_seconds: float
    shot_size: str
    lens_type: str
    camera_movement: str
    composition: str
    lighting: str
    emotional_tone: str
    description: str
    technical_notes: Optional[str] = None


class ShotGrammarLoader:
    """Loads and provides access to the shot grammar JSON"""

    def __init__(self, grammar_path: str = "shot-grammar.json"):
        self.grammar_path = Path(grammar_path)
        self.grammar: Dict[str, Any] = {}
        self.load_grammar()

    def load_grammar(self):
        """Load the shot grammar JSON file"""
        try:
            with open(self.grammar_path, 'r', encoding='utf-8') as f:
                self.grammar = json.load(f)
            print(f"✓ Loaded shot grammar from {self.grammar_path}")
        except FileNotFoundError:
            print(f"✗ Error: Grammar file not found at {self.grammar_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"✗ Error: Invalid JSON in grammar file: {e}")
            sys.exit(1)

    def get_section(self, section_name: str) -> Dict[str, Any]:
        """Get a specific section from the grammar"""
        return self.grammar.get(section_name, {})

    def get_all_sections(self) -> List[str]:
        """Get all available section names"""
        return self.grammar.get('root_structure', {}).get('sections', [])

    def find_by_emotion(self, emotion: str) -> Dict[str, Any]:
        """Find grammar elements matching an emotion"""
        results = {}

        # Search emotional_camera_mapping
        emotional_mapping = self.get_section('emotional_camera_mapping')
        if emotion in emotional_mapping:
            results['camera_setup'] = emotional_mapping[emotion]

        # Search lighting_archetypes for mood matches
        lighting = self.get_section('lighting_archetypes')
        for light_name, light_data in lighting.items():
            if emotion in light_data.get('mood', []):
                if 'lighting' not in results:
                    results['lighting'] = []
                results['lighting'].append({light_name: light_data})

        return results

    def find_by_movement_intensity(self, intensity: str) -> Dict[str, Any]:
        """Find camera movements by intensity level"""
        intensity_grid = self.get_section('movement_intensity_grid')
        return intensity_grid.get(intensity, {})

    def get_scene_template(self, template_name: str) -> Dict[str, Any]:
        """Get a specific scene template"""
        templates = self.get_section('scene_templates')
        return templates.get(template_name, {})


class PromptBuilder:
    """Builds prompts for AI generation"""

    def __init__(self, grammar_loader: ShotGrammarLoader):
        self.grammar = grammar_loader

    def build_generation_prompt(self, song_info: SongInfo, constraints: ProductionConstraints) -> str:
        """Build a comprehensive prompt for AI shot generation"""

        # Extract relevant grammar sections based on mood
        relevant_grammar = self._extract_relevant_grammar(song_info.mood, constraints)

        prompt = f"""You are an expert music video director and cinematographer. Generate a detailed shot list for a music video based on the following information:

## SONG INFORMATION
- Title: {song_info.title}
- Artist: {song_info.artist}
- Genre: {song_info.genre}
- BPM: {song_info.bpm}
- Duration: {song_info.duration_seconds} seconds
- Structure: {' → '.join(song_info.structure)}
- Mood/Emotions: {', '.join(song_info.mood)}

## PRODUCTION CONSTRAINTS
- Budget Level: {constraints.budget_level}
- Environment: {', '.join(constraints.environment)}
- Number of Performers: {constraints.num_performers} ({constraints.performer_type})
- Available Equipment: {', '.join(constraints.available_equipment)}

## SHOT GRAMMAR REFERENCE
Use the following cinematography grammar to construct your shot list:

{json.dumps(relevant_grammar, indent=2, ensure_ascii=False)}

## REQUIREMENTS
1. Create a shot-by-shot breakdown that covers the entire song duration
2. Match shot selection to the emotional arc of the song
3. Ensure visual variety while maintaining coherence
4. Consider the production constraints (budget, equipment)
5. Create energy curves that align with the musical structure
6. Use appropriate transitions between sections
7. Each shot should specify: shot size, lens type, camera movement, composition, lighting, and emotional tone

## OUTPUT FORMAT
Provide the output as a JSON array of shots, where each shot has:
- shot_number (int)
- section (str) - which part of the song
- duration_seconds (float)
- shot_size (str)
- lens_type (str)
- camera_movement (str)
- composition (str)
- lighting (str)
- emotional_tone (str)
- description (str) - what happens in this shot
- technical_notes (str, optional) - any special technical requirements

Generate the shot list now:
"""
        return prompt

    def _extract_relevant_grammar(self, moods: List[str], constraints: ProductionConstraints) -> Dict[str, Any]:
        """Extract relevant parts of the grammar based on mood and constraints"""

        relevant = {
            'lens_types': self.grammar.get_section('lens_types'),
            'shot_sizes': self.grammar.get_section('shot_sizes'),
            'camera_movements': self.grammar.get_section('camera_movements'),
            'composition_rules': self.grammar.get_section('composition_rules'),
            'lighting_archetypes': self.grammar.get_section('lighting_archetypes'),
            'editing_transitions': self.grammar.get_section('editing_transitions'),
        }

        # Add mood-specific sections
        for mood in moods:
            mood_data = self.grammar.find_by_emotion(mood)
            if mood_data:
                relevant[f'mood_{mood}'] = mood_data

        # Add movement intensity based on BPM/genre (could be enhanced)
        relevant['movement_intensity_grid'] = self.grammar.get_section('movement_intensity_grid')

        # Add multi-actor patterns if group performance
        if constraints.num_performers > 1:
            relevant['multi_actor_patterns'] = self.grammar.get_section('multi_actor_patterns')

        # Add environment-specific modifiers
        relevant['environment_modifiers'] = self.grammar.get_section('environment_modifiers')

        return relevant


class ShotListGenerator:
    """Generates shot lists using AI"""

    def __init__(self, grammar_loader: ShotGrammarLoader, ai_provider: Optional[str] = None,
                 use_ai: bool = True, show_prompt: bool = False):
        self.grammar = grammar_loader
        self.prompt_builder = PromptBuilder(grammar_loader)
        self.use_ai = use_ai and AI_AVAILABLE
        self.show_prompt = show_prompt
        self.ai_provider_name = ai_provider or "anthropic"

    def generate(self, song_info: SongInfo, constraints: ProductionConstraints) -> List[Shot]:
        """Generate a shot list"""

        # Build the prompt
        prompt = self.prompt_builder.build_generation_prompt(song_info, constraints)

        if self.show_prompt:
            print("\n" + "="*80)
            print("GENERATION PROMPT")
            print("="*80)
            print(prompt)
            print("="*80 + "\n")

        if self.use_ai:
            try:
                print(f"🤖 Using AI provider: {self.ai_provider_name}")
                provider = get_ai_provider(self.ai_provider_name)
                print("🎬 Generating shot list with AI...")

                response = provider.generate_shot_list(prompt)

                # Parse the JSON response
                shots = self._parse_ai_response(response)

                if shots:
                    print(f"✓ AI generated {len(shots)} shots")
                    return shots
                else:
                    print("⚠ AI response could not be parsed. Falling back to sample generation.")
                    return self._generate_sample_shots(song_info, constraints)

            except Exception as e:
                print(f"⚠ Error with AI generation: {e}")
                print("⚠ Falling back to sample generation...")
                return self._generate_sample_shots(song_info, constraints)
        else:
            print("⚠ AI disabled. Generating sample shot list...\n")
            return self._generate_sample_shots(song_info, constraints)

    def _parse_ai_response(self, response: str) -> Optional[List[Shot]]:
        """Parse AI response into Shot objects"""
        try:
            # Try to parse as JSON
            shots_data = json.loads(response)

            if not isinstance(shots_data, list):
                print("⚠ AI response is not a list")
                return None

            shots = []
            for shot_data in shots_data:
                # Validate required fields
                required_fields = [
                    'shot_number', 'section', 'duration_seconds', 'shot_size',
                    'lens_type', 'camera_movement', 'composition', 'lighting',
                    'emotional_tone', 'description'
                ]

                missing_fields = [f for f in required_fields if f not in shot_data]
                if missing_fields:
                    print(f"⚠ Shot {shot_data.get('shot_number', '?')} missing fields: {missing_fields}")
                    continue

                shot = Shot(
                    shot_number=shot_data['shot_number'],
                    section=shot_data['section'],
                    duration_seconds=float(shot_data['duration_seconds']),
                    shot_size=shot_data['shot_size'],
                    lens_type=shot_data['lens_type'],
                    camera_movement=shot_data['camera_movement'],
                    composition=shot_data['composition'],
                    lighting=shot_data['lighting'],
                    emotional_tone=shot_data['emotional_tone'],
                    description=shot_data['description'],
                    technical_notes=shot_data.get('technical_notes')
                )
                shots.append(shot)

            return shots if shots else None

        except json.JSONDecodeError as e:
            print(f"⚠ Failed to parse AI response as JSON: {e}")
            return None
        except Exception as e:
            print(f"⚠ Error parsing AI response: {e}")
            return None

    def _generate_sample_shots(self, song_info: SongInfo, constraints: ProductionConstraints) -> List[Shot]:
        """Generate a sample shot list (placeholder for AI generation)"""

        shots = []
        shot_num = 1
        time_offset = 0.0

        for section in song_info.structure:
            # Determine section duration (simplified)
            if section == "intro":
                section_duration = 8.0
            elif section == "verse":
                section_duration = 16.0
            elif section == "chorus":
                section_duration = 20.0
            elif section == "bridge":
                section_duration = 12.0
            else:
                section_duration = 10.0

            # Generate shots for this section based on mood and section type
            section_shots = self._generate_section_shots(
                shot_num, section, section_duration, time_offset, song_info.mood
            )

            shots.extend(section_shots)
            shot_num += len(section_shots)
            time_offset += section_duration

        return shots

    def _generate_section_shots(
        self, start_num: int, section: str, duration: float,
        time_offset: float, moods: List[str]
    ) -> List[Shot]:
        """Generate shots for a specific section"""

        shots = []

        if section == "intro":
            shots.append(Shot(
                shot_number=start_num,
                section=section,
                duration_seconds=4.0,
                shot_size="extreme_wide_shot",
                lens_type="wide",
                camera_movement="drone_aerial",
                composition="rule_of_thirds",
                lighting="blue_hour_melancholy",
                emotional_tone="mysterious",
                description="Aerial establishing shot of the city at twilight, slowly descending towards the location"
            ))
            shots.append(Shot(
                shot_number=start_num + 1,
                section=section,
                duration_seconds=4.0,
                shot_size="medium_shot",
                lens_type="standard",
                camera_movement="slow_push",
                composition="center_framing",
                lighting="practical_motivated",
                emotional_tone="anticipation",
                description="Artist in silhouette, camera slowly pushing in as they turn towards camera"
            ))

        elif section == "verse":
            shots.append(Shot(
                shot_number=start_num,
                section=section,
                duration_seconds=8.0,
                shot_size="medium_wide_shot",
                lens_type="standard",
                camera_movement="steadicam",
                composition="rule_of_thirds",
                lighting="soft_box_beauty",
                emotional_tone="intimate",
                description="Artist singing, steadicam following as they move through the space"
            ))
            shots.append(Shot(
                shot_number=start_num + 1,
                section=section,
                duration_seconds=8.0,
                shot_size="close_up",
                lens_type="portrait",
                camera_movement="handheld",
                composition="negative_space",
                lighting="natural_window_light",
                emotional_tone="emotional",
                description="Close-up of artist's face, capturing emotional performance"
            ))

        elif section == "chorus":
            shots.append(Shot(
                shot_number=start_num,
                section=section,
                duration_seconds=10.0,
                shot_size="wide_shot",
                lens_type="wide",
                camera_movement="orbital_360",
                composition="center_framing",
                lighting="colored_gel_expressive",
                emotional_tone="energetic",
                description="360-degree rotation around artist during chorus, energy burst with colored lights"
            ))
            shots.append(Shot(
                shot_number=start_num + 1,
                section=section,
                duration_seconds=10.0,
                shot_size="medium_close_up",
                lens_type="portrait",
                camera_movement="gimbal_flow",
                composition="rule_of_thirds",
                lighting="backlight_silhouette",
                emotional_tone="powerful",
                description="Dynamic gimbal movement with artist, backlighting creating dramatic silhouette"
            ))

        elif section == "bridge":
            shots.append(Shot(
                shot_number=start_num,
                section=section,
                duration_seconds=6.0,
                shot_size="extreme_close_up",
                lens_type="macro",
                camera_movement="static_locked",
                composition="center_framing",
                lighting="single_source_dramatic",
                emotional_tone="intense",
                description="Extreme close-up of eyes, completely still, dramatic single light source"
            ))
            shots.append(Shot(
                shot_number=start_num + 1,
                section=section,
                duration_seconds=6.0,
                shot_size="wide_shot",
                lens_type="wide",
                camera_movement="crane_jib",
                composition="negative_space",
                lighting="backlight_silhouette",
                emotional_tone="isolation",
                description="Crane pulls back revealing artist alone in vast space"
            ))

        return shots


class OutputFormatter:
    """Formats shot lists for different output types"""

    @staticmethod
    def to_json(shots: List[Shot], pretty: bool = True) -> str:
        """Convert shots to JSON format"""
        shots_dict = [asdict(shot) for shot in shots]
        if pretty:
            return json.dumps(shots_dict, indent=2, ensure_ascii=False)
        return json.dumps(shots_dict, ensure_ascii=False)

    @staticmethod
    def to_markdown(shots: List[Shot], song_info: SongInfo, constraints: ProductionConstraints) -> str:
        """Convert shots to Markdown format"""

        md = f"""# Music Video Shot List

## Song Information
- **Title**: {song_info.title}
- **Artist**: {song_info.artist}
- **Genre**: {song_info.genre}
- **BPM**: {song_info.bpm}
- **Duration**: {song_info.duration_seconds}s
- **Mood**: {', '.join(song_info.mood)}

## Production Details
- **Budget Level**: {constraints.budget_level}
- **Environment**: {', '.join(constraints.environment)}
- **Performers**: {constraints.num_performers} ({constraints.performer_type})
- **Equipment**: {', '.join(constraints.available_equipment)}

## Shot List

"""

        current_section = None
        for shot in shots:
            if shot.section != current_section:
                current_section = shot.section
                md += f"\n### {current_section.upper()}\n\n"

            md += f"#### Shot {shot.shot_number}\n"
            md += f"- **Duration**: {shot.duration_seconds}s\n"
            md += f"- **Shot Size**: {shot.shot_size}\n"
            md += f"- **Lens**: {shot.lens_type}\n"
            md += f"- **Movement**: {shot.camera_movement}\n"
            md += f"- **Composition**: {shot.composition}\n"
            md += f"- **Lighting**: {shot.lighting}\n"
            md += f"- **Emotion**: {shot.emotional_tone}\n"
            md += f"- **Description**: {shot.description}\n"
            if shot.technical_notes:
                md += f"- **Technical Notes**: {shot.technical_notes}\n"
            md += "\n"

        return md

    @staticmethod
    def to_csv(shots: List[Shot]) -> str:
        """Convert shots to CSV format"""
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'shot_number', 'section', 'duration_seconds', 'shot_size',
            'lens_type', 'camera_movement', 'composition', 'lighting',
            'emotional_tone', 'description', 'technical_notes'
        ])

        writer.writeheader()
        for shot in shots:
            writer.writerow(asdict(shot))

        return output.getvalue()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Generate music video shot lists using AI and shot grammar'
    )

    # Song information
    parser.add_argument('--title', required=True, help='Song title')
    parser.add_argument('--artist', required=True, help='Artist name')
    parser.add_argument('--genre', required=True, help='Music genre')
    parser.add_argument('--bpm', type=int, required=True, help='Beats per minute')
    parser.add_argument('--duration', type=int, required=True, help='Song duration in seconds')
    parser.add_argument('--structure', required=True, help='Song structure (comma-separated, e.g., intro,verse,chorus,verse,chorus,bridge,chorus)')
    parser.add_argument('--mood', required=True, help='Mood/emotions (comma-separated, e.g., melancholy,urban,introspective)')

    # Production constraints
    parser.add_argument('--budget', choices=['low', 'medium', 'high'], default='medium', help='Budget level')
    parser.add_argument('--environment', default='urban,night', help='Environment types (comma-separated)')
    parser.add_argument('--performers', type=int, default=1, help='Number of performers')
    parser.add_argument('--performer-type', choices=['solo', 'duo', 'group', 'ensemble'], default='solo')
    parser.add_argument('--equipment', default='gimbal,drone', help='Available equipment (comma-separated)')

    # Output options
    parser.add_argument('--output-format', choices=['json', 'markdown', 'csv'], default='markdown', help='Output format')
    parser.add_argument('--output-file', help='Output file path (default: stdout)')
    parser.add_argument('--grammar-file', default='shot-grammar.json', help='Path to shot grammar JSON file')

    # AI options
    parser.add_argument('--ai-provider', choices=['anthropic', 'openai', 'mock'], default='anthropic',
                        help='AI provider to use for generation')
    parser.add_argument('--no-ai', action='store_true', help='Disable AI generation, use sample shots')
    parser.add_argument('--show-prompt', action='store_true', help='Show the generation prompt')

    args = parser.parse_args()

    # Create song info
    song_info = SongInfo(
        title=args.title,
        artist=args.artist,
        genre=args.genre,
        bpm=args.bpm,
        duration_seconds=args.duration,
        structure=args.structure.split(','),
        mood=args.mood.split(',')
    )

    # Create production constraints
    constraints = ProductionConstraints(
        budget_level=args.budget,
        environment=args.environment.split(','),
        num_performers=args.performers,
        performer_type=args.performer_type,
        available_equipment=args.equipment.split(',')
    )

    # Load grammar and generate
    print("🎬 Music Video Shot Generator\n")

    grammar_loader = ShotGrammarLoader(args.grammar_file)
    generator = ShotListGenerator(
        grammar_loader,
        ai_provider=args.ai_provider,
        use_ai=not args.no_ai,
        show_prompt=args.show_prompt
    )

    print("🎵 Generating shot list...")
    shots = generator.generate(song_info, constraints)

    print(f"✓ Generated {len(shots)} shots\n")

    # Format output
    if args.output_format == 'json':
        output = OutputFormatter.to_json(shots)
    elif args.output_format == 'markdown':
        output = OutputFormatter.to_markdown(shots, song_info, constraints)
    elif args.output_format == 'csv':
        output = OutputFormatter.to_csv(shots)
    else:
        output = OutputFormatter.to_json(shots)

    # Write output
    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"✓ Saved to {args.output_file}")
    else:
        print(output)


if __name__ == '__main__':
    main()
