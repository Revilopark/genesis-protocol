"""Hero API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from neo4j import AsyncSession

from genesis.auth.dependencies import get_current_guardian, get_current_user
from genesis.core.database import get_db
from genesis.heroes.schemas import (
    HeroCreate,
    HeroEpisode,
    HeroResponse,
    HeroSummary,
    HeroUpdate,
    HeroWithEpisodes,
)
from genesis.heroes.service import HeroService

router = APIRouter()


@router.post("/", response_model=HeroResponse, status_code=status.HTTP_201_CREATED)
async def create_hero(
    data: HeroCreate,
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> HeroResponse:
    """Create a new Hero for the authenticated user."""
    service = HeroService(session)
    # Note: sponsor_id would come from the user's linked guardian
    # For now, using a placeholder
    return await service.create_hero(
        user_id=current_user["id"],
        data=data,
        sponsor_id=current_user.get("sponsor_id", "default_sponsor"),
    )


@router.get("/me", response_model=HeroResponse)
async def get_my_hero(
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> HeroResponse:
    """Get the current user's Hero."""
    service = HeroService(session)
    return await service.get_hero(current_user["id"])


@router.get("/me/episodes", response_model=HeroWithEpisodes)
async def get_my_hero_with_episodes(
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> HeroWithEpisodes:
    """Get the current user's Hero with recent episodes."""
    service = HeroService(session)
    hero = await service.get_hero(current_user["id"])
    return await service.get_hero_with_episodes(hero.id, limit)


@router.get("/{hero_id}", response_model=HeroResponse)
async def get_hero(
    hero_id: str,
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> HeroResponse:
    """Get a Hero by ID."""
    service = HeroService(session)
    return await service.get_hero_by_id(hero_id)


@router.patch("/{hero_id}", response_model=HeroResponse)
async def update_hero(
    hero_id: str,
    data: HeroUpdate,
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> HeroResponse:
    """Update a Hero's properties."""
    service = HeroService(session)
    return await service.update_hero(hero_id, data, current_user["id"])


@router.patch("/{hero_id}/activate", response_model=HeroResponse)
async def activate_hero(
    hero_id: str,
    guardian: Annotated[dict[str, str], Depends(get_current_guardian)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> HeroResponse:
    """Activate a Hero (guardian-only endpoint)."""
    service = HeroService(session)
    # Guardian ID is their sponsor_id in the system
    return await service.activate_hero(hero_id, sponsor_id=guardian["id"])


@router.get("/guardian/children", response_model=list[HeroSummary])
async def get_guardian_children(
    guardian: Annotated[dict[str, str], Depends(get_current_guardian)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[HeroSummary]:
    """Get all heroes sponsored by the current guardian."""
    service = HeroService(session)
    # Guardian's ID is their sponsor_id in the system
    return await service.get_guardian_children(guardian["id"])


@router.get("/{hero_id}/episodes", response_model=list[HeroEpisode])
async def get_hero_episodes(
    hero_id: str,
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[HeroEpisode]:
    """Get all episodes for a hero."""
    service = HeroService(session)
    return await service.get_hero_episodes(hero_id, limit)


@router.get("/{hero_id}/episodes/latest", response_model=HeroEpisode)
async def get_hero_latest_episode(
    hero_id: str,
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> HeroEpisode:
    """Get the latest episode for a hero."""
    service = HeroService(session)
    return await service.get_hero_latest_episode(hero_id)


@router.get("/{hero_id}/episodes/{episode_number}", response_model=HeroEpisode)
async def get_hero_episode(
    hero_id: str,
    episode_number: int,
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> HeroEpisode:
    """Get a specific episode by number."""
    service = HeroService(session)
    return await service.get_hero_episode(hero_id, episode_number)
