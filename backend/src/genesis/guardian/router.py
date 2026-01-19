"""Guardian dashboard API routes."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, status
from neo4j import AsyncSession
from pydantic import BaseModel, EmailStr

from genesis.auth.dependencies import get_current_guardian
from genesis.core.database import get_db

router = APIRouter()


class GuardianProfile(BaseModel):
    """Guardian profile model."""

    id: str
    email_hash: str
    status: str
    verification_date: datetime | None
    coppa_consent_date: datetime | None
    max_children: int


class ChildSummary(BaseModel):
    """Child (Hero) summary for guardian."""

    id: str
    hero_name: str
    status: str
    episode_count: int
    last_active_at: datetime | None
    pending_connections: int


class ConsentRequest(BaseModel):
    """COPPA consent request."""

    coppa_acknowledged: bool
    terms_accepted: bool


class LinkChildRequest(BaseModel):
    """Request to link a child's Clever account."""

    clever_authorization_code: str


class ContentSettingsUpdate(BaseModel):
    """Update content settings for a child."""

    violence_level: int | None = None
    language_filter: bool | None = None


@router.get("/profile", response_model=GuardianProfile)
async def get_guardian_profile(
    guardian: Annotated[dict[str, str], Depends(get_current_guardian)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> GuardianProfile:
    """Get guardian's profile."""
    query = """
    MATCH (s:SponsorNode {id: $sponsor_id})
    RETURN s
    """
    result = await session.run(query, sponsor_id=guardian["id"])
    record = await result.single()
    if not record:
        raise ValueError("Guardian profile not found")
    s = record["s"]
    return GuardianProfile(
        id=s["id"],
        email_hash=s.get("email_hash", ""),
        status=s["status"],
        verification_date=s.get("verification_date"),
        coppa_consent_date=s.get("coppa_consent_date"),
        max_children=s.get("max_children", 5),
    )


@router.get("/children", response_model=list[ChildSummary])
async def get_children(
    guardian: Annotated[dict[str, str], Depends(get_current_guardian)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[ChildSummary]:
    """Get all children linked to guardian."""
    query = """
    MATCH (hero:Hero)-[:SPONSORED_BY]->(s:SponsorNode {id: $sponsor_id})
    OPTIONAL MATCH (hero)-[c:CONNECTED_TO {approved_by_guardian: false}]-()
    WITH hero, count(c) as pending_count
    RETURN hero.id as id, hero.hero_name as hero_name, hero.status as status,
           hero.episode_count as episode_count, hero.last_active_at as last_active_at,
           pending_count
    ORDER BY hero.created_at DESC
    """
    result = await session.run(query, sponsor_id=guardian["id"])
    records = await result.fetch(20)
    return [
        ChildSummary(
            id=r["id"],
            hero_name=r["hero_name"],
            status=r["status"],
            episode_count=r["episode_count"] or 0,
            last_active_at=r["last_active_at"],
            pending_connections=r["pending_count"],
        )
        for r in records
    ]


@router.get("/children/{child_id}/episodes")
async def get_child_episodes(
    child_id: str,
    guardian: Annotated[dict[str, str], Depends(get_current_guardian)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[dict[str, str]]:
    """Get a child's recent episodes (read-only view for guardian)."""
    query = """
    MATCH (hero:Hero {id: $child_id})-[:SPONSORED_BY]->(s:SponsorNode {id: $sponsor_id})
    MATCH (hero)-[:STARS_IN]->(e:Episode)
    WHERE e.published_at IS NOT NULL
    RETURN e.id as id, e.title as title, e.episode_number as episode_number,
           e.comic_url as comic_url, toString(e.published_at) as published_at
    ORDER BY e.episode_number DESC
    LIMIT 20
    """
    result = await session.run(query, child_id=child_id, sponsor_id=guardian["id"])
    records = await result.fetch(20)
    return [dict(r) for r in records]


@router.patch("/children/{child_id}/settings")
async def update_child_settings(
    child_id: str,
    settings: ContentSettingsUpdate,
    guardian: Annotated[dict[str, str], Depends(get_current_guardian)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Update content settings for a child."""
    # Build dynamic SET clause
    set_parts = []
    params = {"child_id": child_id, "sponsor_id": guardian["id"]}

    if settings.violence_level is not None:
        set_parts.append("hero.content_settings.violence_level = $violence_level")
        params["violence_level"] = settings.violence_level

    if settings.language_filter is not None:
        set_parts.append("hero.content_settings.language_filter = $language_filter")
        params["language_filter"] = settings.language_filter

    if not set_parts:
        return {"message": "No settings to update"}

    query = f"""
    MATCH (hero:Hero {{id: $child_id}})-[:SPONSORED_BY]->(s:SponsorNode {{id: $sponsor_id}})
    SET {', '.join(set_parts)}
    RETURN hero
    """
    result = await session.run(query, **params)
    record = await result.single()
    if not record:
        raise ValueError("Child not found or not authorized")
    return {"message": "Settings updated"}


@router.post("/consent", status_code=status.HTTP_200_OK)
async def submit_coppa_consent(
    consent: ConsentRequest,
    guardian: Annotated[dict[str, str], Depends(get_current_guardian)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Submit COPPA consent acknowledgment."""
    if not consent.coppa_acknowledged or not consent.terms_accepted:
        raise ValueError("Must acknowledge COPPA and accept terms")

    query = """
    MATCH (s:SponsorNode {id: $sponsor_id})
    SET s.coppa_consent_date = datetime(),
        s.status = 'verified'
    RETURN s
    """
    result = await session.run(query, sponsor_id=guardian["id"])
    record = await result.single()
    if not record:
        raise ValueError("Guardian not found")
    return {"message": "COPPA consent recorded"}


@router.post("/link-child", status_code=status.HTTP_201_CREATED)
async def link_child_account(
    request: LinkChildRequest,
    guardian: Annotated[dict[str, str], Depends(get_current_guardian)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Link a child's Clever account to guardian."""
    # This would integrate with Clever OAuth
    # For now, placeholder logic
    return {"message": "Child account linked", "child_id": "placeholder"}


@router.get("/export-data")
async def export_child_data(
    child_id: str,
    guardian: Annotated[dict[str, str], Depends(get_current_guardian)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, object]:
    """Export child's data (COPPA compliance)."""
    # Verify guardian owns this child
    verify_query = """
    MATCH (hero:Hero {id: $child_id})-[:SPONSORED_BY]->(s:SponsorNode {id: $sponsor_id})
    RETURN hero
    """
    verify_result = await session.run(verify_query, child_id=child_id, sponsor_id=guardian["id"])
    if not await verify_result.single():
        raise ValueError("Child not found or not authorized")

    # Gather all child data
    data_query = """
    MATCH (hero:Hero {id: $child_id})
    OPTIONAL MATCH (hero)-[:STARS_IN]->(e:Episode)
    OPTIONAL MATCH (hero)-[c:CONNECTED_TO]-(friend:Hero)
    RETURN hero,
           collect(DISTINCT e) as episodes,
           collect(DISTINCT {friend: friend.hero_name, status: c.status}) as connections
    """
    result = await session.run(data_query, child_id=child_id)
    record = await result.single()

    if not record:
        return {"error": "No data found"}

    return {
        "hero": dict(record["hero"]),
        "episodes": [dict(e) for e in record["episodes"]],
        "connections": record["connections"],
        "exported_at": datetime.utcnow().isoformat(),
    }
