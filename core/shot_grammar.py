"""
Shot Grammar System for MV Orchestra
Provides systematic cinematography vocabulary for Phase 3 clip division
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import random


class ShotGrammar:
    """Cinematography grammar system for systematic shot selection"""

    def __init__(self, grammar_path: str = "shot-grammar.json"):
        self.grammar_path = Path(grammar_path)
        self.grammar: Dict[str, Any] = {}
        self.load_grammar()

    def load_grammar(self) -> None:
        """Load shot grammar from JSON file"""
        if not self.grammar_path.exists():
            raise FileNotFoundError(f"Shot grammar not found: {self.grammar_path}")

        with open(self.grammar_path, 'r', encoding='utf-8') as f:
            self.grammar = json.load(f)

    def get_section(self, section_name: str) -> Dict[str, Any]:
        """Get a specific grammar section"""
        return self.grammar.get(section_name, {})

    def get_lens_types(self) -> Dict[str, Any]:
        """Get all lens types with their properties"""
        return self.get_section('lens_types')

    def get_shot_sizes(self) -> Dict[str, Any]:
        """Get all shot sizes with their properties"""
        return self.get_section('shot_sizes')

    def get_camera_movements(self) -> Dict[str, Any]:
        """Get all camera movements with their properties"""
        return self.get_section('camera_movements')

    def get_composition_rules(self) -> Dict[str, Any]:
        """Get all composition rules"""
        return self.get_section('composition_rules')

    def get_lighting_archetypes(self) -> Dict[str, Any]:
        """Get all lighting setups"""
        return self.get_section('lighting_archetypes')

    def suggest_shot_by_emotion(self, emotion: str) -> Dict[str, Any]:
        """Suggest shot parameters based on emotion"""
        emotional_mapping = self.get_section('emotional_camera_mapping')

        if emotion not in emotional_mapping:
            # Find closest match
            available_emotions = list(emotional_mapping.keys())
            emotion = available_emotions[0] if available_emotions else "joy_excitement"

        emotion_setup = emotional_mapping.get(emotion, {})

        # Extract recommendations
        suggestion = {
            'emotion': emotion,
            'camera': emotion_setup.get('camera', []),
            'composition': emotion_setup.get('composition', []),
            'lighting': emotion_setup.get('lighting', [])
        }

        return suggestion

    def suggest_shot_by_intensity(self, intensity: str) -> Dict[str, Any]:
        """Suggest camera movement based on intensity level"""
        intensity_grid = self.get_section('movement_intensity_grid')

        valid_intensities = ['calm', 'moderate', 'energetic', 'intense', 'extreme']
        if intensity not in valid_intensities:
            intensity = 'moderate'

        intensity_setup = intensity_grid.get(intensity, {})

        return {
            'intensity': intensity,
            'camera': intensity_setup.get('camera', []),
            'speed': intensity_setup.get('speed', '10-40% max_speed'),
            'duration': intensity_setup.get('typical_duration', '4-8sec per shot'),
            'emotions': intensity_setup.get('emotions', [])
        }

    def get_scene_template(self, template_name: str) -> Dict[str, Any]:
        """Get a specific scene template"""
        templates = self.get_section('scene_templates')
        return templates.get(template_name, {})

    def list_scene_templates(self) -> List[str]:
        """List all available scene template names"""
        return list(self.get_section('scene_templates').keys())

    def select_random_shot(
        self,
        emotion: Optional[str] = None,
        intensity: Optional[str] = None,
        shot_size_preference: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Randomly select a coherent shot configuration

        Args:
            emotion: Optional emotion to guide selection
            intensity: Optional intensity level
            shot_size_preference: Optional preferred shot size

        Returns:
            Dictionary with selected shot parameters
        """
        shot_sizes = self.get_shot_sizes()
        lens_types = self.get_lens_types()
        camera_movements = self.get_camera_movements()
        compositions = self.get_composition_rules()
        lighting = self.get_lighting_archetypes()

        # Select shot size
        if shot_size_preference and shot_size_preference in shot_sizes:
            shot_size = shot_size_preference
        else:
            shot_size = random.choice(list(shot_sizes.keys()))

        # Select lens type
        lens_type = random.choice(list(lens_types.keys()))

        # Select camera movement based on intensity
        if intensity:
            intensity_setup = self.suggest_shot_by_intensity(intensity)
            camera_opts = intensity_setup.get('camera', [])
            if camera_opts:
                movement = random.choice(camera_opts)
            else:
                movement = random.choice(list(camera_movements.keys()))
        else:
            movement = random.choice(list(camera_movements.keys()))

        # Select composition and lighting
        composition = random.choice(list(compositions.keys()))
        light = random.choice(list(lighting.keys()))

        return {
            'shot_size': shot_size,
            'lens_type': lens_type,
            'camera_movement': movement,
            'composition': composition,
            'lighting': light
        }

    def build_shot_description(self, shot_params: Dict[str, str]) -> str:
        """
        Build a human-readable shot description from parameters

        Args:
            shot_params: Dictionary with shot parameters

        Returns:
            Formatted shot description string
        """
        parts = []

        if 'shot_size' in shot_params:
            parts.append(shot_params['shot_size'].replace('_', ' '))

        if 'camera_movement' in shot_params:
            parts.append(f"with {shot_params['camera_movement'].replace('_', ' ')}")

        if 'lens_type' in shot_params:
            parts.append(f"using {shot_params['lens_type']} lens")

        if 'composition' in shot_params:
            parts.append(f"({shot_params['composition'].replace('_', ' ')} composition)")

        if 'lighting' in shot_params:
            parts.append(f"lit with {shot_params['lighting'].replace('_', ' ')}")

        return ', '.join(parts).capitalize()

    def validate_shot_params(self, shot_params: Dict[str, str]) -> tuple[bool, List[str]]:
        """
        Validate shot parameters against grammar

        Args:
            shot_params: Dictionary with shot parameters to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check shot_size
        if 'shot_size' in shot_params:
            if shot_params['shot_size'] not in self.get_shot_sizes():
                errors.append(f"Invalid shot_size: {shot_params['shot_size']}")

        # Check lens_type
        if 'lens_type' in shot_params:
            if shot_params['lens_type'] not in self.get_lens_types():
                errors.append(f"Invalid lens_type: {shot_params['lens_type']}")

        # Check camera_movement
        if 'camera_movement' in shot_params:
            if shot_params['camera_movement'] not in self.get_camera_movements():
                errors.append(f"Invalid camera_movement: {shot_params['camera_movement']}")

        # Check composition
        if 'composition' in shot_params:
            if shot_params['composition'] not in self.get_composition_rules():
                errors.append(f"Invalid composition: {shot_params['composition']}")

        # Check lighting
        if 'lighting' in shot_params:
            if shot_params['lighting'] not in self.get_lighting_archetypes():
                errors.append(f"Invalid lighting: {shot_params['lighting']}")

        return (len(errors) == 0, errors)

    def get_summary_stats(self) -> Dict[str, int]:
        """Get summary statistics of grammar coverage"""
        return {
            'lens_types': len(self.get_lens_types()),
            'shot_sizes': len(self.get_shot_sizes()),
            'camera_movements': len(self.get_camera_movements()),
            'composition_rules': len(self.get_composition_rules()),
            'lighting_archetypes': len(self.get_lighting_archetypes()),
            'scene_templates': len(self.get_section('scene_templates')),
            'emotional_mappings': len(self.get_section('emotional_camera_mapping')),
            'total_categories': len(self.grammar.get('root_structure', {}).get('sections', []))
        }


# Convenience function
def load_shot_grammar(grammar_path: str = "shot-grammar.json") -> ShotGrammar:
    """Load and return shot grammar instance"""
    return ShotGrammar(grammar_path)
