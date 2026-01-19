"""Daily episode generation job.

This job is triggered by Cloud Scheduler to generate daily episodes for all active heroes.
It orchestrates the Writers Room -> Art Department -> Studio pipeline.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from genesis.core.database import get_session
from genesis.rooms.writers_room import WritersRoomAgent
from genesis.rooms.art_department import ArtDepartmentAgent
from genesis.rooms.studio import StudioAgent

logger = logging.getLogger(__name__)


class EpisodeGeneratorJob:
    """Job to generate daily episodes for heroes."""

    def __init__(self) -> None:
        """Initialize the job with required agents."""
        self.writers_room = WritersRoomAgent()
        self.art_department = ArtDepartmentAgent()
        self.studio = StudioAgent()

    async def run(self, batch_size: int = 50) -> dict[str, Any]:
        """Run the episode generation job for all active heroes.

        Args:
            batch_size: Number of heroes to process in parallel

        Returns:
            Job execution statistics
        """
        start_time = datetime.now(timezone.utc)
        stats = {
            "started_at": start_time.isoformat(),
            "heroes_processed": 0,
            "episodes_generated": 0,
            "failures": 0,
            "errors": [],
        }

        try:
            # Get all active heroes that need episodes today
            heroes = await self._get_heroes_needing_episodes()
            logger.info(f"Found {len(heroes)} heroes needing episodes")

            # Process in batches
            for i in range(0, len(heroes), batch_size):
                batch = heroes[i : i + batch_size]
                results = await asyncio.gather(
                    *[self._generate_episode_for_hero(hero) for hero in batch],
                    return_exceptions=True,
                )

                for hero, result in zip(batch, results):
                    stats["heroes_processed"] += 1
                    if isinstance(result, Exception):
                        stats["failures"] += 1
                        stats["errors"].append({
                            "hero_id": hero.get("id"),
                            "error": str(result),
                        })
                        logger.error(f"Failed to generate episode for {hero.get('id')}: {result}")
                    else:
                        stats["episodes_generated"] += 1

        except Exception as e:
            logger.error(f"Episode generation job failed: {e}")
            stats["errors"].append({"error": str(e)})

        stats["completed_at"] = datetime.now(timezone.utc).isoformat()
        stats["duration_seconds"] = (
            datetime.now(timezone.utc) - start_time
        ).total_seconds()

        logger.info(
            f"Episode generation completed: {stats['episodes_generated']} generated, "
            f"{stats['failures']} failures in {stats['duration_seconds']:.2f}s"
        )

        return stats

    async def run_for_hero(self, hero_id: str) -> dict[str, Any]:
        """Generate an episode for a specific hero.

        Args:
            hero_id: The hero's ID

        Returns:
            Episode generation result
        """
        hero = await self._get_hero(hero_id)
        if not hero:
            raise ValueError(f"Hero not found: {hero_id}")

        return await self._generate_episode_for_hero(hero)

    async def _get_heroes_needing_episodes(self) -> list[dict[str, Any]]:
        """Get all heroes that need episodes generated today."""
        try:
            async with get_session() as session:
                result = await session.run(
                    """
                    MATCH (h:Hero)
                    WHERE h.status = 'active'
                    AND (h.last_episode_date IS NULL OR h.last_episode_date < date())
                    RETURN h {
                        .id, .hero_name, .power_type, .origin_story,
                        .current_location, .episode_count,
                        .content_settings, .character_sheet
                    } as hero
                    ORDER BY h.last_episode_date ASC
                    """
                )
                records = await result.data()
                return [record["hero"] for record in records]
        except Exception as e:
            logger.warning(f"Could not fetch heroes from Neo4j: {e}")
            return []

    async def _get_hero(self, hero_id: str) -> dict[str, Any] | None:
        """Get a specific hero by ID."""
        try:
            async with get_session() as session:
                result = await session.run(
                    """
                    MATCH (h:Hero {id: $hero_id})
                    RETURN h {
                        .id, .hero_name, .power_type, .origin_story,
                        .current_location, .episode_count,
                        .content_settings, .character_sheet
                    } as hero
                    """,
                    hero_id=hero_id,
                )
                record = await result.single()
                return record["hero"] if record else None
        except Exception as e:
            logger.warning(f"Could not fetch hero from Neo4j: {e}")
            return None

    async def _get_previous_episodes_summary(self, hero_id: str) -> str:
        """Get a summary of the hero's previous episodes."""
        try:
            async with get_session() as session:
                result = await session.run(
                    """
                    MATCH (h:Hero {id: $hero_id})-[:HAS_EPISODE]->(e:Episode)
                    RETURN e.synopsis as synopsis
                    ORDER BY e.episode_number DESC
                    LIMIT 5
                    """,
                    hero_id=hero_id,
                )
                records = await result.data()
                if not records:
                    return "This is the hero's first adventure."

                summaries = [r["synopsis"] for r in records if r.get("synopsis")]
                return " ".join(summaries[:3]) if summaries else "The hero has had previous adventures."
        except Exception as e:
            logger.warning(f"Could not fetch episode history: {e}")
            return "The hero has had previous adventures."

    async def _get_canon_events(self) -> list[dict[str, Any]]:
        """Get active canon events that should influence episodes."""
        try:
            async with get_session() as session:
                result = await session.run(
                    """
                    MATCH (e:Event)
                    WHERE e.status = 'active'
                    AND e.start_date <= date()
                    AND (e.end_date IS NULL OR e.end_date >= date())
                    RETURN e {.title, .description, .significance_score} as event
                    ORDER BY e.significance_score DESC
                    LIMIT 5
                    """
                )
                records = await result.data()
                return [record["event"] for record in records]
        except Exception as e:
            logger.warning(f"Could not fetch canon events: {e}")
            return []

    async def _generate_episode_for_hero(self, hero: dict[str, Any]) -> dict[str, Any]:
        """Generate a complete episode for a hero.

        This orchestrates the full pipeline:
        1. Writers Room generates the script
        2. Art Department generates panel images
        3. Studio generates the video

        Args:
            hero: Hero data dictionary

        Returns:
            Generated episode data
        """
        hero_id = hero.get("id", "unknown")
        hero_name = hero.get("hero_name", "Hero")
        episode_number = (hero.get("episode_count") or 0) + 1

        logger.info(f"Generating episode {episode_number} for {hero_name} ({hero_id})")

        # Get context for generation
        previous_summary = await self._get_previous_episodes_summary(hero_id)
        canon_events = await self._get_canon_events()

        # Step 1: Generate script with Writers Room
        writers_input = {
            "hero_name": hero_name,
            "power_type": hero.get("power_type", "Unknown"),
            "origin_story": hero.get("origin_story", ""),
            "current_location": hero.get("current_location", "Metropolis Prime"),
            "episode_number": episode_number,
            "previous_episodes_summary": previous_summary,
            "active_canon_events": canon_events,
            "content_settings": hero.get("content_settings", {}),
            "include_crossover": False,
            "crossover_hero": None,
        }

        script_result = await self.writers_room.process(writers_input)
        script = script_result.get("script", {})

        logger.info(f"Script generated for {hero_name}: {script.get('title', 'Untitled')}")

        # Step 2: Generate panel images with Art Department
        art_input = {
            "hero_id": hero_id,
            "hero_name": hero_name,
            "episode_number": episode_number,
            "character_sheet": hero.get("character_sheet"),
            "panels": script.get("panels", []),
            "style_preset": "comic_book",
            "content_settings": hero.get("content_settings", {}),
        }

        art_result = await self.art_department.process(art_input)
        generated_panels = art_result.get("generated_panels", [])

        logger.info(f"Generated {len(generated_panels)} panels for {hero_name}")

        # Step 3: Generate video with Studio
        # Identify climax panels (usually the last 2)
        panel_numbers = [p.get("panel_number", 0) for p in script.get("panels", [])]
        climax_panels = panel_numbers[-2:] if len(panel_numbers) >= 2 else panel_numbers

        studio_input = {
            "hero_id": hero_id,
            "hero_name": hero_name,
            "episode_number": episode_number,
            "panels": [
                {**p, "image_url": next(
                    (gp.get("image_url") for gp in generated_panels
                     if gp.get("panel_number") == p.get("panel_number")),
                    None
                )}
                for p in script.get("panels", [])
            ],
            "script": script,
            "content_settings": hero.get("content_settings", {}),
            "include_generative_highlight": True,
            "climax_panel_numbers": climax_panels,
        }

        video_result = await self.studio.process(studio_input)

        logger.info(f"Video generated for {hero_name}")

        # Save episode to database
        episode_data = {
            "hero_id": hero_id,
            "episode_number": episode_number,
            "title": script.get("title", f"Episode {episode_number}"),
            "synopsis": script.get("synopsis", ""),
            "script": script,
            "panels": generated_panels,
            "video": video_result.get("video"),
            "tags": script.get("tags", []),
            "canon_references": script.get("canon_references", []),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        await self._save_episode(hero_id, episode_data)

        return episode_data

    async def _save_episode(self, hero_id: str, episode_data: dict[str, Any]) -> None:
        """Save generated episode to the database."""
        try:
            async with get_session() as session:
                await session.run(
                    """
                    MATCH (h:Hero {id: $hero_id})
                    CREATE (e:Episode {
                        id: randomUUID(),
                        hero_id: $hero_id,
                        episode_number: $episode_number,
                        title: $title,
                        synopsis: $synopsis,
                        tags: $tags,
                        generated_at: datetime($generated_at)
                    })
                    CREATE (h)-[:HAS_EPISODE]->(e)
                    SET h.episode_count = $episode_number,
                        h.last_episode_date = date()
                    """,
                    hero_id=hero_id,
                    episode_number=episode_data["episode_number"],
                    title=episode_data["title"],
                    synopsis=episode_data["synopsis"],
                    tags=episode_data.get("tags", []),
                    generated_at=episode_data["generated_at"],
                )
                logger.info(f"Saved episode {episode_data['episode_number']} for hero {hero_id}")
        except Exception as e:
            logger.error(f"Failed to save episode to database: {e}")
