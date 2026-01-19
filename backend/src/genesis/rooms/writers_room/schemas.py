"""Writers Room schemas."""

from pydantic import BaseModel, Field


class PanelDescription(BaseModel):
    """Description of a single comic panel."""

    panel_number: int
    visual_prompt: str = Field(..., description="Detailed description for image generation")
    dialogue: list[dict[str, str]] = Field(
        default_factory=list,
        description="List of {character, text} dialogue entries",
    )
    caption: str | None = Field(None, description="Narrator caption text")
    action: str = Field(..., description="What's happening in the panel")


class EpisodeScript(BaseModel):
    """Complete episode script output."""

    title: str
    synopsis: str
    panels: list[PanelDescription]
    storylet_id: str | None = None
    canon_references: list[str] = Field(
        default_factory=list,
        description="IDs of canon events referenced",
    )
    tags: list[str] = Field(default_factory=list)


class WritersRoomInput(BaseModel):
    """Input for Writers Room agent."""

    hero_id: str
    hero_name: str
    power_type: str
    origin_story: str
    episode_number: int
    previous_episodes_summary: str | None = None
    active_canon_events: list[dict[str, str | int | float]] = Field(default_factory=list)
    current_location: str | None = None
    include_crossover: bool = False
    crossover_hero: dict[str, str] | None = None
    content_settings: dict[str, int | bool] = Field(default_factory=dict)


class WritersRoomOutput(BaseModel):
    """Output from Writers Room agent."""

    script: EpisodeScript
    generation_notes: str | None = None
    safety_flags: list[str] = Field(default_factory=list)
