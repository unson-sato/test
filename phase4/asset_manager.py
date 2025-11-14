"""
Asset Management for MV Orchestra v2.8

This module manages assets required for video generation,
including reference images, style guides, and audio segments.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from pathlib import Path
from enum import Enum


class AssetType(Enum):
    """Types of assets"""
    REFERENCE_IMAGE = "reference_image"
    STYLE_GUIDE = "style_guide"
    CHARACTER_REFERENCE = "character_reference"
    LOCATION_REFERENCE = "location_reference"
    AUDIO_SEGMENT = "audio_segment"
    LIP_SYNC_AUDIO = "lip_sync_audio"
    COLOR_PALETTE = "color_palette"
    MOTION_REFERENCE = "motion_reference"
    CONSISTENCY_EMBEDDING = "consistency_embedding"


@dataclass
class Asset:
    """
    Represents a single asset.

    Attributes:
        asset_id: Unique identifier
        asset_type: Type of asset
        description: Human-readable description
        source: Where the asset comes from
        file_path: Optional path to asset file
        url: Optional URL to asset
        metadata: Additional metadata
    """
    asset_id: str
    asset_type: AssetType
    description: str
    source: str
    file_path: Optional[str] = None
    url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'asset_id': self.asset_id,
            'asset_type': self.asset_type.value,
            'description': self.description,
            'source': self.source,
            'file_path': self.file_path,
            'url': self.url,
            'metadata': self.metadata
        }

    @property
    def exists(self) -> bool:
        """Check if asset file exists"""
        if self.file_path:
            return Path(self.file_path).exists()
        return False


@dataclass
class ClipAssets:
    """
    Assets required for a specific clip.

    Attributes:
        clip_id: Clip identifier
        required_assets: List of required assets
        optional_assets: List of optional assets
        consistency_requirements: Consistency requirements
    """
    clip_id: str
    required_assets: List[Asset] = field(default_factory=list)
    optional_assets: List[Asset] = field(default_factory=list)
    consistency_requirements: Dict[str, Any] = field(default_factory=dict)

    def add_asset(self, asset: Asset, required: bool = True) -> None:
        """
        Add an asset to this clip.

        Args:
            asset: Asset to add
            required: Whether asset is required (True) or optional (False)
        """
        if required:
            self.required_assets.append(asset)
        else:
            self.optional_assets.append(asset)

    def get_assets_by_type(self, asset_type: AssetType) -> List[Asset]:
        """
        Get all assets of a specific type.

        Args:
            asset_type: Type of asset to retrieve

        Returns:
            List of matching assets
        """
        all_assets = self.required_assets + self.optional_assets
        return [a for a in all_assets if a.asset_type == asset_type]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'clip_id': self.clip_id,
            'required_assets': [a.to_dict() for a in self.required_assets],
            'optional_assets': [a.to_dict() for a in self.optional_assets],
            'consistency_requirements': self.consistency_requirements
        }


class AssetManager:
    """
    Manages assets for all clips in a session.
    """

    def __init__(self, session_id: str):
        """
        Initialize asset manager.

        Args:
            session_id: Session identifier
        """
        self.session_id = session_id
        self.clip_assets: Dict[str, ClipAssets] = {}
        self.global_assets: List[Asset] = []
        self._asset_counter = 0

    def create_asset(
        self,
        asset_type: AssetType,
        description: str,
        source: str,
        file_path: Optional[str] = None,
        url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Asset:
        """
        Create a new asset.

        Args:
            asset_type: Type of asset
            description: Asset description
            source: Source of asset
            file_path: Optional file path
            url: Optional URL
            metadata: Optional metadata

        Returns:
            Created Asset
        """
        self._asset_counter += 1
        asset_id = f"asset_{self.session_id}_{self._asset_counter:04d}"

        return Asset(
            asset_id=asset_id,
            asset_type=asset_type,
            description=description,
            source=source,
            file_path=file_path,
            url=url,
            metadata=metadata or {}
        )

    def add_clip_asset(
        self,
        clip_id: str,
        asset: Asset,
        required: bool = True
    ) -> None:
        """
        Add an asset to a specific clip.

        Args:
            clip_id: Clip identifier
            asset: Asset to add
            required: Whether asset is required
        """
        if clip_id not in self.clip_assets:
            self.clip_assets[clip_id] = ClipAssets(clip_id=clip_id)

        self.clip_assets[clip_id].add_asset(asset, required)

    def add_global_asset(self, asset: Asset) -> None:
        """
        Add a global asset (used across multiple clips).

        Args:
            asset: Asset to add
        """
        self.global_assets.append(asset)

    def get_clip_assets(self, clip_id: str) -> Optional[ClipAssets]:
        """
        Get assets for a specific clip.

        Args:
            clip_id: Clip identifier

        Returns:
            ClipAssets or None if not found
        """
        return self.clip_assets.get(clip_id)

    def get_all_assets(self) -> List[Asset]:
        """
        Get all assets (global + all clip assets).

        Returns:
            List of all assets
        """
        all_assets = self.global_assets.copy()

        for clip_assets in self.clip_assets.values():
            all_assets.extend(clip_assets.required_assets)
            all_assets.extend(clip_assets.optional_assets)

        return all_assets

    def get_assets_by_type(self, asset_type: AssetType) -> List[Asset]:
        """
        Get all assets of a specific type.

        Args:
            asset_type: Type of asset

        Returns:
            List of matching assets
        """
        return [a for a in self.get_all_assets() if a.asset_type == asset_type]

    def set_consistency_requirements(
        self,
        clip_id: str,
        requirements: Dict[str, Any]
    ) -> None:
        """
        Set consistency requirements for a clip.

        Args:
            clip_id: Clip identifier
            requirements: Consistency requirements
        """
        if clip_id not in self.clip_assets:
            self.clip_assets[clip_id] = ClipAssets(clip_id=clip_id)

        self.clip_assets[clip_id].consistency_requirements = requirements

    def get_asset_summary(self) -> Dict[str, Any]:
        """
        Get summary of all assets.

        Returns:
            Dictionary with asset statistics
        """
        all_assets = self.get_all_assets()

        type_counts = {}
        for asset in all_assets:
            type_name = asset.asset_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        return {
            'total_assets': len(all_assets),
            'global_assets': len(self.global_assets),
            'clips_with_assets': len(self.clip_assets),
            'assets_by_type': type_counts,
            'missing_files': [
                a.asset_id for a in all_assets
                if a.file_path and not a.exists
            ]
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Export asset manager state to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            'session_id': self.session_id,
            'global_assets': [a.to_dict() for a in self.global_assets],
            'clip_assets': {
                clip_id: assets.to_dict()
                for clip_id, assets in self.clip_assets.items()
            },
            'summary': self.get_asset_summary()
        }


def create_character_consistency_asset(
    character_name: str,
    reference_images: List[str],
    source: str = "Phase 1 character design"
) -> Asset:
    """
    Create a character consistency asset.

    Args:
        character_name: Name of character
        reference_images: List of reference image paths
        source: Source description

    Returns:
        Character reference Asset
    """
    return Asset(
        asset_id=f"char_ref_{character_name.lower().replace(' ', '_')}",
        asset_type=AssetType.CHARACTER_REFERENCE,
        description=f"Character consistency reference for {character_name}",
        source=source,
        metadata={
            'character_name': character_name,
            'reference_images': reference_images,
            'consistency_method': 'visual_reference'
        }
    )


def create_style_guide_asset(
    style_name: str,
    color_palette: List[str],
    visual_references: Optional[List[str]] = None
) -> Asset:
    """
    Create a style guide asset.

    Args:
        style_name: Name of style
        color_palette: List of colors (hex or names)
        visual_references: Optional visual reference paths

    Returns:
        Style guide Asset
    """
    return Asset(
        asset_id=f"style_{style_name.lower().replace(' ', '_')}",
        asset_type=AssetType.STYLE_GUIDE,
        description=f"Style guide: {style_name}",
        source="Phase 0/1 overall design",
        metadata={
            'style_name': style_name,
            'color_palette': color_palette,
            'visual_references': visual_references or []
        }
    )


def create_audio_segment_asset(
    clip_id: str,
    start_time: float,
    end_time: float,
    audio_file: str,
    has_vocals: bool = False
) -> Asset:
    """
    Create an audio segment asset.

    Args:
        clip_id: Clip identifier
        start_time: Start time in seconds
        end_time: End time in seconds
        audio_file: Path to audio file
        has_vocals: Whether segment has vocals (for lip sync)

    Returns:
        Audio segment Asset
    """
    asset_type = AssetType.LIP_SYNC_AUDIO if has_vocals else AssetType.AUDIO_SEGMENT

    return Asset(
        asset_id=f"audio_{clip_id}",
        asset_type=asset_type,
        description=f"Audio segment for {clip_id} ({start_time:.2f}s - {end_time:.2f}s)",
        source="Original track",
        file_path=audio_file,
        metadata={
            'clip_id': clip_id,
            'start_time': start_time,
            'end_time': end_time,
            'duration': end_time - start_time,
            'has_vocals': has_vocals
        }
    )
