"""
Tests for Phase 4 Generation Strategies Validator

Tests validation functionality for generation strategies including:
- Strategy completeness
- Generation mode validity
- Prompt quality
- Asset requirements
- Consistency requirements
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.validators.validate_phase4_strategies import (
    validate_strategy_completeness,
    validate_generation_mode_validity,
    validate_prompt_quality,
    validate_asset_requirements,
    validate_consistency_requirements,
    validate_variance_parameters,
    validate_creative_adjustments,
    validate_budget_timeline
)


class TestStrategyCompleteness:
    """Test strategy completeness validation."""

    def test_all_clips_covered(self):
        """Test that all clips having strategies passes."""
        phase3_clips = [
            {'clip_id': 'clip_001'},
            {'clip_id': 'clip_002'},
            {'clip_id': 'clip_003'}
        ]
        phase4_strategies = [
            {'clip_id': 'clip_001'},
            {'clip_id': 'clip_002'},
            {'clip_id': 'clip_003'}
        ]
        result = validate_strategy_completeness(phase3_clips, phase4_strategies)
        assert result['passed'] is True
        assert len(result['missing_clips']) == 0
        assert len(result['extra_clips']) == 0

    def test_missing_clips_fail(self):
        """Test that missing strategies are detected."""
        phase3_clips = [
            {'clip_id': 'clip_001'},
            {'clip_id': 'clip_002'},
            {'clip_id': 'clip_003'}
        ]
        phase4_strategies = [
            {'clip_id': 'clip_001'}
            # Missing clip_002 and clip_003
        ]
        result = validate_strategy_completeness(phase3_clips, phase4_strategies)
        assert result['passed'] is False
        assert 'clip_002' in result['missing_clips']
        assert 'clip_003' in result['missing_clips']

    def test_extra_clips_fail(self):
        """Test that extra strategies are detected."""
        phase3_clips = [
            {'clip_id': 'clip_001'}
        ]
        phase4_strategies = [
            {'clip_id': 'clip_001'},
            {'clip_id': 'clip_999'}  # Extra
        ]
        result = validate_strategy_completeness(phase3_clips, phase4_strategies)
        assert result['passed'] is False
        assert 'clip_999' in result['extra_clips']


class TestGenerationModeValidity:
    """Test generation mode validity validation."""

    def test_valid_modes_pass(self):
        """Test that valid generation modes pass."""
        strategies = [
            {'clip_id': 'clip_001', 'generation_mode': 'veo2'},
            {'clip_id': 'clip_002', 'generation_mode': 'sora'},
            {'clip_id': 'clip_003', 'generation_mode': 'runway_gen3'},
            {'clip_id': 'clip_004', 'generation_mode': 'traditional'}
        ]
        result = validate_generation_mode_validity(strategies)
        assert result['passed'] is True
        assert len(result['invalid_modes']) == 0

    def test_case_insensitive(self):
        """Test that mode names are case-insensitive."""
        strategies = [
            {'clip_id': 'clip_001', 'generation_mode': 'VEO2'},
            {'clip_id': 'clip_002', 'generation_mode': 'Sora'}
        ]
        result = validate_generation_mode_validity(strategies)
        assert result['passed'] is True

    def test_normalized_names(self):
        """Test that mode names with spaces/dashes are normalized."""
        strategies = [
            {'clip_id': 'clip_001', 'generation_mode': 'Runway Gen-3'},
            {'clip_id': 'clip_002', 'generation_mode': 'image to video'}
        ]
        result = validate_generation_mode_validity(strategies)
        # Should normalize to runway_gen3 and image_to_video
        assert result['passed'] is True

    def test_invalid_mode_fail(self):
        """Test that invalid modes are detected."""
        strategies = [
            {'clip_id': 'clip_001', 'generation_mode': 'invalid_mode'},
            {'clip_id': 'clip_002', 'generation_mode': 'unknown'}
        ]
        result = validate_generation_mode_validity(strategies)
        assert result['passed'] is False
        assert len(result['invalid_modes']) == 2

    def test_mode_distribution(self):
        """Test that mode distribution is tracked."""
        strategies = [
            {'clip_id': 'clip_001', 'generation_mode': 'veo2'},
            {'clip_id': 'clip_002', 'generation_mode': 'veo2'},
            {'clip_id': 'clip_003', 'generation_mode': 'sora'}
        ]
        result = validate_generation_mode_validity(strategies)
        assert result['mode_distribution']['veo2'] == 2
        assert result['mode_distribution']['sora'] == 1


class TestPromptQuality:
    """Test prompt quality validation."""

    def test_valid_prompts_pass(self):
        """Test that valid prompts pass."""
        strategies = [
            {
                'clip_id': 'clip_001',
                'prompt_template': {
                    'full_prompt': 'A cinematic shot of a person walking in the rain'
                }
            },
            {
                'clip_id': 'clip_002',
                'prompt_template': {
                    'base_prompt': 'Establishing shot of a city skyline'
                }
            }
        ]
        result = validate_prompt_quality(strategies)
        assert result['passed'] is True
        assert len(result['empty_prompts']) == 0

    def test_empty_prompt_fail(self):
        """Test that empty prompts are detected."""
        strategies = [
            {
                'clip_id': 'clip_001',
                'prompt_template': {
                    'full_prompt': ''
                }
            }
        ]
        result = validate_prompt_quality(strategies)
        assert result['passed'] is False
        assert 'clip_001' in result['empty_prompts']

    def test_too_short_prompt_fail(self):
        """Test that too-short prompts are detected."""
        strategies = [
            {
                'clip_id': 'clip_001',
                'prompt_template': {
                    'full_prompt': 'short'  # Too short
                }
            }
        ]
        result = validate_prompt_quality(strategies)
        assert result['passed'] is False
        assert 'clip_001' in result['too_short']

    def test_too_long_prompt_warning(self):
        """Test that too-long prompts generate warnings."""
        strategies = [
            {
                'clip_id': 'clip_001',
                'prompt_template': {
                    'full_prompt': 'x' * 1500  # Very long
                }
            }
        ]
        result = validate_prompt_quality(strategies)
        assert 'clip_001' in result['too_long']

    def test_average_length_calculation(self):
        """Test average prompt length calculation."""
        strategies = [
            {'clip_id': 'clip_001', 'prompt_template': {'full_prompt': 'a' * 100}},
            {'clip_id': 'clip_002', 'prompt_template': {'full_prompt': 'b' * 200}}
        ]
        result = validate_prompt_quality(strategies)
        assert result['avg_prompt_length'] == 150.0


class TestAssetRequirements:
    """Test asset requirements validation."""

    def test_valid_assets_pass(self):
        """Test that valid asset requirements pass."""
        strategies = [
            {
                'clip_id': 'clip_001',
                'assets_required': [
                    {'type': 'character_reference', 'description': 'Main character'},
                    {'type': 'style_guide', 'description': 'Color palette'}
                ]
            }
        ]
        result = validate_asset_requirements(strategies)
        assert result['passed'] is True

    def test_missing_assets_field_fail(self):
        """Test that missing assets_required field is detected."""
        strategies = [
            {
                'clip_id': 'clip_001'
                # Missing assets_required
            }
        ]
        result = validate_asset_requirements(strategies)
        assert result['passed'] is False
        assert 'clip_001' in result['missing_assets']

    def test_invalid_assets_structure(self):
        """Test that invalid asset structure is detected."""
        strategies = [
            {
                'clip_id': 'clip_001',
                'assets_required': 'not_a_list'  # Should be a list
            }
        ]
        result = validate_asset_requirements(strategies)
        assert result['passed'] is False


class TestConsistencyRequirements:
    """Test consistency requirements validation."""

    def test_valid_consistency_pass(self):
        """Test that valid consistency requirements pass."""
        strategies = [
            {
                'clip_id': 'clip_001',
                'consistency_requirements': {
                    'character_consistency': 'high',
                    'background_consistency': 'medium',
                    'style_consistency': 'high'
                }
            }
        ]
        result = validate_consistency_requirements(strategies)
        assert result['passed'] is True

    def test_missing_fields_fail(self):
        """Test that missing required fields are detected."""
        strategies = [
            {
                'clip_id': 'clip_001',
                'consistency_requirements': {
                    'character_consistency': 'high'
                    # Missing background_consistency and style_consistency
                }
            }
        ]
        result = validate_consistency_requirements(strategies)
        assert result['passed'] is False
        assert 'clip_001' in result['missing_consistency']

    def test_missing_consistency_field_fail(self):
        """Test that missing consistency_requirements field is detected."""
        strategies = [
            {
                'clip_id': 'clip_001'
                # Missing consistency_requirements
            }
        ]
        result = validate_consistency_requirements(strategies)
        assert result['passed'] is False


class TestVarianceParameters:
    """Test variance parameters validation."""

    def test_valid_variance_pass(self):
        """Test that valid variance parameters pass."""
        strategies = [
            {
                'clip_id': 'clip_001',
                'variance_params': {
                    'camera_angle_variance': 0.2,
                    'lighting_variance': 0.3,
                    'motion_variance': 0.15
                }
            }
        ]
        result = validate_variance_parameters(strategies)
        assert result['passed'] is True

    def test_out_of_range_fail(self):
        """Test that out-of-range values are detected."""
        strategies = [
            {
                'clip_id': 'clip_001',
                'variance_params': {
                    'camera_angle_variance': 1.5,  # > 1.0
                    'lighting_variance': -0.1  # < 0.0
                }
            }
        ]
        result = validate_variance_parameters(strategies)
        assert result['passed'] is False
        assert len(result['out_of_range']) == 2

    def test_missing_variance_ok(self):
        """Test that missing variance_params is tracked but may be ok."""
        strategies = [
            {
                'clip_id': 'clip_001'
                # Missing variance_params
            }
        ]
        result = validate_variance_parameters(strategies)
        assert 'clip_001' in result['missing_variance']


class TestCreativeAdjustmentsIntegration:
    """Test creative adjustments integration validation."""

    def test_valid_adjustments_pass(self):
        """Test that valid creative adjustments pass."""
        strategies = [
            {
                'clip_id': 'clip_001',
                'creative_adjustments': {
                    'base_reference': 'clip_000',
                    'adjustment_type': 'enhance',
                    'magnitude': 0.3
                }
            }
        ]
        result = validate_creative_adjustments(strategies)
        assert result['passed'] is True

    def test_missing_base_reference_fail(self):
        """Test that missing base_reference is detected."""
        strategies = [
            {
                'clip_id': 'clip_001',
                'creative_adjustments': {
                    'adjustment_type': 'enhance'
                    # Missing base_reference
                }
            }
        ]
        result = validate_creative_adjustments(strategies)
        assert result['passed'] is False
        assert 'clip_001' in result['invalid_references']

    def test_adjustments_optional(self):
        """Test that creative_adjustments are optional."""
        strategies = [
            {'clip_id': 'clip_001'}  # No adjustments
        ]
        result = validate_creative_adjustments(strategies)
        assert result['clips_with_adjustments'] == 0


class TestBudgetTimeline:
    """Test budget and timeline validation."""

    def test_budget_calculation(self):
        """Test budget estimation."""
        strategies = [
            {'clip_id': 'clip_001', 'estimated_cost': '$50-100'},
            {'clip_id': 'clip_002', 'estimated_cost': '$100-200'},
            {'clip_id': 'clip_003', 'estimated_cost': '$75-150'}
        ]
        result = validate_budget_timeline(strategies)
        assert result['passed'] is True
        assert result['total_estimated_cost'] > 0

    def test_timeline_estimation(self):
        """Test timeline estimation."""
        strategies = [
            {'clip_id': 'clip_001', 'estimated_time': '1 day'},
            {'clip_id': 'clip_002', 'estimated_time': '2 days'},
            {'clip_id': 'clip_003', 'estimated_time': '1 week'}
        ]
        result = validate_budget_timeline(strategies)
        assert result['passed'] is True
        assert result['total_estimated_time_hours'] > 0

    def test_missing_estimates_ok(self):
        """Test that missing estimates default gracefully."""
        strategies = [
            {'clip_id': 'clip_001'}  # No cost/time estimates
        ]
        result = validate_budget_timeline(strategies)
        # Should still pass, just with 0 totals
        assert result['passed'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
