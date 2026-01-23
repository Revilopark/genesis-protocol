"""Hero service for business logic."""

from neo4j import AsyncSession

from genesis.core.exceptions import NotFoundError, ValidationError
from genesis.heroes.repository import HeroRepository
from genesis.heroes.schemas import (
    ContentSettings,
    EpisodeSummary,
    HeroCreate,
    HeroResponse,
    HeroStatus,
    HeroSummary,
    HeroUpdate,
    HeroWithEpisodes,
    PowerType,
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
