"""Content generation API routes."""

from datetime import datetime
from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from neo4j import AsyncSession
from pydantic import BaseModel

from genesis.auth.dependencies import get_current_user
from genesis.core.database import get_db

router = APIRouter()


class GenerationStatus(str, Enum):
    """Episode generation status."""

    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ModerationStatus(str, Enum):
    """Episode moderation status."""

    PENDING = "pending"
    APPROVED = "approved"
    FLAGGED = "flagged"
    REJECTED = "rejected"


class EpisodeResponse(BaseModel):
    """Episode response model."""

    id: str
    hero_id: str
    episode_number: int
    title: str
    synopsis: str
    comic_url: str | None
    video_url: str | None
    tier: str
    generation_status: GenerationStatus
    moderation_status: ModerationStatus
    generated_at: datetime | None
    published_at: datetime | None


class EpisodeRequest(BaseModel):
    """Request to generate a new episode."""

    include_crossover: bool = False
    crossover_hero_id: str | None = None


@router.get("/episodes", response_model=list[EpisodeResponse])
async def get_episodes(
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[EpisodeResponse]:
    """Get episodes for the current user's hero."""
    query = """
    MATCH (hero:Hero {user_id: $user_id})-[:STARS_IN]->(e:Episode)
    WHERE e.published_at IS NOT NULL
    RETURN e
    ORDER BY e.episode_number DESC
    SKIP $offset
    LIMIT $limit
    """
    result = await session.run(query, user_id=current_user["id"], limit=limit, offset=offset)
    records = await result.fetch(limit)
    return [
        EpisodeResponse(
            id=r["e"]["id"],
            hero_id=r["e"]["hero_id"],
            episode_number=r["e"]["episode_number"],
            title=r["e"]["title"],
            synopsis=r["e"].get("synopsis", ""),
            comic_url=r["e"].get("comic_url"),
            video_url=r["e"].get("video_url"),
            tier=r["e"].get("tier", "B"),
            generation_status=GenerationStatus(r["e"]["generation_status"]),
            moderation_status=ModerationStatus(r["e"]["moderation_status"]),
            generated_at=r["e"].get("generated_at"),
            published_at=r["e"].get("published_at"),
        )
        for r in records
    ]


@router.get("/episodes/{episode_id}", response_model=EpisodeResponse)
async def get_episode(
    episode_id: str,
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> EpisodeResponse:
    """Get a specific episode."""
    query = """
    MATCH (hero:Hero {user_id: $user_id})-[:STARS_IN]->(e:Episode {id: $episode_id})
    RETURN e
    """
    result = await session.run(query, user_id=current_user["id"], episode_id=episode_id)
    record = await result.single()
    if not record:
        raise ValueError("Episode not found")
    e = record["e"]
    return EpisodeResponse(
        id=e["id"],
        hero_id=e["hero_id"],
        episode_number=e["episode_number"],
        title=e["title"],
        synopsis=e.get("synopsis", ""),
        comic_url=e.get("comic_url"),
        video_url=e.get("video_url"),
        tier=e.get("tier", "B"),
        generation_status=GenerationStatus(e["generation_status"]),
        moderation_status=ModerationStatus(e["moderation_status"]),
        generated_at=e.get("generated_at"),
        published_at=e.get("published_at"),
    )


@router.post("/episodes/generate", response_model=EpisodeResponse, status_code=status.HTTP_202_ACCEPTED)
async def request_episode_generation(
    request: EpisodeRequest,
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> EpisodeResponse:
    """Request generation of a new episode."""
    # Get the hero and their episode count
    hero_query = """
    MATCH (hero:Hero {user_id: $user_id})
    RETURN hero
    """
    hero_result = await session.run(hero_query, user_id=current_user["id"])
    hero_record = await hero_result.single()
    if not hero_record:
        raise ValueError("Hero not found")

    hero = hero_record["hero"]
    next_episode_number = hero.get("episode_count", 0) + 1

    # Create pending episode
    create_query = """
    MATCH (hero:Hero {user_id: $user_id})
    CREATE (e:Episode {
        id: randomUUID(),
        hero_id: hero.id,
        episode_number: $episode_number,
        title: 'Episode ' + toString($episode_number),
        synopsis: '',
        comic_url: null,
        video_url: null,
        tier: 'B',
        generation_status: 'pending',
        moderation_status: 'pending',
        include_crossover: $include_crossover,
        crossover_hero_id: $crossover_hero_id,
        generated_at: null,
        published_at: null,
        created_at: datetime()
    })
    CREATE (hero)-[:STARS_IN]->(e)
    SET hero.episode_count = $episode_number
    RETURN e
    """
    result = await session.run(
        create_query,
        user_id=current_user["id"],
        episode_number=next_episode_number,
        include_crossover=request.include_crossover,
        crossover_hero_id=request.crossover_hero_id,
    )
    record = await result.single()
    if not record:
        raise ValueError("Failed to create episode")

    e = record["e"]
    return EpisodeResponse(
        id=e["id"],
        hero_id=e["hero_id"],
        episode_number=e["episode_number"],
        title=e["title"],
        synopsis=e.get("synopsis", ""),
        comic_url=e.get("comic_url"),
        video_url=e.get("video_url"),
        tier=e.get("tier", "B"),
        generation_status=GenerationStatus(e["generation_status"]),
        moderation_status=ModerationStatus(e["moderation_status"]),
        generated_at=e.get("generated_at"),
        published_at=e.get("published_at"),
    )


@router.post("/episodes/{episode_id}/rate")
async def rate_episode(
    episode_id: str,
    rating: Annotated[int, Query(ge=1, le=5)],
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Rate an episode."""
    query = """
    MATCH (hero:Hero {user_id: $user_id})-[:STARS_IN]->(e:Episode {id: $episode_id})
    SET e.user_rating = $rating
    RETURN e
    """
    result = await session.run(
        query,
        user_id=current_user["id"],
        episode_id=episode_id,
        rating=rating,
    )
    record = await result.single()
    if not record:
        raise ValueError("Episode not found")
    return {"message": "Rating saved"}
