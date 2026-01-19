"""Canon updater job for nightly world state updates.

This job runs nightly to:
1. Detect emergent patterns from user episodes
2. Calculate significance scores
3. Promote significant events to Canon Layer
4. Update NPC awareness with new world state
"""

import logging
from datetime import datetime, timezone
from typing import Any

import vertexai
from vertexai.generative_models import GenerativeModel

from genesis.config import settings
from genesis.core.database import get_session

logger = logging.getLogger(__name__)

SIGNIFICANCE_THRESHOLD = 50.0


class CanonUpdaterJob:
    """Job to update the Canon Layer with emergent world events."""

    _initialized: bool = False

    def __init__(self) -> None:
        """Initialize the job."""
        self._model: GenerativeModel | None = None

    def _ensure_initialized(self) -> None:
        """Initialize Vertex AI if not already done."""
        if not CanonUpdaterJob._initialized and settings.gcp_project_id:
            try:
                vertexai.init(
                    project=settings.gcp_project_id,
                    location=settings.gcp_location,
                )
                CanonUpdaterJob._initialized = True
                self._model = GenerativeModel("gemini-2.0-flash")
                logger.info("Vertex AI initialized for Canon Updater")
            except Exception as e:
                logger.warning(f"Failed to initialize Vertex AI: {e}")

    async def run(self) -> dict[str, Any]:
        """Run the canon update job.

        Returns:
            Job execution statistics
        """
        start_time = datetime.now(timezone.utc)
        stats = {
            "started_at": start_time.isoformat(),
            "events_analyzed": 0,
            "events_promoted": 0,
            "npcs_updated": 0,
            "errors": [],
        }

        try:
            self._ensure_initialized()

            # Step 1: Gather today's episode events
            events = await self._gather_episode_events()
            stats["events_analyzed"] = len(events)
            logger.info(f"Gathered {len(events)} events from today's episodes")

            # Step 2: Calculate significance scores
            scored_events = await self._calculate_significance_scores(events)

            # Step 3: Promote significant events to Canon
            promoted = await self._promote_to_canon(scored_events)
            stats["events_promoted"] = len(promoted)
            logger.info(f"Promoted {len(promoted)} events to Canon Layer")

            # Step 4: Generate world state summary
            world_summary = await self._generate_world_summary(promoted)

            # Step 5: Update NPC awareness
            npcs_updated = await self._update_npc_awareness(world_summary)
            stats["npcs_updated"] = npcs_updated

        except Exception as e:
            logger.error(f"Canon update job failed: {e}")
            stats["errors"].append({"error": str(e)})

        stats["completed_at"] = datetime.now(timezone.utc).isoformat()
        stats["duration_seconds"] = (
            datetime.now(timezone.utc) - start_time
        ).total_seconds()

        return stats

    async def _gather_episode_events(self) -> list[dict[str, Any]]:
        """Gather significant events from today's generated episodes."""
        try:
            async with get_session() as session:
                result = await session.run(
                    """
                    MATCH (e:Episode)
                    WHERE date(e.generated_at) = date()
                    RETURN e {
                        .id, .hero_id, .title, .synopsis, .tags,
                        .canon_references
                    } as episode
                    """
                )
                records = await result.data()

                # Extract events from episodes
                events = []
                for record in records:
                    episode = record["episode"]
                    # Each tag/reference could be an event
                    for tag in episode.get("tags", []):
                        events.append({
                            "type": "tag",
                            "value": tag,
                            "episode_id": episode["id"],
                            "hero_id": episode["hero_id"],
                        })
                    for ref in episode.get("canon_references", []):
                        events.append({
                            "type": "canon_reference",
                            "value": ref,
                            "episode_id": episode["id"],
                            "hero_id": episode["hero_id"],
                        })

                return events
        except Exception as e:
            logger.warning(f"Could not gather episode events: {e}")
            return []

    async def _calculate_significance_scores(
        self,
        events: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Calculate significance scores for events.

        Scoring formula:
        - base_score: Event magnitude (1-10, estimated)
        - social_multiplier: 1 + (num_heroes_involved * 0.1)
        - novelty_bonus: 1.5 if event type never seen before
        - final_score = base_score * social_multiplier * novelty_bonus
        """
        # Group events by value to count occurrences
        event_counts: dict[str, int] = {}
        for event in events:
            key = f"{event['type']}:{event['value']}"
            event_counts[key] = event_counts.get(key, 0) + 1

        # Get existing canon events for novelty check
        existing_events = await self._get_existing_canon_events()
        existing_values = {e.get("title", "").lower() for e in existing_events}

        scored_events = []
        for key, count in event_counts.items():
            event_type, value = key.split(":", 1)

            # Base score (simplified - in production, use AI to estimate)
            base_score = 5.0

            # Social multiplier
            social_multiplier = 1 + (count * 0.1)

            # Novelty bonus
            novelty_bonus = 1.5 if value.lower() not in existing_values else 1.0

            final_score = base_score * social_multiplier * novelty_bonus

            scored_events.append({
                "type": event_type,
                "value": value,
                "occurrence_count": count,
                "base_score": base_score,
                "social_multiplier": social_multiplier,
                "novelty_bonus": novelty_bonus,
                "final_score": final_score,
            })

        # Sort by score descending
        scored_events.sort(key=lambda e: e["final_score"], reverse=True)

        return scored_events

    async def _get_existing_canon_events(self) -> list[dict[str, Any]]:
        """Get existing canon events for novelty comparison."""
        try:
            async with get_session() as session:
                result = await session.run(
                    """
                    MATCH (e:Event)
                    WHERE e.layer = 'canon'
                    RETURN e {.title, .description} as event
                    """
                )
                records = await result.data()
                return [record["event"] for record in records]
        except Exception as e:
            logger.warning(f"Could not fetch existing canon events: {e}")
            return []

    async def _promote_to_canon(
        self,
        scored_events: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Promote high-scoring events to the Canon Layer."""
        promoted = []

        for event in scored_events:
            if event["final_score"] >= SIGNIFICANCE_THRESHOLD:
                # Generate canon event description using AI
                description = await self._generate_event_description(event)

                try:
                    async with get_session() as session:
                        await session.run(
                            """
                            CREATE (e:Event {
                                id: randomUUID(),
                                title: $title,
                                description: $description,
                                layer: 'canon',
                                significance_score: $score,
                                status: 'active',
                                created_at: datetime(),
                                start_date: date(),
                                source: 'emergent'
                            })
                            """,
                            title=event["value"],
                            description=description,
                            score=event["final_score"],
                        )
                        promoted.append({
                            "title": event["value"],
                            "description": description,
                            "score": event["final_score"],
                        })
                        logger.info(f"Promoted event to Canon: {event['value']}")
                except Exception as e:
                    logger.error(f"Failed to promote event {event['value']}: {e}")

        return promoted

    async def _generate_event_description(self, event: dict[str, Any]) -> str:
        """Generate a canon event description using AI."""
        if self._model is None:
            return f"A significant event occurred: {event['value']}"

        try:
            prompt = f"""
            Generate a brief, dramatic description (2-3 sentences) for a comic book universe
            canon event based on this emergent pattern from hero stories:

            Event: {event['value']}
            Type: {event['type']}
            Occurrence count: {event['occurrence_count']}

            The description should:
            - Be suitable for a shared superhero universe
            - Hint at broader implications
            - Be written in present tense
            """

            response = await self._model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            logger.warning(f"Failed to generate event description: {e}")
            return f"A significant event occurred: {event['value']}"

    async def _generate_world_summary(
        self,
        promoted_events: list[dict[str, Any]],
    ) -> str:
        """Generate a summary of today's world state changes."""
        if not promoted_events:
            return "The world remains unchanged today."

        if self._model is None:
            event_titles = [e["title"] for e in promoted_events]
            return f"Today's events: {', '.join(event_titles)}"

        try:
            events_text = "\n".join(
                f"- {e['title']}: {e['description']}"
                for e in promoted_events
            )

            prompt = f"""
            Summarize today's events in the Genesis Protocol universe in a single paragraph
            (3-4 sentences). This summary will be used to update NPC awareness.

            Today's events:
            {events_text}

            Write in present tense, as if reporting current events in a living world.
            """

            response = await self._model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            logger.warning(f"Failed to generate world summary: {e}")
            event_titles = [e["title"] for e in promoted_events]
            return f"Today's events: {', '.join(event_titles)}"

    async def _update_npc_awareness(self, world_summary: str) -> int:
        """Update NPC knowledge with the new world state."""
        updated_count = 0

        try:
            async with get_session() as session:
                # Get all NPCs
                result = await session.run(
                    """
                    MATCH (n:NPC)
                    WHERE n.status = 'active'
                    RETURN n.id as id
                    """
                )
                records = await result.data()

                # Update each NPC's world knowledge
                for record in records:
                    npc_id = record["id"]
                    await session.run(
                        """
                        MATCH (n:NPC {id: $npc_id})
                        SET n.world_state_summary = $summary,
                            n.world_state_updated = datetime()
                        """,
                        npc_id=npc_id,
                        summary=world_summary,
                    )
                    updated_count += 1

                logger.info(f"Updated world awareness for {updated_count} NPCs")

        except Exception as e:
            logger.warning(f"Could not update NPC awareness: {e}")

        return updated_count
