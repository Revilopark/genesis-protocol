"""Social graph API routes."""

from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from neo4j import AsyncSession
from pydantic import BaseModel

from genesis.auth.dependencies import get_current_guardian, get_current_user
from genesis.core.database import get_db

router = APIRouter()


class ConnectionStatus(str, Enum):
    """Connection status enum."""

    PENDING = "pending"
    APPROVED = "approved"
    BLOCKED = "blocked"


class ConnectionRequest(BaseModel):
    """Connection request payload."""

    target_hero_id: str


class ConnectionResponse(BaseModel):
    """Connection response model."""

    id: str
    hero_id: str
    hero_name: str
    status: str
    initiated_at: str
    approved_by_guardian: bool


class FriendSummary(BaseModel):
    """Friend summary model."""

    hero_id: str
    hero_name: str
    power_type: str
    is_online: bool = False


@router.get("/friends", response_model=list[FriendSummary])
async def get_friends(
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[FriendSummary]:
    """Get approved friends list."""
    query = """
    MATCH (hero:Hero {user_id: $user_id})-[c:CONNECTED_TO {status: 'approved'}]-(friend:Hero)
    RETURN friend.id as hero_id, friend.hero_name as hero_name, friend.power_type as power_type
    """
    result = await session.run(query, user_id=current_user["id"])
    records = await result.fetch(100)
    return [
        FriendSummary(
            hero_id=r["hero_id"],
            hero_name=r["hero_name"],
            power_type=r["power_type"],
        )
        for r in records
    ]


@router.post("/connect", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def request_connection(
    request: ConnectionRequest,
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ConnectionResponse:
    """Send a friend connection request."""
    query = """
    MATCH (hero:Hero {user_id: $user_id})
    MATCH (target:Hero {id: $target_id})
    CREATE (hero)-[c:CONNECTED_TO {
        id: randomUUID(),
        status: 'pending',
        initiated_by: hero.id,
        initiated_at: datetime(),
        approved_by_guardian: false
    }]->(target)
    RETURN c.id as id, target.id as hero_id, target.hero_name as hero_name,
           c.status as status, toString(c.initiated_at) as initiated_at,
           c.approved_by_guardian as approved_by_guardian
    """
    result = await session.run(
        query,
        user_id=current_user["id"],
        target_id=request.target_hero_id,
    )
    record = await result.single()
    if not record:
        raise ValueError("Failed to create connection")
    return ConnectionResponse(**dict(record))


@router.get("/requests/pending", response_model=list[ConnectionResponse])
async def get_pending_requests(
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[ConnectionResponse]:
    """Get pending connection requests for current user."""
    query = """
    MATCH (requester:Hero)-[c:CONNECTED_TO {status: 'pending'}]->(hero:Hero {user_id: $user_id})
    RETURN c.id as id, requester.id as hero_id, requester.hero_name as hero_name,
           c.status as status, toString(c.initiated_at) as initiated_at,
           c.approved_by_guardian as approved_by_guardian
    """
    result = await session.run(query, user_id=current_user["id"])
    records = await result.fetch(100)
    return [ConnectionResponse(**dict(r)) for r in records]


@router.post("/requests/{connection_id}/approve")
async def approve_connection(
    connection_id: str,
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Approve a pending connection request."""
    query = """
    MATCH (requester:Hero)-[c:CONNECTED_TO {id: $connection_id, status: 'pending'}]->(hero:Hero {user_id: $user_id})
    SET c.status = 'approved', c.approved_at = datetime()
    RETURN c
    """
    result = await session.run(query, connection_id=connection_id, user_id=current_user["id"])
    record = await result.single()
    if not record:
        raise ValueError("Connection not found or already processed")
    return {"message": "Connection approved"}


@router.post("/requests/{connection_id}/reject")
async def reject_connection(
    connection_id: str,
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Reject a pending connection request."""
    query = """
    MATCH (requester:Hero)-[c:CONNECTED_TO {id: $connection_id, status: 'pending'}]->(hero:Hero {user_id: $user_id})
    DELETE c
    """
    await session.run(query, connection_id=connection_id, user_id=current_user["id"])
    return {"message": "Connection rejected"}


@router.get("/guardian/pending-approvals", response_model=list[ConnectionResponse])
async def get_guardian_pending_approvals(
    guardian: Annotated[dict[str, str], Depends(get_current_guardian)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[ConnectionResponse]:
    """Get pending connections requiring guardian approval."""
    query = """
    MATCH (hero:Hero)-[:SPONSORED_BY]->(sponsor:SponsorNode {id: $sponsor_id})
    MATCH (other:Hero)-[c:CONNECTED_TO {status: 'approved', approved_by_guardian: false}]-(hero)
    RETURN c.id as id, other.id as hero_id, other.hero_name as hero_name,
           c.status as status, toString(c.initiated_at) as initiated_at,
           c.approved_by_guardian as approved_by_guardian
    """
    result = await session.run(query, sponsor_id=guardian["id"])
    records = await result.fetch(100)
    return [ConnectionResponse(**dict(r)) for r in records]


@router.post("/guardian/approve/{connection_id}")
async def guardian_approve_connection(
    connection_id: str,
    guardian: Annotated[dict[str, str], Depends(get_current_guardian)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Guardian approves a connection (Digital Playdate)."""
    query = """
    MATCH (hero:Hero)-[:SPONSORED_BY]->(sponsor:SponsorNode {id: $sponsor_id})
    MATCH ()-[c:CONNECTED_TO {id: $connection_id}]-(hero)
    SET c.approved_by_guardian = true, c.guardian_approved_at = datetime()
    RETURN c
    """
    result = await session.run(query, connection_id=connection_id, sponsor_id=guardian["id"])
    record = await result.single()
    if not record:
        raise ValueError("Connection not found")
    return {"message": "Connection approved by guardian"}
