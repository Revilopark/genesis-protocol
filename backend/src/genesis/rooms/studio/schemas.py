"""Studio schemas for video synthesis."""

from typing import Any

from pydantic import BaseModel, Field


class PanelVideoSegment(BaseModel):
    """Video segment generated from a single panel."""

    panel_number: int
    segment_type: str  # "parallax" or "generative"
    duration_seconds: float
    video_url: str | None = None
    status: str = "pending"  # pending, processing, completed, failed


class AudioTrack(BaseModel):
    """Audio track for the video."""

    track_type: str  # "dialogue", "music", "sfx"
    audio_url: str
    start_time: float
    duration: float


class VideoComposition(BaseModel):
    """Final composed video."""

    video_url: str
    duration_seconds: float
    resolution: str = "1080p"
    format: str = "mp4"
    file_size_mb: float = 0.0


class StudioInput(BaseModel):
    """Input for Studio processing."""

    hero_id: str
    hero_name: str
    episode_number: int
    panels: list[dict[str, Any]]  # Panel images with metadata
    script: dict[str, Any]  # Episode script with dialogue
    content_settings: dict[str, Any] = Field(default_factory=dict)
    include_generative_highlight: bool = True
    climax_panel_numbers: list[int] = Field(default_factory=list)  # Panels for Veo generation


class StudioOutput(BaseModel):
    """Output from Studio processing."""

    hero_id: str
    episode_number: int
    video: VideoComposition | None = None
    segments: list[PanelVideoSegment] = Field(default_factory=list)
    audio_tracks: list[AudioTrack] = Field(default_factory=list)
    total_processing_time: float = 0.0
    status: str = "completed"
    error_message: str | None = None
