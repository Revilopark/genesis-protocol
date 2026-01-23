"""Canon layer API routes.

The Canon Layer is the global state of the Genesis Protocol universe.
It contains world laws, events, locations, NPCs, and narrative arcs
that affect all users. Changes to the Canon propagate to all Variant
(user-specific) subgraphs.
"""

import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from neo4j import AsyncSession
from pydantic import BaseModel, Field

from genesis.auth.dependencies import get_current_admin, get_current_user
from genesis.core.database import get_db

logger = logging.getLogger(__name__)
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
    event_type: str  # global_arc, regional, social, emergent
    start_date: datetime | None = None
    end_date: datetime | None = None
    region: str | None = None  # For regional events
    significance_score: float = Field(default=50.0, ge=0, le=100)


class CreateLocation(BaseModel):
    """Create location request."""

    name: str
    location_type: str  # city, landmark, region, dimension
    description: str
    parent_location_id: str | None = None
    coordinates: dict[str, float] | None = None


class CreateNPC(BaseModel):
    """Create NPC request."""

    name: str
    npc_type: str  # hero, villain, civilian, authority, cosmic
    description: str
    power_level: int = Field(default=1, ge=1, le=100)
    abilities: list[str] = []
    affiliation: str | None = None
    is_recurring: bool = True


class CreateGlobalArc(BaseModel):
    """Create global narrative arc request."""

    title: str
    description: str
    total_phases: int = Field(default=8, ge=1, le=20)
    weekly_beats: list[str] = []  # Brief description for each phase


class UpdateArcPhase(BaseModel):
    """Update arc phase request."""

    new_phase: int
    phase_summary: str | None = None


class EmergentEventProposal(BaseModel):
    """Proposal to promote user-generated event to Canon."""

    event_description: str
    source_hero_ids: list[str]
    significance_score: float
    proposed_title: str


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
@router.post("/admin/events", response_model=CanonEvent, status_code=status.HTTP_201_CREATED)
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
        region: $region,
        significance_score: $significance_score,
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
        region=data.region,
        significance_score=data.significance_score,
        created_by=admin["id"],
    )
    record = await result.single()
    if not record:
        raise ValueError("Failed to create event")
    e = record["e"]
    logger.info(f"Canon event created: {e['title']} by admin {admin['id']}")
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


@router.patch("/admin/events/{event_id}/activate")
async def activate_event(
    event_id: str,
    admin: Annotated[dict[str, str], Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Activate a scheduled canon event."""
    query = """
    MATCH (e:CanonEvent {id: $event_id})
    WHERE e.status = 'scheduled'
    SET e.status = 'active', e.activated_at = datetime(), e.activated_by = $admin_id
    RETURN e.title as title
    """
    result = await session.run(query, event_id=event_id, admin_id=admin["id"])
    record = await result.single()
    if not record:
        raise ValueError("Event not found or already active")
    logger.info(f"Canon event activated: {record['title']}")
    return {"message": f"Event '{record['title']}' activated"}


@router.patch("/admin/events/{event_id}/complete")
async def complete_event(
    event_id: str,
    outcome: Annotated[str, Query()],
    admin: Annotated[dict[str, str], Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Complete an active canon event with an outcome."""
    query = """
    MATCH (e:CanonEvent {id: $event_id})
    WHERE e.status = 'active'
    SET e.status = 'completed',
        e.outcome = $outcome,
        e.completed_at = datetime(),
        e.completed_by = $admin_id
    RETURN e.title as title
    """
    result = await session.run(
        query, event_id=event_id, outcome=outcome, admin_id=admin["id"]
    )
    record = await result.single()
    if not record:
        raise ValueError("Event not found or not active")
    logger.info(f"Canon event completed: {record['title']} - {outcome}")
    return {"message": f"Event '{record['title']}' completed", "outcome": outcome}


# Location management
@router.post("/admin/locations", response_model=Location, status_code=status.HTTP_201_CREATED)
async def create_location(
    data: CreateLocation,
    admin: Annotated[dict[str, str], Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> Location:
    """Create a new canonical location."""
    query = """
    CREATE (l:Location {
        id: randomUUID(),
        name: $name,
        location_type: $location_type,
        description: $description,
        is_canonical: true,
        coordinates: $coordinates,
        created_by: $created_by,
        created_at: datetime()
    })
    WITH l
    OPTIONAL MATCH (parent:Location {id: $parent_id})
    FOREACH (_ IN CASE WHEN parent IS NOT NULL THEN [1] ELSE [] END |
        CREATE (l)-[:LOCATED_IN]->(parent)
    )
    RETURN l
    """
    result = await session.run(
        query,
        name=data.name,
        location_type=data.location_type,
        description=data.description,
        coordinates=data.coordinates,
        parent_id=data.parent_location_id,
        created_by=admin["id"],
    )
    record = await result.single()
    if not record:
        raise ValueError("Failed to create location")
    loc = record["l"]
    return Location(
        id=loc["id"],
        name=loc["name"],
        location_type=loc["location_type"],
        description=loc["description"],
    )


# NPC management
@router.post("/admin/npcs", response_model=NPC, status_code=status.HTTP_201_CREATED)
async def create_npc(
    data: CreateNPC,
    admin: Annotated[dict[str, str], Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> NPC:
    """Create a new canonical NPC."""
    query = """
    CREATE (n:NPC {
        id: randomUUID(),
        name: $name,
        npc_type: $npc_type,
        description: $description,
        power_level: $power_level,
        abilities: $abilities,
        affiliation: $affiliation,
        is_canonical: true,
        is_recurring: $is_recurring,
        created_by: $created_by,
        created_at: datetime()
    })
    RETURN n
    """
    result = await session.run(
        query,
        name=data.name,
        npc_type=data.npc_type,
        description=data.description,
        power_level=data.power_level,
        abilities=data.abilities,
        affiliation=data.affiliation,
        is_recurring=data.is_recurring,
        created_by=admin["id"],
    )
    record = await result.single()
    if not record:
        raise ValueError("Failed to create NPC")
    npc = record["n"]
    logger.info(f"Canon NPC created: {npc['name']}")
    return NPC(
        id=npc["id"],
        name=npc["name"],
        npc_type=npc["npc_type"],
        description=npc["description"],
        power_level=npc["power_level"],
    )


# Global Arc management
@router.post("/admin/arcs", response_model=GlobalArc, status_code=status.HTTP_201_CREATED)
async def create_global_arc(
    data: CreateGlobalArc,
    admin: Annotated[dict[str, str], Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> GlobalArc:
    """Create a new global narrative arc (seasonal storyline)."""
    query = """
    CREATE (a:GlobalArc {
        id: randomUUID(),
        title: $title,
        description: $description,
        status: 'planned',
        current_phase: 0,
        total_phases: $total_phases,
        weekly_beats: $weekly_beats,
        created_by: $created_by,
        created_at: datetime()
    })
    RETURN a
    """
    result = await session.run(
        query,
        title=data.title,
        description=data.description,
        total_phases=data.total_phases,
        weekly_beats=data.weekly_beats,
        created_by=admin["id"],
    )
    record = await result.single()
    if not record:
        raise ValueError("Failed to create arc")
    arc = record["a"]
    logger.info(f"Global arc created: {arc['title']}")
    return GlobalArc(
        id=arc["id"],
        title=arc["title"],
        description=arc["description"],
        status=arc["status"],
        current_phase=arc["current_phase"],
        total_phases=arc["total_phases"],
    )


@router.patch("/admin/arcs/{arc_id}/start")
async def start_global_arc(
    arc_id: str,
    admin: Annotated[dict[str, str], Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Start a planned global arc (makes it active)."""
    # First, check if there's already an active arc
    check_query = """
    MATCH (a:GlobalArc {status: 'active'})
    RETURN a.title as title
    """
    check_result = await session.run(check_query)
    check_record = await check_result.single()
    if check_record:
        raise ValueError(f"Arc '{check_record['title']}' is already active. Complete it first.")

    query = """
    MATCH (a:GlobalArc {id: $arc_id})
    WHERE a.status = 'planned'
    SET a.status = 'active',
        a.current_phase = 1,
        a.started_at = datetime(),
        a.started_by = $admin_id
    RETURN a.title as title
    """
    result = await session.run(query, arc_id=arc_id, admin_id=admin["id"])
    record = await result.single()
    if not record:
        raise ValueError("Arc not found or already started")
    logger.info(f"Global arc started: {record['title']}")
    return {"message": f"Arc '{record['title']}' started", "current_phase": 1}


@router.patch("/admin/arcs/{arc_id}/advance")
async def advance_arc_phase(
    arc_id: str,
    data: UpdateArcPhase,
    admin: Annotated[dict[str, str], Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Advance a global arc to the next phase."""
    query = """
    MATCH (a:GlobalArc {id: $arc_id, status: 'active'})
    WHERE $new_phase <= a.total_phases
    SET a.current_phase = $new_phase,
        a.phase_updated_at = datetime(),
        a.last_phase_summary = $phase_summary
    RETURN a.title as title, a.current_phase as phase, a.total_phases as total
    """
    result = await session.run(
        query,
        arc_id=arc_id,
        new_phase=data.new_phase,
        phase_summary=data.phase_summary,
    )
    record = await result.single()
    if not record:
        raise ValueError("Arc not found, not active, or invalid phase")
    logger.info(f"Arc '{record['title']}' advanced to phase {record['phase']}/{record['total']}")
    return {
        "message": f"Arc advanced to phase {record['phase']}",
        "title": record["title"],
        "current_phase": record["phase"],
        "total_phases": record["total"],
    }


@router.patch("/admin/arcs/{arc_id}/complete")
async def complete_global_arc(
    arc_id: str,
    outcome: Annotated[str, Query()],
    admin: Annotated[dict[str, str], Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Complete a global arc with final outcome."""
    query = """
    MATCH (a:GlobalArc {id: $arc_id, status: 'active'})
    SET a.status = 'completed',
        a.outcome = $outcome,
        a.completed_at = datetime(),
        a.completed_by = $admin_id
    RETURN a.title as title
    """
    result = await session.run(query, arc_id=arc_id, outcome=outcome, admin_id=admin["id"])
    record = await result.single()
    if not record:
        raise ValueError("Arc not found or not active")
    logger.info(f"Global arc completed: {record['title']} - {outcome}")
    return {"message": f"Arc '{record['title']}' completed", "outcome": outcome}


# Emergent behavior detection
@router.post("/admin/emergent/propose")
async def propose_emergent_event(
    proposal: EmergentEventProposal,
    admin: Annotated[dict[str, str], Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Propose a user-generated emergent event for Canon promotion.

    The Canon Auditor (AI or human) reviews patterns from user episodes
    and proposes events that should become part of the shared universe.
    """
    query = """
    CREATE (p:EmergentProposal {
        id: randomUUID(),
        title: $title,
        description: $description,
        source_hero_ids: $hero_ids,
        significance_score: $significance_score,
        status: 'pending_review',
        proposed_by: $proposed_by,
        created_at: datetime()
    })
    RETURN p.id as id
    """
    result = await session.run(
        query,
        title=proposal.proposed_title,
        description=proposal.event_description,
        hero_ids=proposal.source_hero_ids,
        significance_score=proposal.significance_score,
        proposed_by=admin["id"],
    )
    record = await result.single()
    if not record:
        raise ValueError("Failed to create proposal")

    logger.info(f"Emergent event proposed: {proposal.proposed_title}")
    return {
        "message": "Emergent event proposal created",
        "proposal_id": record["id"],
    }


@router.post("/admin/emergent/{proposal_id}/approve")
async def approve_emergent_event(
    proposal_id: str,
    admin: Annotated[dict[str, str], Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CanonEvent:
    """Approve an emergent event proposal and promote it to Canon."""
    # Get proposal and create canon event
    query = """
    MATCH (p:EmergentProposal {id: $proposal_id, status: 'pending_review'})
    SET p.status = 'approved', p.approved_by = $admin_id, p.approved_at = datetime()
    WITH p
    CREATE (e:CanonEvent {
        id: randomUUID(),
        title: p.title,
        description: p.description,
        event_type: 'emergent',
        status: 'active',
        significance_score: p.significance_score,
        source_proposal_id: p.id,
        source_hero_ids: p.source_hero_ids,
        created_by: $admin_id,
        created_at: datetime()
    })
    CREATE (p)-[:PROMOTED_TO]->(e)
    RETURN e
    """
    result = await session.run(query, proposal_id=proposal_id, admin_id=admin["id"])
    record = await result.single()
    if not record:
        raise ValueError("Proposal not found or already processed")

    e = record["e"]
    logger.info(f"Emergent event approved and promoted to Canon: {e['title']}")

    return CanonEvent(
        id=e["id"],
        title=e["title"],
        description=e["description"],
        event_type=e["event_type"],
        status=e["status"],
        start_date=None,
        end_date=None,
        significance_score=e["significance_score"],
    )


@router.get("/admin/emergent/pending")
async def get_pending_proposals(
    admin: Annotated[dict[str, str], Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
) -> list[dict[str, object]]:
    """Get pending emergent event proposals for review."""
    query = """
    MATCH (p:EmergentProposal {status: 'pending_review'})
    RETURN p {.id, .title, .description, .significance_score, .source_hero_ids, .created_at}
    ORDER BY p.significance_score DESC
    LIMIT $limit
    """
    result = await session.run(query, limit=limit)
    records = await result.fetch(limit)
    return [dict(r["p"]) for r in records]
