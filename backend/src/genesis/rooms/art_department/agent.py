"""Art Department agent implementation using Imagen 3."""

import asyncio
import base64
import logging
import time
import uuid
from typing import Any

import vertexai
from google.cloud import storage
from vertexai.preview.vision_models import ImageGenerationModel

from genesis.config import settings
from genesis.rooms.base import BaseRoom
from genesis.rooms.art_department.schemas import (
    ArtDepartmentInput,
    ArtDepartmentOutput,
    GeneratedPanel,
    PanelRequest,
)

logger = logging.getLogger(__name__)

# Style presets for consistent comic book aesthetics
STYLE_PRESETS = {
    "comic_book": "digital comic book art style, bold outlines, dynamic composition, vibrant colors, professional illustration",
    "manga": "manga art style, clean lines, expressive characters, screentone shading",
    "realistic": "semi-realistic comic art, detailed rendering, cinematic lighting",
    "animated": "animated series art style, clean cel-shaded look, bright colors",
}

# Negative prompt to avoid common issues
NEGATIVE_PROMPT = (
    "blurry, low quality, distorted, deformed, bad anatomy, "
    "text, watermark, signature, extra limbs, missing limbs, "
    "realistic photograph, 3D render, clay render"
)


class ArtDepartmentAgent(BaseRoom):
    """Art Department agent for image generation using Imagen 3."""

    _initialized: bool = False

    def __init__(self) -> None:
        """Initialize the agent."""
        self._model: ImageGenerationModel | None = None
        self._storage_client: storage.Client | None = None
        self._bucket_name = f"{settings.gcp_project_id}-genesis-assets"

    def _ensure_initialized(self) -> None:
        """Initialize Vertex AI and storage if not already done."""
        if not ArtDepartmentAgent._initialized and settings.gcp_project_id:
            try:
                vertexai.init(
                    project=settings.gcp_project_id,
                    location=settings.gcp_location,
                )
                ArtDepartmentAgent._initialized = True
                logger.info("Vertex AI initialized for Art Department")
            except Exception as e:
                logger.warning(f"Failed to initialize Vertex AI: {e}")

        if self._model is None and ArtDepartmentAgent._initialized:
            try:
                self._model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
                logger.info("Imagen 3 model loaded")
            except Exception as e:
                logger.warning(f"Failed to load Imagen 3 model: {e}")

        if self._storage_client is None and settings.gcp_project_id:
            try:
                self._storage_client = storage.Client(project=settings.gcp_project_id)
                logger.info("GCS client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize GCS client: {e}")

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Generate panel images from input."""
        validated_input = ArtDepartmentInput(**input_data)
        start_time = time.time()

        # Generate all panels
        generated_panels: list[GeneratedPanel] = []
        failed_panels: list[int] = []

        # Process panels in batches to manage API rate limits
        batch_size = 4
        panels = validated_input.panels

        for i in range(0, len(panels), batch_size):
            batch = panels[i : i + batch_size]
            tasks = [
                self._generate_panel(
                    panel=PanelRequest(**p),
                    hero_name=validated_input.hero_name,
                    hero_id=validated_input.hero_id,
                    episode_number=validated_input.episode_number,
                    style_preset=validated_input.style_preset,
                    character_sheet=validated_input.character_sheet,
                    content_settings=validated_input.content_settings,
                )
                for p in batch
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Panel generation failed: {result}")
                    if batch:
                        failed_panels.append(batch[0].get("panel_number", 0))
                elif result is not None:
                    generated_panels.append(result)
                else:
                    if batch:
                        failed_panels.append(batch[0].get("panel_number", 0))

        total_time = time.time() - start_time

        output = ArtDepartmentOutput(
            hero_id=validated_input.hero_id,
            episode_number=validated_input.episode_number,
            generated_panels=generated_panels,
            total_generation_time=total_time,
            failed_panels=failed_panels,
        )
        return output.model_dump()

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input data."""
        try:
            ArtDepartmentInput(**input_data)
            return True
        except Exception:
            return False

    def get_output_schema(self) -> dict[str, Any]:
        """Return output schema."""
        return ArtDepartmentOutput.model_json_schema()

    def _build_generation_prompt(
        self,
        panel: PanelRequest,
        hero_name: str,
        style_preset: str,
        character_sheet: dict[str, Any] | None,
    ) -> str:
        """Build the image generation prompt."""
        style = STYLE_PRESETS.get(style_preset, STYLE_PRESETS["comic_book"])

        # Base prompt from panel description
        prompt_parts = [
            panel.visual_prompt,
            f"Style: {style}",
            f"Scene mood: {panel.mood}",
            f"Time of day: {panel.time_of_day}",
            f"Location: {panel.location}",
        ]

        # Add character consistency hints
        if character_sheet:
            visual_desc = character_sheet.get("visual_description", "")
            costume_desc = character_sheet.get("costume_description", "")
            if visual_desc:
                prompt_parts.append(f"Main character ({hero_name}): {visual_desc}")
            if costume_desc:
                prompt_parts.append(f"Costume: {costume_desc}")

        # Add action context
        if panel.action:
            prompt_parts.append(f"Action: {panel.action}")

        return ". ".join(prompt_parts)

    async def _generate_panel(
        self,
        panel: PanelRequest,
        hero_name: str,
        hero_id: str,
        episode_number: int,
        style_preset: str,
        character_sheet: dict[str, Any] | None,
        content_settings: dict[str, Any],
    ) -> GeneratedPanel | None:
        """Generate a single panel image."""
        self._ensure_initialized()

        # Build the generation prompt
        prompt = self._build_generation_prompt(
            panel=panel,
            hero_name=hero_name,
            style_preset=style_preset,
            character_sheet=character_sheet,
        )

        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                if self._model is None:
                    logger.warning("Imagen model not initialized, returning placeholder")
                    return self._generate_placeholder_panel(panel, prompt)

                # Generate image using Imagen 3
                response = self._model.generate_images(
                    prompt=prompt,
                    number_of_images=1,
                    aspect_ratio="3:4",  # Comic panel aspect ratio
                    safety_filter_level="block_some",
                    person_generation="allow_adult",
                    negative_prompt=NEGATIVE_PROMPT,
                )

                if not response.images:
                    logger.warning(f"No images generated for panel {panel.panel_number}")
                    retry_count += 1
                    continue

                # Get the generated image
                generated_image = response.images[0]

                # Upload to GCS
                image_url = await self._upload_to_gcs(
                    image_data=generated_image._image_bytes,
                    hero_id=hero_id,
                    episode_number=episode_number,
                    panel_number=panel.panel_number,
                )

                return GeneratedPanel(
                    panel_number=panel.panel_number,
                    image_url=image_url,
                    generation_prompt=prompt,
                    safety_score=1.0,
                    retry_count=retry_count,
                )

            except Exception as e:
                logger.error(f"Error generating panel {panel.panel_number}: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(1)  # Brief delay before retry

        # All retries failed
        logger.error(f"Failed to generate panel {panel.panel_number} after {max_retries} retries")
        return self._generate_placeholder_panel(panel, prompt)

    def _generate_placeholder_panel(
        self,
        panel: PanelRequest,
        prompt: str,
    ) -> GeneratedPanel:
        """Generate a placeholder panel when image generation fails."""
        # Return a placeholder URL that the frontend can handle
        return GeneratedPanel(
            panel_number=panel.panel_number,
            image_url=f"placeholder://panel_{panel.panel_number}",
            generation_prompt=prompt,
            safety_score=0.0,
            retry_count=3,
        )

    async def _upload_to_gcs(
        self,
        image_data: bytes,
        hero_id: str,
        episode_number: int,
        panel_number: int,
    ) -> str:
        """Upload generated image to Google Cloud Storage."""
        if self._storage_client is None:
            logger.warning("GCS client not initialized")
            return f"placeholder://panel_{panel_number}"

        try:
            bucket = self._storage_client.bucket(self._bucket_name)

            # Generate unique filename
            unique_id = uuid.uuid4().hex[:8]
            blob_path = f"heroes/{hero_id}/episodes/{episode_number}/panel_{panel_number}_{unique_id}.png"

            blob = bucket.blob(blob_path)
            blob.upload_from_string(image_data, content_type="image/png")

            # Make publicly readable (or use signed URLs for private access)
            blob.make_public()

            return blob.public_url

        except Exception as e:
            logger.error(f"Failed to upload to GCS: {e}")
            return f"placeholder://panel_{panel_number}"

    async def generate_character_sheet(
        self,
        hero_id: str,
        hero_name: str,
        visual_description: str,
        costume_description: str,
        power_type: str,
    ) -> dict[str, Any]:
        """Generate a character reference sheet for consistency."""
        self._ensure_initialized()

        # Build comprehensive character prompt
        prompt = (
            f"Character reference sheet for comic book hero. "
            f"Character name: {hero_name}. "
            f"Appearance: {visual_description}. "
            f"Costume: {costume_description}. "
            f"Powers: {power_type}. "
            f"Show character in T-pose with front view, clean background, "
            f"full body visible, {STYLE_PRESETS['comic_book']}"
        )

        try:
            if self._model is None:
                logger.warning("Imagen model not initialized for character sheet")
                return {
                    "hero_id": hero_id,
                    "hero_name": hero_name,
                    "visual_description": visual_description,
                    "costume_description": costume_description,
                    "reference_images": [],
                }

            response = self._model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="1:1",
                safety_filter_level="block_some",
                person_generation="allow_adult",
                negative_prompt=NEGATIVE_PROMPT,
            )

            if response.images:
                image_url = await self._upload_to_gcs(
                    image_data=response.images[0]._image_bytes,
                    hero_id=hero_id,
                    episode_number=0,  # Character sheet stored at episode 0
                    panel_number=0,
                )

                return {
                    "hero_id": hero_id,
                    "hero_name": hero_name,
                    "visual_description": visual_description,
                    "costume_description": costume_description,
                    "reference_images": [image_url],
                }

        except Exception as e:
            logger.error(f"Failed to generate character sheet: {e}")

        return {
            "hero_id": hero_id,
            "hero_name": hero_name,
            "visual_description": visual_description,
            "costume_description": costume_description,
            "reference_images": [],
        }
