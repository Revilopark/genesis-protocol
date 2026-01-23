"""Writers Room schemas for narrative structure and episode generation."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# =============================================================================
# Enums for Narrative Structure
# =============================================================================


class ActType(str, Enum):
    """Three-act structure types."""

    SETUP = "setup"  # Act 1: Introduction, inciting incident
    CONFRONTATION = "confrontation"  # Act 2: Rising action, complications
    RESOLUTION = "resolution"  # Act 3: Climax, falling action, resolution


class SceneType(str, Enum):
    """Types of scenes in the narrative."""

    ACTION = "action"  # Fight scenes, chases, physical conflict
    DIALOGUE = "dialogue"  # Character conversations, exposition
    DISCOVERY = "discovery"  # Revealing information, plot twists
    EMOTIONAL = "emotional"  # Character development, relationships
    TRANSITION = "transition"  # Moving between locations/times
    MONTAGE = "montage"  # Time passage, training sequences


class LocationType(str, Enum):
    """Interior vs exterior location types."""

    INTERIOR = "INT"
    EXTERIOR = "EXT"
    BOTH = "INT/EXT"  # Mixed scenes


class TimeOfDay(str, Enum):
    """Time of day for scene setting."""

    DAY = "day"
    NIGHT = "night"
    DAWN = "dawn"
    DUSK = "dusk"
    CONTINUOUS = "continuous"  # Continues from previous scene


class PacingLevel(str, Enum):
    """Narrative pacing intensity."""

    SLOW = "slow"  # Contemplative, character moments
    MEDIUM = "medium"  # Normal progression
    FAST = "fast"  # Quick cuts, action sequences
    FRANTIC = "frantic"  # Climactic, high-stakes moments


class MoodAtmosphere(str, Enum):
    """Scene mood and atmosphere."""

    HEROIC = "heroic"
    MYSTERIOUS = "mysterious"
    TENSE = "tense"
    LIGHTHEARTED = "lighthearted"
    DARK = "dark"
    HOPEFUL = "hopeful"
    MELANCHOLIC = "melancholic"
    EPIC = "epic"


# =============================================================================
# Character Schemas
# =============================================================================


class CharacterRole(str, Enum):
    """Character roles in the story."""

    PROTAGONIST = "protagonist"
    ANTAGONIST = "antagonist"
    ALLY = "ally"
    MENTOR = "mentor"
    COMIC_RELIEF = "comic_relief"
    LOVE_INTEREST = "love_interest"
    BYSTANDER = "bystander"
    AUTHORITY = "authority"


class CharacterDescription(BaseModel):
    """Detailed character description for the episode."""

    character_id: str | None = Field(None, description="Reference ID if existing character")
    name: str
    role: CharacterRole
    appearance: str = Field(..., description="Physical description for visual consistency")
    costume: str | None = Field(None, description="What they're wearing in this episode")
    personality_traits: list[str] = Field(default_factory=list)
    motivation: str | None = Field(None, description="What drives them in this episode")
    arc_in_episode: str | None = Field(None, description="Character development in this episode")


class CharacterRelationship(BaseModel):
    """Relationship between two characters."""

    character_a: str
    character_b: str
    relationship_type: str = Field(..., description="friend, rival, mentor, enemy, family, etc.")
    dynamic: str = Field(..., description="How they interact, tension points, chemistry")
    history: str | None = Field(None, description="Backstory of their relationship")


# =============================================================================
# Location & Setting Schemas
# =============================================================================


class LocationDescription(BaseModel):
    """Detailed location/setting description."""

    location_id: str | None = Field(None, description="Reference ID if canonical location")
    name: str
    location_type: LocationType
    description: str = Field(..., description="Visual description of the location")
    atmosphere: MoodAtmosphere
    key_features: list[str] = Field(
        default_factory=list,
        description="Notable visual elements (e.g., 'neon signs', 'ancient ruins')",
    )
    lighting: str | None = Field(None, description="Lighting conditions and mood")
    weather: str | None = Field(None, description="Weather conditions if relevant")
    sound_ambience: str | None = Field(None, description="Background sounds for audio track")


# =============================================================================
# World Elements Schemas
# =============================================================================


class PropDescription(BaseModel):
    """Important prop or object in the scene."""

    name: str
    description: str
    significance: str = Field(..., description="Why this prop matters to the story")
    visual_details: str | None = Field(None, description="Details for consistent rendering")


class ThematicElement(BaseModel):
    """Thematic elements woven through the episode."""

    theme: str = Field(..., description="Core theme (e.g., 'sacrifice', 'identity', 'trust')")
    manifestation: str = Field(..., description="How this theme appears in the episode")
    visual_motifs: list[str] = Field(
        default_factory=list,
        description="Visual symbols representing this theme",
    )


# =============================================================================
# Scene & Narrative Flow Schemas
# =============================================================================


class SceneDescription(BaseModel):
    """Complete scene description with all narrative elements."""

    scene_number: int
    scene_type: SceneType
    act: ActType
    location: LocationDescription
    time_of_day: TimeOfDay
    duration_estimate: str = Field(
        default="1-2 pages",
        description="Estimated length in comic pages",
    )
    pacing: PacingLevel
    mood: MoodAtmosphere

    # Scene content
    scene_heading: str = Field(
        ...,
        description="Screenplay-style heading (e.g., 'INT. HERO BASE - NIGHT')",
    )
    scene_summary: str = Field(..., description="Brief summary of what happens")
    opening_hook: str | None = Field(None, description="How the scene grabs attention")
    closing_hook: str | None = Field(None, description="Cliffhanger or transition to next scene")

    # Characters in scene
    characters_present: list[str] = Field(default_factory=list)
    character_objectives: dict[str, str] = Field(
        default_factory=dict,
        description="What each character wants in this scene",
    )

    # Visual and narrative beats
    key_beats: list[str] = Field(
        default_factory=list,
        description="Major story beats that must happen",
    )
    visual_highlights: list[str] = Field(
        default_factory=list,
        description="Key visuals/moments for splash panels",
    )

    # Props and elements
    important_props: list[str] = Field(default_factory=list)
    action_description: str | None = Field(None, description="Physical action in the scene")


class SequenceDescription(BaseModel):
    """A sequence is a series of related scenes forming a narrative unit."""

    sequence_number: int
    title: str = Field(..., description="Sequence title for reference")
    purpose: str = Field(..., description="What this sequence accomplishes narratively")
    scenes: list[int] = Field(..., description="Scene numbers in this sequence")
    emotional_arc: str = Field(..., description="Emotional journey through this sequence")


class NarrativeStructure(BaseModel):
    """Complete narrative structure for the episode."""

    # Three-act breakdown
    act_one_summary: str = Field(..., description="Setup: Status quo, inciting incident")
    act_two_summary: str = Field(..., description="Confrontation: Complications, midpoint")
    act_three_summary: str = Field(..., description="Resolution: Climax, new status quo")

    # Pacing map
    pacing_notes: str | None = Field(
        None,
        description="Overall pacing strategy for the episode",
    )
    climax_scene: int | None = Field(None, description="Scene number of the climax")

    # Sequences and scenes
    sequences: list[SequenceDescription] = Field(default_factory=list)
    scenes: list[SceneDescription] = Field(default_factory=list)

    # Narrative flow
    central_conflict: str = Field(..., description="The main conflict driving the episode")
    stakes: str = Field(..., description="What's at risk if the hero fails")
    resolution_type: str = Field(
        default="partial_victory",
        description="How the episode resolves (victory, defeat, cliffhanger, etc.)",
    )


# =============================================================================
# Panel and Script Schemas (Enhanced)
# =============================================================================


class PanelDescription(BaseModel):
    """Description of a single comic panel with enhanced details."""

    panel_number: int
    scene_number: int | None = Field(None, description="Which scene this panel belongs to")
    visual_prompt: str = Field(..., description="Detailed description for image generation")
    dialogue: list[dict[str, str]] = Field(
        default_factory=list,
        description="List of {character, text} dialogue entries",
    )
    caption: str | None = Field(None, description="Narrator caption text")
    action: str = Field(..., description="What's happening in the panel")

    # Enhanced panel details
    panel_size: str = Field(
        default="standard",
        description="Panel size: small, standard, large, splash, double-splash",
    )
    camera_angle: str | None = Field(
        None,
        description="Shot type: wide, medium, close-up, extreme close-up, bird's eye, worm's eye",
    )
    focus_character: str | None = Field(None, description="Primary character in focus")
    emotional_beat: str | None = Field(None, description="Emotional moment this panel captures")
    sound_effects: list[str] = Field(
        default_factory=list,
        description="Visual sound effects (e.g., 'BOOM!', 'WHOOSH!')",
    )
    transition_to_next: str | None = Field(
        None,
        description="Transition type: cut, dissolve, match-cut, etc.",
    )


class EpisodeScript(BaseModel):
    """Complete episode script output with full narrative structure."""

    title: str
    synopsis: str
    panels: list[PanelDescription]
    storylet_id: str | None = None
    canon_references: list[str] = Field(
        default_factory=list,
        description="IDs of canon events referenced",
    )
    tags: list[str] = Field(default_factory=list)

    # Enhanced narrative elements
    narrative_structure: NarrativeStructure | None = Field(
        None,
        description="Full narrative breakdown (optional for simple episodes)",
    )
    characters: list[CharacterDescription] = Field(
        default_factory=list,
        description="Characters appearing in this episode",
    )
    character_relationships: list[CharacterRelationship] = Field(
        default_factory=list,
        description="Key relationships explored",
    )
    locations: list[LocationDescription] = Field(
        default_factory=list,
        description="Locations used in the episode",
    )
    props: list[PropDescription] = Field(
        default_factory=list,
        description="Important props and objects",
    )
    themes: list[ThematicElement] = Field(
        default_factory=list,
        description="Thematic elements in the episode",
    )

    # Production notes
    tone: MoodAtmosphere | None = Field(None, description="Overall episode tone")
    estimated_pages: int = Field(default=6, description="Target page count")
    climax_panels: list[int] = Field(
        default_factory=list,
        description="Panel numbers for Veo video generation",
    )


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
