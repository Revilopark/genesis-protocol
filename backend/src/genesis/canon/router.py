"""Canon layer API routes."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from neo4j import AsyncSession
from pydantic import BaseModel

from genesis.auth.dependencies import get_current_admin, get_current_user
from genesis.core.database import get_db

router = APIRouter()


class CanonEvent(BaseModel):
    """Canon event model."""

    id: str
    title: str
    description: str
    event_type: str
    status: str
    start_date: datetime | None
    end_date: datetime | None
    significance_score: float


class Location(BaseModel):
    """Location model."""

    id: str
    name: str
    location_type: str
    description: str


class NPC(BaseModel):
    """NPC model."""

    id: str
    name: str
    npc_type: str
    description: str
    power_level: int


class GlobalArc(BaseModel):
    """Global narrative arc model."""

    id: str
    title: str
    description: str
    status: str
    current_phase: int
    total_phases: int


class CreateCanonEvent(BaseModel):
    """Create canon event request."""

    title: str
    description: str
    event_type: str
    start_date: datetime | None = None
    end_date: datetime | None = None


@router.get("/events", response_model=list[CanonEvent])
async def get_active_events(
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[CanonEvent]:
    """Get active canon events."""
    query = """
    MATCH (e:CanonEvent)
    WHERE e.status IN ['active', 'scheduled']
    RETURN e
    ORDER BY e.significance_score DESC, e.start_date ASC
    LIMIT $limit
    """
    result = await session.run(query, limit=limit)
    records = await result.fetch(limit)
    return [
        CanonEvent(
            id=r["e"]["id"],
            title=r["e"]["title"],
            description=r["e"]["description"],
            event_type=r["e"]["event_type"],
            status=r["e"]["status"],
            start_date=r["e"].get("start_date"),
            end_date=r["e"].get("end_date"),
            significance_score=r["e"].get("significance_score", 0.0),
        )
        for r in records
    ]


@router.get("/events/{event_id}", response_model=CanonEvent)
async def get_event(
    event_id: str,
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CanonEvent:
    """Get a specific canon event."""
    query = """
    MATCH (e:CanonEvent {id: $event_id})
    RETURN e
    """
    result = await session.run(query, event_id=event_id)
    record = await result.single()
    if not record:
        raise ValueError("Event not found")
    e = record["e"]
    return CanonEvent(
        id=e["id"],
        title=e["title"],
        description=e["description"],
        event_type=e["event_type"],
        status=e["status"],
        start_date=e.get("start_date"),
        end_date=e.get("end_date"),
        significance_score=e.get("significance_score", 0.0),
    )


@router.get("/locations", response_model=list[Location])
async def get_locations(
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    location_type: Annotated[str | None, Query()] = None,
) -> list[Location]:
    """Get locations in the canon."""
    if location_type:
        query = """
        MATCH (l:Location {location_type: $location_type, is_canonical: true})
        RETURN l
        ORDER BY l.name
        """
        result = await session.run(query, location_type=location_type)
    else:
        query = """
        MATCH (l:Location {is_canonical: true})
        RETURN l
        ORDER BY l.name
        """
        result = await session.run(query)

    records = await result.fetch(100)
    return [
        Location(
            id=r["l"]["id"],
            name=r["l"]["name"],
            location_type=r["l"]["location_type"],
            description=r["l"]["description"],
        )
        for r in records
    ]


@router.get("/npcs", response_model=list[NPC])
async def get_npcs(
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    npc_type: Annotated[str | None, Query()] = None,
) -> list[NPC]:
    """Get NPCs in the canon."""
    if npc_type:
        query = """
        MATCH (n:NPC {npc_type: $npc_type, is_canonical: true})
        RETURN n
        ORDER BY n.power_level DESC, n.name
        """
        result = await session.run(query, npc_type=npc_type)
    else:
        query = """
        MATCH (n:NPC {is_canonical: true})
        RETURN n
        ORDER BY n.power_level DESC, n.name
        """
        result = await session.run(query)

    records = await result.fetch(100)
    return [
        NPC(
            id=r["n"]["id"],
            name=r["n"]["name"],
            npc_type=r["n"]["npc_type"],
            description=r["n"]["description"],
            power_level=r["n"].get("power_level", 1),
        )
        for r in records
    ]


@router.get("/arcs/active", response_model=GlobalArc | None)
async def get_active_arc(
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> GlobalArc | None:
    """Get the currently active global arc."""
    query = """
    MATCH (a:GlobalArc {status: 'active'})
    RETURN a
    LIMIT 1
    """
    result = await session.run(query)
    record = await result.single()
    if not record:
        return None
    a = record["a"]
    return GlobalArc(
        id=a["id"],
        title=a["title"],
        description=a["description"],
        status=a["status"],
        current_phase=a.get("current_phase", 1),
        total_phases=a.get("total_phases", 1),
    )


# Admin endpoints for managing canon
@router.post("/admin/events", response_model=CanonEvent)
async def create_canon_event(
    data: CreateCanonEvent,
    admin: Annotated[dict[str, str], Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CanonEvent:
    """Create a new canon event (admin only)."""
    query = """
    CREATE (e:CanonEvent {
        id: randomUUID(),
        title: $title,
        description: $description,
        event_type: $event_type,
        status: 'scheduled',
        start_date: $start_date,
        end_date: $end_date,
        significance_score: 0.0,
        created_by: $created_by,
        created_at: datetime()
    })
    RETURN e
    """
    result = await session.run(
        query,
        title=data.title,
        description=data.description,
        event_type=data.event_type,
        start_date=data.start_date,
        end_date=data.end_date,
        created_by=admin["id"],
    )
    record = await result.single()
    if not record:
        raise ValueError("Failed to create event")
    e = record["e"]
    return CanonEvent(
        id=e["id"],
        title=e["title"],
        description=e["description"],
        event_type=e["event_type"],
        status=e["status"],
        start_date=e.get("start_date"),
        end_date=e.get("end_date"),
        significance_score=e.get("significance_score", 0.0),
    )
