"""Writers Room agent implementation using Google AI Studio."""

import json
import logging
from typing import Any

from google import genai
from google.genai import types

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

logger = logging.getLogger(__name__)


class WritersRoomAgent(BaseRoom):
    """Writers Room agent for narrative generation using Gemini 3 Pro."""

    def __init__(self) -> None:
        """Initialize the agent."""
        self.model_name = "gemini-3-pro-preview"
        self._client: genai.Client | None = None

    def _ensure_initialized(self) -> None:
        """Initialize Google AI Studio if not already done."""
        if self._client is not None:
            return  # Already initialized

        if not settings.gemini_api_key:
            logger.warning(f"GEMINI_API_KEY not configured (empty/not set)")
            return

        try:
            logger.info(f"Initializing Google AI Studio client with key prefix: {settings.gemini_api_key[:10]}...")
            self._client = genai.Client(api_key=settings.gemini_api_key)
            logger.info("Google AI Studio client initialized for Writers Room")
        except Exception as e:
            logger.error(f"Failed to initialize Google AI Studio: {e}")

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Generate episode script from input."""
        validated_input = WritersRoomInput(**input_data)

        # Build the prompt
        prompt = self._build_prompt(validated_input)

        # Generate script using Gemini
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
            previous_episodes_summary=input_data.previous_episodes_summary
            or "This is the hero's first adventure.",
            canon_events_text=canon_events_text,
            violence_level=input_data.content_settings.get("violence_level", 1),
            language_filter=input_data.content_settings.get("language_filter", True),
            crossover_section=crossover_section,
        )

        return prompt

    def _get_generation_config(self, input_data: WritersRoomInput) -> types.GenerateContentConfig:
        """Get generation config based on content settings."""
        return types.GenerateContentConfig(
            temperature=0.9,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            response_mime_type="application/json",
        )

    async def _generate_script(
        self,
        prompt: str,
        input_data: WritersRoomInput,
    ) -> EpisodeScript:
        """Generate script using Gemini 2.5 Pro."""
        self._ensure_initialized()

        # If Google AI Studio not initialized, return fallback
        if self._client is None:
            logger.warning("Google AI Studio not initialized, returning fallback script")
            return self._generate_fallback_script(input_data)

        try:
            generation_config = self._get_generation_config(input_data)

            # Add JSON schema instruction to prompt
            json_instruction = """
Output your response as a valid JSON object with this exact structure:
{
    "title": "Episode title",
    "synopsis": "Brief episode summary",
    "panels": [
        {
            "panel_number": 1,
            "visual_prompt": "Detailed description for image generation",
            "dialogue": [{"character": "Name", "text": "What they say"}],
            "caption": "Narrative caption or null",
            "action": "What happens in this panel"
        }
    ],
    "canon_references": ["list of canon elements referenced"],
    "tags": ["action", "mystery", etc.]
}

Generate exactly 8-10 panels for this episode.
"""
            full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}\n\n{json_instruction}"

            import asyncio
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model=self.model_name,
                contents=full_prompt,
                config=generation_config,
            )

            # Parse the response
            response_text = response.text.strip()

            # Handle potential markdown code blocks
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])

            script_data = json.loads(response_text)

            # Validate and create EpisodeScript
            return EpisodeScript(
                title=script_data.get("title", f"Episode {input_data.episode_number}"),
                synopsis=script_data.get("synopsis", ""),
                panels=script_data.get("panels", []),
                canon_references=script_data.get("canon_references", []),
                tags=script_data.get("tags", []),
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            return self._generate_fallback_script(input_data)
        except Exception as e:
            logger.error(f"Error generating script with Gemini: {e}")
            return self._generate_fallback_script(input_data)

    def _generate_fallback_script(self, input_data: WritersRoomInput) -> EpisodeScript:
        """Generate a fallback script when Gemini is unavailable."""
        return EpisodeScript(
            title=f"Episode {input_data.episode_number}: A New Challenge",
            synopsis=f"{input_data.hero_name} faces an unexpected challenge in their journey as a hero.",
            panels=[
                {
                    "panel_number": 1,
                    "visual_prompt": f"Wide establishing shot of a futuristic city at golden hour. {input_data.hero_name} stands on a tall building rooftop, cape flowing in the wind. The city skyline stretches into the distance with flying vehicles.",
                    "dialogue": [],
                    "caption": "In a world where heroes are born every day, one stands ready to make their mark...",
                    "action": f"{input_data.hero_name} surveys the city from above",
                },
                {
                    "panel_number": 2,
                    "visual_prompt": f"Medium shot of {input_data.hero_name}'s face in profile, determined expression. City lights reflect in their eyes. Wind-swept hair adds dynamic movement.",
                    "dialogue": [
                        {"character": input_data.hero_name, "text": "The city needs me."}
                    ],
                    "caption": None,
                    "action": "Hero's resolve strengthens",
                },
                {
                    "panel_number": 3,
                    "visual_prompt": "Street level view of a chaotic scene. Citizens running in panic. Smoke rises from a nearby building. Emergency lights flash.",
                    "dialogue": [],
                    "caption": "But tonight, something is different...",
                    "action": "Chaos erupts in the streets below",
                },
                {
                    "panel_number": 4,
                    "visual_prompt": f"Dynamic action shot of {input_data.hero_name} leaping from the rooftop, body in a heroic diving pose. Motion blur emphasizes speed.",
                    "dialogue": [
                        {"character": input_data.hero_name, "text": "Time to be a hero!"}
                    ],
                    "caption": None,
                    "action": "Hero launches into action",
                },
                {
                    "panel_number": 5,
                    "visual_prompt": f"Ground level shot looking up as {input_data.hero_name} lands dramatically in a three-point stance. Dust and debris scatter from the impact.",
                    "dialogue": [],
                    "caption": "With powers that set them apart from ordinary citizens...",
                    "action": "Hero lands dramatically",
                },
                {
                    "panel_number": 6,
                    "visual_prompt": f"Close-up of {input_data.hero_name}'s hands as their {input_data.power_type.lower()} powers activate. Energy or effects appropriate to their power type surround them.",
                    "dialogue": [],
                    "caption": None,
                    "action": "Powers manifest",
                },
                {
                    "panel_number": 7,
                    "visual_prompt": "Wide shot of the hero confronting the source of danger. Dramatic lighting with the threat silhouetted against flames or destruction.",
                    "dialogue": [
                        {"character": input_data.hero_name, "text": "This ends now!"}
                    ],
                    "caption": "Every hero must face their first true test.",
                    "action": "Hero confronts the threat",
                },
                {
                    "panel_number": 8,
                    "visual_prompt": f"Triumphant shot of {input_data.hero_name} standing amid cleared rubble, helping a grateful citizen to their feet. Sun breaking through clouds in background.",
                    "dialogue": [
                        {"character": "Citizen", "text": "Thank you! You saved us!"},
                        {"character": input_data.hero_name, "text": "Just doing what's right."},
                    ],
                    "caption": "And in that moment, a legend begins.",
                    "action": "Hero saves the day",
                },
            ],
            canon_references=[],
            tags=["action", "origin", "heroic"],
        )
