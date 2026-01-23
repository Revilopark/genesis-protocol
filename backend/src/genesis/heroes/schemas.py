"""Hero schemas."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class HeroStatus(str, Enum):
    """Hero account status."""

    PENDING = "pending"  # Awaiting guardian approval
    ACTIVE = "active"  # Full access
    SUSPENDED = "suspended"  # Temporarily disabled


class PowerType(str, Enum):
    """Hero power types."""

    TECH = "tech"
    MAGIC = "magic"
    PHYSICAL = "physical"
    PSYCHIC = "psychic"


class ContentSettings(BaseModel):
    """Content filter settings."""

    violence_level: int = Field(default=1, ge=1, le=3, description="1=mild, 2=moderate, 3=intense")
    language_filter: bool = Field(default=True)


class HeroCreate(BaseModel):
    """Create hero request."""

    hero_name: str = Field(..., min_length=3, max_length=50)
    power_type: PowerType
    origin_story: str = Field(..., max_length=500)


class HeroUpdate(BaseModel):
    """Update hero request."""

    hero_name: str | None = Field(None, min_length=3, max_length=50)
    origin_story: str | None = Field(None, max_length=500)
    content_settings: ContentSettings | None = None


class HeroResponse(BaseModel):
    """Hero response model."""

    id: str
    user_id: str
    hero_name: str
    power_type: PowerType
    status: HeroStatus
    episode_count: int
    significance_score: float
    power_level: int
    abilities: list[str]
    current_location_id: str | None
    character_locker_url: str | None
    content_settings: ContentSettings
    created_at: datetime
    last_active_at: datetime | None


class HeroSummary(BaseModel):
    """Hero summary for lists."""

    id: str
    hero_name: str
    power_type: PowerType
    status: HeroStatus
    power_level: int


class EpisodeSummary(BaseModel):
    """Episode summary for hero profile."""

    id: str
    episode_number: int
    title: str
    comic_url: str | None
    video_url: str | None
    generated_at: datetime


class HeroWithEpisodes(BaseModel):
    """Hero with recent episodes."""

    hero: HeroResponse
    recent_episodes: list[EpisodeSummary]


class PanelDialogue(BaseModel):
    """Dialogue in a panel."""

    character: str
    text: str


class Panel(BaseModel):
    """Panel in an episode."""

    panel_number: int
    image_url: str | None = None
    generation_prompt: str | None = None
    visual_prompt: str | None = None
    dialogue: list[PanelDialogue] = Field(default_factory=list)
    caption: str | None = None
    action: str | None = None
    safety_score: float = 1.0
    retry_count: int = 0


class Script(BaseModel):
    """Episode script."""

    title: str
    synopsis: str
    panels: list[Panel]
    canon_references: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class VideoInfo(BaseModel):
    """Video information."""

    video_url: str
    duration_seconds: float
    resolution: str
    format: str
    file_size_mb: float


class HeroEpisode(BaseModel):
    """Full episode detail response."""

    hero_id: str
    episode_number: int
    title: str
    synopsis: str
    script: Script
    panels: list[Panel]
    video: VideoInfo | None = None
    tags: list[str] = Field(default_factory=list)
    canon_references: list[str] = Field(default_factory=list)
    generated_at: datetime
