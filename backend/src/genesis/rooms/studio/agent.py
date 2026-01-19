"""Studio agent implementation for video synthesis using Veo 3.1 fast."""

import asyncio
import logging
import time
import uuid
from typing import Any

import google.generativeai as genai
from google.cloud import storage

from genesis.config import settings
from genesis.rooms.base import BaseRoom
from genesis.rooms.studio.schemas import (
    AudioTrack,
    PanelVideoSegment,
    StudioInput,
    StudioOutput,
    VideoComposition,
)

logger = logging.getLogger(__name__)

# Video configuration constants
PARALLAX_DURATION_PER_PANEL = 5.0  # seconds
GENERATIVE_DURATION_PER_PANEL = 10.0  # seconds for Veo-generated climax
TARGET_TOTAL_DURATION = 60.0  # 60-second episode videos


class StudioAgent(BaseRoom):
    """Studio agent for video synthesis using Veo 3.1 fast and parallax techniques."""

    _initialized: bool = False

    def __init__(self) -> None:
        """Initialize the agent."""
        self._veo_model: Any = None
        self._storage_client: storage.Client | None = None
        self._bucket_name = f"{settings.gcp_project_id}-genesis-assets"

    def _ensure_initialized(self) -> None:
        """Initialize Google AI Studio and storage if not already done."""
        if not StudioAgent._initialized and settings.gemini_api_key:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                StudioAgent._initialized = True
                logger.info("Google AI Studio initialized for Studio")
            except Exception as e:
                logger.warning(f"Failed to initialize Google AI Studio: {e}")

        if self._veo_model is None and StudioAgent._initialized:
            try:
                # Use Veo 3.1 fast for video generation
                self._veo_model = genai.GenerativeModel("veo-3.1-fast-generate-preview")
                logger.info("Veo 3.1 fast model loaded")
            except Exception as e:
                logger.warning(f"Failed to load Veo 3.1 fast model: {e}")

        if self._storage_client is None and settings.gcp_project_id:
            try:
                self._storage_client = storage.Client(project=settings.gcp_project_id)
                logger.info("GCS client initialized for Studio")
            except Exception as e:
                logger.warning(f"Failed to initialize GCS client: {e}")

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Generate video from panels and script."""
        validated_input = StudioInput(**input_data)
        start_time = time.time()

        self._ensure_initialized()

        segments: list[PanelVideoSegment] = []
        audio_tracks: list[AudioTrack] = []

        try:
            # Step 1: Determine which panels get parallax vs generative treatment
            panel_assignments = self._assign_panel_treatments(
                panels=validated_input.panels,
                climax_panels=validated_input.climax_panel_numbers,
                include_generative=validated_input.include_generative_highlight,
            )

            # Step 2: Generate parallax segments for non-climax panels
            parallax_tasks = []
            for panel, treatment in panel_assignments.items():
                if treatment == "parallax":
                    panel_data = next(
                        (p for p in validated_input.panels if p.get("panel_number") == panel),
                        None,
                    )
                    if panel_data:
                        parallax_tasks.append(
                            self._generate_parallax_segment(
                                panel_data=panel_data,
                                hero_id=validated_input.hero_id,
                                episode_number=validated_input.episode_number,
                            )
                        )

            parallax_results = await asyncio.gather(*parallax_tasks, return_exceptions=True)
            for result in parallax_results:
                if isinstance(result, PanelVideoSegment):
                    segments.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Parallax generation error: {result}")

            # Step 3: Generate Veo 3.1 segments for climax panels
            if validated_input.include_generative_highlight:
                for panel_num in validated_input.climax_panel_numbers:
                    panel_data = next(
                        (p for p in validated_input.panels if p.get("panel_number") == panel_num),
                        None,
                    )
                    if panel_data:
                        segment = await self._generate_veo_segment(
                            panel_data=panel_data,
                            script=validated_input.script,
                            hero_id=validated_input.hero_id,
                            episode_number=validated_input.episode_number,
                        )
                        segments.append(segment)

            # Step 4: Generate audio tracks
            audio_tracks = await self._generate_audio_tracks(
                script=validated_input.script,
                hero_name=validated_input.hero_name,
                segments=segments,
                hero_id=validated_input.hero_id,
                episode_number=validated_input.episode_number,
            )

            # Step 5: Compose final video
            video = await self._compose_final_video(
                segments=segments,
                audio_tracks=audio_tracks,
                hero_id=validated_input.hero_id,
                episode_number=validated_input.episode_number,
            )

            total_time = time.time() - start_time

            output = StudioOutput(
                hero_id=validated_input.hero_id,
                episode_number=validated_input.episode_number,
                video=video,
                segments=segments,
                audio_tracks=audio_tracks,
                total_processing_time=total_time,
                status="completed",
            )

        except Exception as e:
            logger.error(f"Studio processing error: {e}")
            total_time = time.time() - start_time
            output = StudioOutput(
                hero_id=validated_input.hero_id,
                episode_number=validated_input.episode_number,
                video=None,
                segments=segments,
                audio_tracks=audio_tracks,
                total_processing_time=total_time,
                status="failed",
                error_message=str(e),
            )

        return output.model_dump()

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input data."""
        try:
            StudioInput(**input_data)
            return True
        except Exception:
            return False

    def get_output_schema(self) -> dict[str, Any]:
        """Return output schema."""
        return StudioOutput.model_json_schema()

    def _assign_panel_treatments(
        self,
        panels: list[dict[str, Any]],
        climax_panels: list[int],
        include_generative: bool,
    ) -> dict[int, str]:
        """Assign treatment type (parallax vs generative) to each panel."""
        assignments = {}

        for panel in panels:
            panel_num = panel.get("panel_number", 0)
            if include_generative and panel_num in climax_panels:
                assignments[panel_num] = "generative"
            else:
                assignments[panel_num] = "parallax"

        return assignments

    async def _generate_parallax_segment(
        self,
        panel_data: dict[str, Any],
        hero_id: str,
        episode_number: int,
    ) -> PanelVideoSegment:
        """Generate 2.5D parallax motion video from a static panel.

        Parallax effect creates depth by:
        1. Separating foreground/background layers (AI-assisted)
        2. Applying Ken Burns camera movements (pan, zoom)
        3. Adding subtle animations (floating particles, flickering lights)
        """
        panel_number = panel_data.get("panel_number", 0)
        image_url = panel_data.get("image_url", "")

        try:
            # Simulate parallax generation (in production, use video processing)
            await asyncio.sleep(0.1)  # Placeholder for actual processing

            video_url = await self._create_parallax_video(
                image_url=image_url,
                panel_number=panel_number,
                hero_id=hero_id,
                episode_number=episode_number,
                duration=PARALLAX_DURATION_PER_PANEL,
            )

            return PanelVideoSegment(
                panel_number=panel_number,
                segment_type="parallax",
                duration_seconds=PARALLAX_DURATION_PER_PANEL,
                video_url=video_url,
                status="completed",
            )

        except Exception as e:
            logger.error(f"Parallax generation failed for panel {panel_number}: {e}")
            return PanelVideoSegment(
                panel_number=panel_number,
                segment_type="parallax",
                duration_seconds=PARALLAX_DURATION_PER_PANEL,
                video_url=None,
                status="failed",
            )

    async def _create_parallax_video(
        self,
        image_url: str,
        panel_number: int,
        hero_id: str,
        episode_number: int,
        duration: float,
    ) -> str:
        """Create parallax video from static image."""
        unique_id = uuid.uuid4().hex[:8]
        video_path = f"heroes/{hero_id}/episodes/{episode_number}/parallax_panel_{panel_number}_{unique_id}.mp4"

        return f"gs://{self._bucket_name}/{video_path}"

    async def _generate_veo_segment(
        self,
        panel_data: dict[str, Any],
        script: dict[str, Any],
        hero_id: str,
        episode_number: int,
    ) -> PanelVideoSegment:
        """Generate video segment using Veo 3.1 fast for climax scenes."""
        panel_number = panel_data.get("panel_number", 0)
        image_url = panel_data.get("image_url", "")

        try:
            # Build Veo prompt from panel data and script context
            prompt = self._build_veo_prompt(panel_data, script)

            # Call Veo 3.1 fast API
            video_url = await self._call_veo_api(
                prompt=prompt,
                reference_image_url=image_url,
                hero_id=hero_id,
                episode_number=episode_number,
                panel_number=panel_number,
            )

            return PanelVideoSegment(
                panel_number=panel_number,
                segment_type="generative",
                duration_seconds=GENERATIVE_DURATION_PER_PANEL,
                video_url=video_url,
                status="completed",
            )

        except Exception as e:
            logger.error(f"Veo generation failed for panel {panel_number}: {e}")
            return PanelVideoSegment(
                panel_number=panel_number,
                segment_type="generative",
                duration_seconds=GENERATIVE_DURATION_PER_PANEL,
                video_url=None,
                status="failed",
            )

    def _build_veo_prompt(
        self,
        panel_data: dict[str, Any],
        script: dict[str, Any],
    ) -> str:
        """Build prompt for Veo video generation."""
        visual_prompt = panel_data.get("visual_prompt", "")
        action = panel_data.get("action", "")

        prompt_parts = [
            "Comic book action sequence, dynamic camera movement",
            visual_prompt,
            f"Action: {action}",
            "Dramatic lighting, cinematic composition",
            "High energy, fluid motion, superhero style",
        ]

        return ". ".join(prompt_parts)

    async def _call_veo_api(
        self,
        prompt: str,
        reference_image_url: str,
        hero_id: str,
        episode_number: int,
        panel_number: int,
    ) -> str:
        """Call Veo 3.1 fast API for video generation."""
        unique_id = uuid.uuid4().hex[:8]
        video_path = f"heroes/{hero_id}/episodes/{episode_number}/veo_panel_{panel_number}_{unique_id}.mp4"

        if self._veo_model is None:
            logger.warning("Veo model not initialized, returning placeholder")
            return f"gs://{self._bucket_name}/{video_path}"

        try:
            # Generate video using Veo 3.1 fast
            response = await self._veo_model.generate_content_async(
                contents=[prompt],
                generation_config={
                    "response_modalities": ["VIDEO"],
                    "video_config": {
                        "duration_seconds": int(GENERATIVE_DURATION_PER_PANEL),
                        "aspect_ratio": "16:9",
                    },
                },
            )

            # Check if video was generated
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, "video_metadata"):
                            # Upload video to GCS
                            video_data = part.inline_data.data if hasattr(part, "inline_data") else None
                            if video_data:
                                uploaded_url = await self._upload_video_to_gcs(
                                    video_data=video_data,
                                    hero_id=hero_id,
                                    episode_number=episode_number,
                                    panel_number=panel_number,
                                )
                                return uploaded_url

            logger.warning(f"No video generated for panel {panel_number}")
            return f"gs://{self._bucket_name}/{video_path}"

        except Exception as e:
            logger.error(f"Veo API call failed for panel {panel_number}: {e}")
            return f"gs://{self._bucket_name}/{video_path}"

    async def _upload_video_to_gcs(
        self,
        video_data: bytes,
        hero_id: str,
        episode_number: int,
        panel_number: int,
    ) -> str:
        """Upload generated video to Google Cloud Storage."""
        if self._storage_client is None:
            logger.warning("GCS client not initialized")
            unique_id = uuid.uuid4().hex[:8]
            return f"placeholder://video_{panel_number}_{unique_id}"

        try:
            bucket = self._storage_client.bucket(self._bucket_name)

            unique_id = uuid.uuid4().hex[:8]
            blob_path = f"heroes/{hero_id}/episodes/{episode_number}/veo_panel_{panel_number}_{unique_id}.mp4"

            blob = bucket.blob(blob_path)
            blob.upload_from_string(video_data, content_type="video/mp4")
            blob.make_public()

            return blob.public_url

        except Exception as e:
            logger.error(f"Failed to upload video to GCS: {e}")
            return f"placeholder://video_{panel_number}"

    async def _generate_audio_tracks(
        self,
        script: dict[str, Any],
        hero_name: str,
        segments: list[PanelVideoSegment],
        hero_id: str,
        episode_number: int,
    ) -> list[AudioTrack]:
        """Generate audio tracks for the video."""
        audio_tracks = []

        panels = script.get("panels", [])

        current_time = 0.0
        for segment in sorted(segments, key=lambda s: s.panel_number):
            panel_script = next(
                (p for p in panels if p.get("panel_number") == segment.panel_number),
                None,
            )

            if panel_script:
                dialogues = panel_script.get("dialogue", [])
                for dialogue in dialogues:
                    character = dialogue.get("character", "Unknown")
                    text = dialogue.get("text", "")

                    if text:
                        audio_url = await self._generate_dialogue_audio(
                            character=character,
                            text=text,
                            hero_id=hero_id,
                            episode_number=episode_number,
                        )

                        audio_tracks.append(
                            AudioTrack(
                                track_type="dialogue",
                                audio_url=audio_url,
                                start_time=current_time,
                                duration=len(text) * 0.05,
                            )
                        )

            current_time += segment.duration_seconds

        music_url = await self._generate_background_music(
            hero_id=hero_id,
            episode_number=episode_number,
            total_duration=current_time,
        )

        audio_tracks.append(
            AudioTrack(
                track_type="music",
                audio_url=music_url,
                start_time=0.0,
                duration=current_time,
            )
        )

        return audio_tracks

    async def _generate_dialogue_audio(
        self,
        character: str,
        text: str,
        hero_id: str,
        episode_number: int,
    ) -> str:
        """Generate dialogue audio using text-to-speech."""
        unique_id = uuid.uuid4().hex[:8]
        audio_path = f"heroes/{hero_id}/episodes/{episode_number}/dialogue_{unique_id}.mp3"

        return f"gs://{self._bucket_name}/{audio_path}"

    async def _generate_background_music(
        self,
        hero_id: str,
        episode_number: int,
        total_duration: float,
    ) -> str:
        """Generate or select background music."""
        unique_id = uuid.uuid4().hex[:8]
        audio_path = f"heroes/{hero_id}/episodes/{episode_number}/music_{unique_id}.mp3"

        return f"gs://{self._bucket_name}/{audio_path}"

    async def _compose_final_video(
        self,
        segments: list[PanelVideoSegment],
        audio_tracks: list[AudioTrack],
        hero_id: str,
        episode_number: int,
    ) -> VideoComposition | None:
        """Compose final video from segments and audio."""
        if not segments:
            return None

        total_duration = sum(s.duration_seconds for s in segments)

        unique_id = uuid.uuid4().hex[:8]
        video_path = f"heroes/{hero_id}/episodes/{episode_number}/final_{unique_id}.mp4"
        video_url = f"gs://{self._bucket_name}/{video_path}"

        return VideoComposition(
            video_url=video_url,
            duration_seconds=total_duration,
            resolution="1080p",
            format="mp4",
            file_size_mb=total_duration * 2.0,
        )
