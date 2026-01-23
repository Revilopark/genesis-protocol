"""Hero service for business logic."""

from neo4j import AsyncSession

from genesis.core.exceptions import NotFoundError, ValidationError
from genesis.heroes.repository import HeroRepository
from genesis.heroes.schemas import (
    ContentSettings,
    EpisodeSummary,
    HeroCreate,
    HeroEpisode,
    HeroResponse,
    HeroStatus,
    HeroSummary,
    HeroUpdate,
    HeroWithEpisodes,
    Panel,
    PanelDialogue,
    PowerType,
    Script,
    VideoInfo,
)


class HeroService:
    """Business logic for Hero operations."""

    def __init__(self, session: AsyncSession):
        self.repo = HeroRepository(session)

    async def create_hero(
        self,
        user_id: str,
        data: HeroCreate,
        sponsor_id: str,
    ) -> HeroResponse:
        """Create a new Hero for a user."""
        # Check if user already has a hero
        existing = await self.repo.get_hero_by_user_id(user_id)
        if existing:
            raise ValidationError("User already has a hero")

        hero = await self.repo.create_hero(user_id, data, sponsor_id)
        return self._to_hero_response(hero)

    async def get_hero(self, user_id: str) -> HeroResponse:
        """Get Hero by user ID."""
        hero = await self.repo.get_hero_by_user_id(user_id)
        if not hero:
            raise NotFoundError("Hero not found")
        return self._to_hero_response(hero)

    async def get_hero_by_id(self, hero_id: str) -> HeroResponse:
        """Get Hero by hero ID."""
        hero = await self.repo.get_hero_by_id(hero_id)
        if not hero:
            raise NotFoundError("Hero not found")
        return self._to_hero_response(hero)

    async def get_hero_with_episodes(
        self,
        hero_id: str,
        limit: int = 10,
    ) -> HeroWithEpisodes:
        """Get Hero with recent episodes."""
        result = await self.repo.get_hero_with_episodes(hero_id, limit)
        if not result:
            raise NotFoundError("Hero not found")

        hero_response = self._to_hero_response(result["hero"])
        episodes = [
            EpisodeSummary(
                id=e["id"],
                episode_number=e["episode_number"],
                title=e["title"],
                comic_url=e.get("comic_url"),
                video_url=e.get("video_url"),
                generated_at=e["generated_at"],
            )
            for e in result["episodes"]
        ]

        return HeroWithEpisodes(hero=hero_response, recent_episodes=episodes)

    async def update_hero(
        self,
        hero_id: str,
        data: HeroUpdate,
        user_id: str,
    ) -> HeroResponse:
        """Update Hero properties."""
        # Verify ownership
        hero = await self.repo.get_hero_by_id(hero_id)
        if not hero:
            raise NotFoundError("Hero not found")
        if hero["user_id"] != user_id:
            raise ValidationError("Not authorized to update this hero")

        updated = await self.repo.update_hero(hero_id, data)
        if not updated:
            raise NotFoundError("Hero not found")
        return self._to_hero_response(updated)

    async def activate_hero(
        self,
        hero_id: str,
        sponsor_id: str,
    ) -> HeroResponse:
        """Activate a Hero after guardian approval."""
        # Verify guardian owns this hero
        is_owner = await self.repo.verify_guardian_ownership(hero_id, sponsor_id)
        if not is_owner:
            raise ValidationError("Not authorized to activate this hero")

        success = await self.repo.update_status(hero_id, HeroStatus.ACTIVE)
        if not success:
            raise NotFoundError("Hero not found")

        hero = await self.repo.get_hero_by_id(hero_id)
        if not hero:
            raise NotFoundError("Hero not found")
        return self._to_hero_response(hero)

    async def get_guardian_children(
        self,
        sponsor_id: str,
    ) -> list[HeroSummary]:
        """Get all heroes sponsored by a guardian."""
        heroes = await self.repo.get_heroes_by_sponsor(sponsor_id)
        return [
            HeroSummary(
                id=h["id"],
                hero_name=h["hero_name"],
                power_type=PowerType(h["power_type"]),
                status=HeroStatus(h["status"]),
                power_level=h["power_level"],
            )
            for h in heroes
        ]

    async def get_hero_episodes(
        self,
        hero_id: str,
        limit: int = 10,
    ) -> list[HeroEpisode]:
        """Get all episodes for a hero."""
        episodes = await self.repo.get_hero_episodes(hero_id, limit)
        return [self._to_hero_episode(e) for e in episodes]

    async def get_hero_latest_episode(self, hero_id: str) -> HeroEpisode:
        """Get the latest episode for a hero."""
        episode = await self.repo.get_hero_latest_episode(hero_id)
        if not episode:
            raise NotFoundError("No episodes found for this hero")
        return self._to_hero_episode(episode)

    async def get_hero_episode(
        self,
        hero_id: str,
        episode_number: int,
    ) -> HeroEpisode:
        """Get a specific episode by number."""
        episode = await self.repo.get_hero_episode(hero_id, episode_number)
        if not episode:
            raise NotFoundError(f"Episode {episode_number} not found")
        return self._to_hero_episode(episode)

    def _to_hero_episode(self, episode: dict) -> HeroEpisode:  # type: ignore[type-arg]
        """Convert Neo4j episode result to HeroEpisode."""
        # Parse panels
        raw_panels = episode.get("panels", [])
        panels = []
        for p in raw_panels:
            dialogue = [
                PanelDialogue(character=d.get("character", ""), text=d.get("text", ""))
                for d in p.get("dialogue", [])
            ]
            panels.append(
                Panel(
                    panel_number=p.get("panel_number", 0),
                    image_url=p.get("image_url"),
                    generation_prompt=p.get("generation_prompt"),
                    visual_prompt=p.get("visual_prompt"),
                    dialogue=dialogue,
                    caption=p.get("caption"),
                    action=p.get("action"),
                    safety_score=p.get("safety_score", 1.0),
                    retry_count=p.get("retry_count", 0),
                )
            )

        # Parse script
        raw_script = episode.get("script", {})
        script_panels = []
        for p in raw_script.get("panels", []):
            dialogue = [
                PanelDialogue(character=d.get("character", ""), text=d.get("text", ""))
                for d in p.get("dialogue", [])
            ]
            script_panels.append(
                Panel(
                    panel_number=p.get("panel_number", 0),
                    visual_prompt=p.get("visual_prompt"),
                    dialogue=dialogue,
                    caption=p.get("caption"),
                    action=p.get("action"),
                )
            )

        script = Script(
            title=raw_script.get("title", episode.get("title", "")),
            synopsis=raw_script.get("synopsis", episode.get("synopsis", "")),
            panels=script_panels,
            canon_references=raw_script.get("canon_references", []),
            tags=raw_script.get("tags", []),
        )

        # Parse video
        raw_video = episode.get("video")
        video = None
        if raw_video:
            video = VideoInfo(
                video_url=raw_video.get("video_url", ""),
                duration_seconds=raw_video.get("duration_seconds", 0),
                resolution=raw_video.get("resolution", "1080p"),
                format=raw_video.get("format", "mp4"),
                file_size_mb=raw_video.get("file_size_mb", 0),
            )

        return HeroEpisode(
            hero_id=episode.get("hero_id", ""),
            episode_number=episode.get("episode_number", 0),
            title=episode.get("title", ""),
            synopsis=episode.get("synopsis", ""),
            script=script,
            panels=panels,
            video=video,
            tags=episode.get("tags", []),
            canon_references=episode.get("canon_references", []),
            generated_at=episode.get("generated_at"),
        )

    def _to_hero_response(self, hero: dict) -> HeroResponse:  # type: ignore[type-arg]
        """Convert Neo4j result to HeroResponse."""
        content_settings = hero.get("content_settings", {})
        if isinstance(content_settings, dict):
            settings = ContentSettings(**content_settings)
        else:
            settings = ContentSettings()

        return HeroResponse(
            id=hero["id"],
            user_id=hero["user_id"],
            hero_name=hero["hero_name"],
            power_type=PowerType(hero["power_type"]),
            status=HeroStatus(hero["status"]),
            episode_count=hero.get("episode_count", 0),
            significance_score=hero.get("significance_score", 0.0),
            power_level=hero.get("power_level", 1),
            abilities=hero.get("abilities", []),
            current_location_id=hero.get("current_location_id"),
            character_locker_url=hero.get("character_locker_url"),
            content_settings=settings,
            created_at=hero["created_at"],
            last_active_at=hero.get("last_active_at"),
        )
