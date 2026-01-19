"""Hero repository for Neo4j operations."""

from typing import Any

from neo4j import AsyncSession

from genesis.heroes.schemas import ContentSettings, HeroCreate, HeroStatus, HeroUpdate


class HeroRepository:
    """Neo4j repository for Hero operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_hero(
        self,
        user_id: str,
        data: HeroCreate,
        sponsor_id: str,
    ) -> dict[str, Any]:
        """Create a new Hero node linked to a Sponsor."""
        query = """
        MATCH (sponsor:SponsorNode {id: $sponsor_id})
        CREATE (hero:Hero {
            id: randomUUID(),
            user_id: $user_id,
            hero_name: $hero_name,
            power_type: $power_type,
            origin_story: $origin_story,
            status: $status,
            episode_count: 0,
            significance_score: 0.0,
            power_level: 1,
            abilities: [],
            current_location_id: null,
            character_locker_url: null,
            content_settings: $content_settings,
            created_at: datetime(),
            last_active_at: null
        })
        CREATE (hero)-[:SPONSORED_BY]->(sponsor)
        RETURN hero
        """
        default_settings = ContentSettings()
        result = await self.session.run(
            query,
            user_id=user_id,
            sponsor_id=sponsor_id,
            hero_name=data.hero_name,
            power_type=data.power_type.value,
            origin_story=data.origin_story,
            status=HeroStatus.PENDING.value,
            content_settings=default_settings.model_dump(),
        )
        record = await result.single()
        return dict(record["hero"]) if record else {}

    async def get_hero_by_id(self, hero_id: str) -> dict[str, Any] | None:
        """Get Hero by ID."""
        query = """
        MATCH (hero:Hero {id: $hero_id})
        RETURN hero
        """
        result = await self.session.run(query, hero_id=hero_id)
        record = await result.single()
        return dict(record["hero"]) if record else None

    async def get_hero_by_user_id(self, user_id: str) -> dict[str, Any] | None:
        """Retrieve Hero by user ID."""
        query = """
        MATCH (hero:Hero {user_id: $user_id})
        RETURN hero
        """
        result = await self.session.run(query, user_id=user_id)
        record = await result.single()
        return dict(record["hero"]) if record else None

    async def get_hero_with_episodes(
        self,
        hero_id: str,
        limit: int = 10,
    ) -> dict[str, Any] | None:
        """Retrieve Hero with recent episodes."""
        query = """
        MATCH (hero:Hero {id: $hero_id})
        OPTIONAL MATCH (hero)-[:STARS_IN]->(episode:Episode)
        WHERE episode.published_at IS NOT NULL
        WITH hero, episode
        ORDER BY episode.episode_number DESC
        LIMIT $limit
        RETURN hero, collect(episode) as episodes
        """
        result = await self.session.run(query, hero_id=hero_id, limit=limit)
        record = await result.single()
        if not record:
            return None
        return {
            "hero": dict(record["hero"]),
            "episodes": [dict(e) for e in record["episodes"]],
        }

    async def update_hero(
        self,
        hero_id: str,
        data: HeroUpdate,
    ) -> dict[str, Any] | None:
        """Update Hero properties."""
        set_clauses = []
        params: dict[str, Any] = {"hero_id": hero_id}

        if data.hero_name is not None:
            set_clauses.append("hero.hero_name = $hero_name")
            params["hero_name"] = data.hero_name

        if data.origin_story is not None:
            set_clauses.append("hero.origin_story = $origin_story")
            params["origin_story"] = data.origin_story

        if data.content_settings is not None:
            set_clauses.append("hero.content_settings = $content_settings")
            params["content_settings"] = data.content_settings.model_dump()

        if not set_clauses:
            return await self.get_hero_by_id(hero_id)

        query = f"""
        MATCH (hero:Hero {{id: $hero_id}})
        SET {', '.join(set_clauses)}
        RETURN hero
        """
        result = await self.session.run(query, **params)
        record = await result.single()
        return dict(record["hero"]) if record else None

    async def update_status(self, hero_id: str, status: HeroStatus) -> bool:
        """Update Hero status (e.g., PENDING -> ACTIVE)."""
        query = """
        MATCH (hero:Hero {id: $hero_id})
        SET hero.status = $status
        RETURN hero
        """
        result = await self.session.run(
            query,
            hero_id=hero_id,
            status=status.value,
        )
        record = await result.single()
        return record is not None

    async def get_heroes_by_sponsor(
        self,
        sponsor_id: str,
    ) -> list[dict[str, Any]]:
        """Get all heroes sponsored by a guardian."""
        query = """
        MATCH (hero:Hero)-[:SPONSORED_BY]->(sponsor:SponsorNode {id: $sponsor_id})
        RETURN hero
        ORDER BY hero.created_at DESC
        """
        result = await self.session.run(query, sponsor_id=sponsor_id)
        records = await result.fetch(100)
        return [dict(r["hero"]) for r in records]

    async def update_last_active(self, hero_id: str) -> None:
        """Update hero's last active timestamp."""
        query = """
        MATCH (hero:Hero {id: $hero_id})
        SET hero.last_active_at = datetime()
        """
        await self.session.run(query, hero_id=hero_id)
