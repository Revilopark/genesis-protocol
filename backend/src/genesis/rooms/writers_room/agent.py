"""Writers Room agent implementation."""

import json
from typing import Any

from genesis.config import settings
from genesis.rooms.base import BaseRoom
from genesis.rooms.writers_room.prompts import (
    CROSSOVER_SECTION_TEMPLATE,
    EPISODE_PROMPT_TEMPLATE,
    SYSTEM_PROMPT,
)
from genesis.rooms.writers_room.schemas import (
    EpisodeScript,
    WritersRoomInput,
    WritersRoomOutput,
)


class WritersRoomAgent(BaseRoom):
    """Writers Room agent for narrative generation using Gemini."""

    def __init__(self) -> None:
        """Initialize the agent."""
        self.model_name = "gemini-1.5-pro"
        # In production, initialize Vertex AI client here
        # self.client = vertexai.generative_models.GenerativeModel(self.model_name)

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Generate episode script from input."""
        validated_input = WritersRoomInput(**input_data)

        # Build the prompt
        prompt = self._build_prompt(validated_input)

        # In production, call Gemini API
        # For now, return a placeholder
        script = await self._generate_script(prompt, validated_input)

        output = WritersRoomOutput(script=script)
        return output.model_dump()

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input data."""
        try:
            WritersRoomInput(**input_data)
            return True
        except Exception:
            return False

    def get_output_schema(self) -> dict[str, Any]:
        """Return output schema."""
        return WritersRoomOutput.model_json_schema()

    def _build_prompt(self, input_data: WritersRoomInput) -> str:
        """Build the episode generation prompt."""
        # Format canon events
        canon_events_text = "\n".join(
            f"- {event.get('title', 'Unknown')}: {event.get('description', '')}"
            for event in input_data.active_canon_events
        ) or "No major world events currently active."

        # Handle crossover section
        crossover_section = ""
        if input_data.include_crossover and input_data.crossover_hero:
            crossover_section = CROSSOVER_SECTION_TEMPLATE.format(
                crossover_hero_name=input_data.crossover_hero.get("hero_name", "Unknown"),
                crossover_hero_powers=input_data.crossover_hero.get("power_type", "Unknown"),
            )

        # Build full prompt
        prompt = EPISODE_PROMPT_TEMPLATE.format(
            episode_number=input_data.episode_number,
            hero_name=input_data.hero_name,
            power_type=input_data.power_type,
            origin_story=input_data.origin_story,
            current_location=input_data.current_location or "Metropolis Prime",
            previous_episodes_summary=input_data.previous_episodes_summary or "This is the hero's first adventure.",
            canon_events_text=canon_events_text,
            violence_level=input_data.content_settings.get("violence_level", 1),
            language_filter=input_data.content_settings.get("language_filter", True),
            crossover_section=crossover_section,
        )

        return prompt

    async def _generate_script(
        self,
        prompt: str,
        input_data: WritersRoomInput,
    ) -> EpisodeScript:
        """Generate script using Gemini (placeholder implementation)."""
        # TODO: Implement actual Gemini API call
        # For now, return a placeholder script
        return EpisodeScript(
            title=f"Episode {input_data.episode_number}: A New Challenge",
            synopsis=f"{input_data.hero_name} faces an unexpected challenge in their journey as a hero.",
            panels=[
                {
                    "panel_number": 1,
                    "visual_prompt": f"Wide shot of {input_data.hero_name} standing on a rooftop at sunset, city skyline behind them.",
                    "dialogue": [],
                    "caption": "Every hero's journey begins with a single step...",
                    "action": f"{input_data.hero_name} surveys the city",
                },
                {
                    "panel_number": 2,
                    "visual_prompt": "Close-up of the hero's face, determined expression, wind blowing their hair.",
                    "dialogue": [
                        {"character": input_data.hero_name, "text": "Time to make a difference."}
                    ],
                    "caption": None,
                    "action": "Hero prepares for action",
                },
            ],
            canon_references=[],
            tags=["action", "origin"],
        )
