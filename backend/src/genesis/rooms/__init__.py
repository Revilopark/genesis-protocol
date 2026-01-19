"""AI Agent Rooms module for content generation pipeline.

The Rooms are a multi-agent AI system for daily content generation:
- Writers Room: Narrative generation using Gemini 1.5 Pro
- Art Department: Image generation using Imagen 3
- Studio: Video synthesis using parallax + Veo
"""

from genesis.rooms.art_department import ArtDepartmentAgent
from genesis.rooms.studio import StudioAgent
from genesis.rooms.writers_room import WritersRoomAgent

__all__ = [
    "ArtDepartmentAgent",
    "StudioAgent",
    "WritersRoomAgent",
]
