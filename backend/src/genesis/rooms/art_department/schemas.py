"""Art Department schemas for image generation."""

from typing import Any

from pydantic import BaseModel, Field


class CharacterSheet(BaseModel):
    """Character reference sheet for consistency."""

    hero_id: str
    hero_name: str
    visual_description: str
    costume_description: str
    color_palette: list[str] = Field(default_factory=list)
    reference_images: list[str] = Field(default_factory=list)  # GCS URLs


class PanelRequest(BaseModel):
    """Request for a single panel image generation."""

    panel_number: int
    visual_prompt: str
    action: str
    characters: list[str] = Field(default_factory=list)
    mood: str = "neutral"
    time_of_day: str = "day"
    location: str = "city"


class GeneratedPanel(BaseModel):
    """Generated panel image result."""

    panel_number: int
    image_url: str
    generation_prompt: str
    safety_score: float = 1.0
    retry_count: int = 0


class ArtDepartmentInput(BaseModel):
    """Input for Art Department processing."""

    hero_id: str
    hero_name: str
    episode_number: int
    character_sheet: dict[str, Any] | None = None
    panels: list[dict[str, Any]]
    style_preset: str = "comic_book"
    content_settings: dict[str, Any] = Field(default_factory=dict)


class ArtDepartmentOutput(BaseModel):
    """Output from Art Department processing."""

    hero_id: str
    episode_number: int
    generated_panels: list[GeneratedPanel]
    character_sheet_url: str | None = None
    total_generation_time: float = 0.0
    failed_panels: list[int] = Field(default_factory=list)
