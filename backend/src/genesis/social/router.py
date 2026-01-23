"""Social graph API routes."""

import logging
from datetime import datetime
from enum import Enum
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from neo4j import AsyncSession
from pydantic import BaseModel

from genesis.auth.dependencies import get_current_guardian, get_current_user
from genesis.core.database import get_db

logger = logging.getLogger(__name__)
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


class CrossoverStatus(str, Enum):
    """Crossover request status."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    COMPLETED = "completed"
    EXPIRED = "expired"


class CrossoverRequest(BaseModel):
    """Request for a crossover episode with a friend."""

    target_hero_id: str
    message: str | None = None


class CrossoverResponse(BaseModel):
    """Crossover request/invitation response."""

    id: str
    requester_hero_id: str
    requester_hero_name: str
    target_hero_id: str
    target_hero_name: str
    status: CrossoverStatus
    message: str | None
    created_at: datetime
    episode_id: str | None = None


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


# Crossover Episode Mechanics
@router.post("/crossover/request", response_model=CrossoverResponse, status_code=status.HTTP_201_CREATED)
async def request_crossover(
    request: CrossoverRequest,
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CrossoverResponse:
    """Request a crossover episode with a friend.

    Crossover episodes feature both heroes teaming up in a shared adventure.
    The target hero must accept the request before the episode is generated.
    """
    # Verify they are friends
    friend_check = """
    MATCH (requester:Hero {user_id: $user_id})-[c:CONNECTED_TO {status: 'approved'}]-(target:Hero {id: $target_id})
    RETURN requester.id as requester_id, requester.hero_name as requester_name,
           target.hero_name as target_name
    """
    check_result = await session.run(
        friend_check, user_id=current_user["id"], target_id=request.target_hero_id
    )
    check_record = await check_result.single()
    if not check_record:
        raise ValueError("You can only request crossovers with approved friends")

    # Check for existing pending crossover request
    existing_check = """
    MATCH (requester:Hero {id: $requester_id})-[cr:CROSSOVER_REQUEST {status: 'pending'}]->(target:Hero {id: $target_id})
    RETURN cr
    """
    existing_result = await session.run(
        existing_check,
        requester_id=check_record["requester_id"],
        target_id=request.target_hero_id,
    )
    if await existing_result.single():
        raise ValueError("You already have a pending crossover request with this hero")

    # Create crossover request
    query = """
    MATCH (requester:Hero {user_id: $user_id})
    MATCH (target:Hero {id: $target_id})
    CREATE (requester)-[cr:CROSSOVER_REQUEST {
        id: randomUUID(),
        status: 'pending',
        message: $message,
        created_at: datetime(),
        expires_at: datetime() + duration('P7D')
    }]->(target)
    RETURN cr.id as id, requester.id as requester_hero_id, requester.hero_name as requester_hero_name,
           target.id as target_hero_id, target.hero_name as target_hero_name,
           cr.status as status, cr.message as message, cr.created_at as created_at
    """
    result = await session.run(
        query,
        user_id=current_user["id"],
        target_id=request.target_hero_id,
        message=request.message,
    )
    record = await result.single()
    if not record:
        raise ValueError("Failed to create crossover request")

    logger.info(f"Crossover request created: {record['requester_hero_name']} -> {record['target_hero_name']}")

    # Send real-time notification if target is online
    try:
        from genesis.presence.router import send_crossover_invite

        await send_crossover_invite(
            target_hero_id=record["target_hero_id"],
            from_hero_id=record["requester_hero_id"],
            from_hero_name=record["requester_hero_name"],
        )
    except Exception as e:
        logger.warning(f"Failed to send crossover notification: {e}")

    return CrossoverResponse(
        id=record["id"],
        requester_hero_id=record["requester_hero_id"],
        requester_hero_name=record["requester_hero_name"],
        target_hero_id=record["target_hero_id"],
        target_hero_name=record["target_hero_name"],
        status=CrossoverStatus(record["status"]),
        message=record["message"],
        created_at=record["created_at"],
    )


@router.get("/crossover/pending", response_model=list[CrossoverResponse])
async def get_pending_crossovers(
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[CrossoverResponse]:
    """Get pending crossover requests (both sent and received)."""
    query = """
    MATCH (hero:Hero {user_id: $user_id})
    OPTIONAL MATCH (hero)-[sent:CROSSOVER_REQUEST {status: 'pending'}]->(target:Hero)
    OPTIONAL MATCH (requester:Hero)-[received:CROSSOVER_REQUEST {status: 'pending'}]->(hero)
    WITH hero,
         collect(DISTINCT {
             id: sent.id, requester_id: hero.id, requester_name: hero.hero_name,
             target_id: target.id, target_name: target.hero_name,
             status: sent.status, message: sent.message, created_at: sent.created_at,
             direction: 'sent'
         }) as sent_requests,
         collect(DISTINCT {
             id: received.id, requester_id: requester.id, requester_name: requester.hero_name,
             target_id: hero.id, target_name: hero.hero_name,
             status: received.status, message: received.message, created_at: received.created_at,
             direction: 'received'
         }) as received_requests
    RETURN sent_requests + received_requests as all_requests
    """
    result = await session.run(query, user_id=current_user["id"])
    record = await result.single()
    if not record:
        return []

    requests = [
        CrossoverResponse(
            id=r["id"],
            requester_hero_id=r["requester_id"],
            requester_hero_name=r["requester_name"],
            target_hero_id=r["target_id"],
            target_hero_name=r["target_name"],
            status=CrossoverStatus(r["status"]) if r["status"] else CrossoverStatus.PENDING,
            message=r["message"],
            created_at=r["created_at"],
        )
        for r in record["all_requests"]
        if r["id"]  # Filter out null entries
    ]
    return requests


@router.post("/crossover/{crossover_id}/accept")
async def accept_crossover(
    crossover_id: str,
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    """Accept a crossover request and trigger episode generation.

    When accepted, a crossover episode is generated for both heroes.
    """
    # Verify current user is the target of this request
    query = """
    MATCH (requester:Hero)-[cr:CROSSOVER_REQUEST {id: $crossover_id, status: 'pending'}]->(target:Hero {user_id: $user_id})
    SET cr.status = 'accepted', cr.accepted_at = datetime()
    RETURN cr.id as id, requester.id as requester_id, requester.hero_name as requester_name,
           target.id as target_id, target.hero_name as target_name,
           requester {.power_type, .origin_story, .current_location} as requester_data,
           target {.power_type, .origin_story, .current_location} as target_data
    """
    result = await session.run(query, crossover_id=crossover_id, user_id=current_user["id"])
    record = await result.single()
    if not record:
        raise ValueError("Crossover request not found or already processed")

    logger.info(
        f"Crossover accepted: {record['requester_name']} + {record['target_name']}"
    )

    # Trigger crossover episode generation in background for BOTH heroes
    async def generate_crossover_episodes():
        try:
            from genesis.core.database import get_session
            from genesis.rooms.writers_room import WritersRoomAgent
            from genesis.rooms.art_department import ArtDepartmentAgent
            from genesis.rooms.studio import StudioAgent
            import asyncio

            writers_room = WritersRoomAgent()
            art_department = ArtDepartmentAgent()
            studio = StudioAgent()

            requester_id = record["requester_id"]
            requester_name = record["requester_name"]
            target_id = record["target_id"]
            target_name = record["target_name"]

            # Build crossover hero data for each perspective
            requester_as_crossover = {
                "hero_name": requester_name,
                "power_type": record["requester_data"].get("power_type", "Unknown"),
            }
            target_as_crossover = {
                "hero_name": target_name,
                "power_type": record["target_data"].get("power_type", "Unknown"),
            }

            # Generate shared crossover script once (same story for both)
            async with get_session() as db_session:
                # Get requester's episode count
                req_result = await db_session.run(
                    "MATCH (h:Hero {id: $id}) RETURN h.episode_count as count",
                    id=requester_id,
                )
                req_record = await req_result.single()
                requester_episode_num = (req_record["count"] or 0) + 1 if req_record else 1

                # Get target's episode count
                tgt_result = await db_session.run(
                    "MATCH (h:Hero {id: $id}) RETURN h.episode_count as count",
                    id=target_id,
                )
                tgt_record = await tgt_result.single()
                target_episode_num = (tgt_record["count"] or 0) + 1 if tgt_record else 1

            # Generate crossover script from requester's perspective
            writers_input = {
                "hero_id": requester_id,
                "hero_name": requester_name,
                "power_type": record["requester_data"].get("power_type", "Unknown"),
                "origin_story": record["requester_data"].get("origin_story", ""),
                "current_location": record["requester_data"].get("current_location", "Metropolis Prime"),
                "episode_number": requester_episode_num,
                "previous_episodes_summary": "",
                "active_canon_events": [],
                "content_settings": {"violence_level": 1, "language_filter": True},
                "include_crossover": True,
                "crossover_hero": target_as_crossover,
            }
            script_result = await writers_room.process(writers_input)
            shared_script = script_result.get("script", {})

            # Generate panels once (shared between both episodes)
            art_input = {
                "hero_id": requester_id,
                "hero_name": requester_name,
                "episode_number": requester_episode_num,
                "character_sheet": None,
                "panels": shared_script.get("panels", []),
                "style_preset": "comic_book",
                "content_settings": {"violence_level": 1, "language_filter": True},
            }
            art_result = await art_department.process(art_input)
            generated_panels = art_result.get("generated_panels", [])

            # Save episode for BOTH heroes
            async with get_session() as db_session:
                # Save requester's episode
                await db_session.run(
                    """
                    MATCH (h:Hero {id: $hero_id})
                    CREATE (e:Episode {
                        id: randomUUID(),
                        hero_id: $hero_id,
                        episode_number: $episode_number,
                        title: $title,
                        synopsis: $synopsis,
                        tags: $tags,
                        is_crossover: true,
                        crossover_partner_id: $partner_id,
                        crossover_partner_name: $partner_name,
                        generation_status: 'completed',
                        moderation_status: 'pending',
                        generated_at: datetime(),
                        published_at: datetime()
                    })
                    CREATE (h)-[:STARS_IN]->(e)
                    SET h.episode_count = $episode_number
                    RETURN e.id as episode_id
                    """,
                    hero_id=requester_id,
                    episode_number=requester_episode_num,
                    title=f"Team-Up: {requester_name} & {target_name}",
                    synopsis=shared_script.get("synopsis", f"{requester_name} teams up with {target_name}!"),
                    tags=shared_script.get("tags", ["crossover", "team-up"]),
                    partner_id=target_id,
                    partner_name=target_name,
                )

                # Save target's episode (same content, different hero ownership)
                await db_session.run(
                    """
                    MATCH (h:Hero {id: $hero_id})
                    CREATE (e:Episode {
                        id: randomUUID(),
                        hero_id: $hero_id,
                        episode_number: $episode_number,
                        title: $title,
                        synopsis: $synopsis,
                        tags: $tags,
                        is_crossover: true,
                        crossover_partner_id: $partner_id,
                        crossover_partner_name: $partner_name,
                        generation_status: 'completed',
                        moderation_status: 'pending',
                        generated_at: datetime(),
                        published_at: datetime()
                    })
                    CREATE (h)-[:STARS_IN]->(e)
                    SET h.episode_count = $episode_number
                    RETURN e.id as episode_id
                    """,
                    hero_id=target_id,
                    episode_number=target_episode_num,
                    title=f"Team-Up: {target_name} & {requester_name}",
                    synopsis=shared_script.get("synopsis", f"{target_name} teams up with {requester_name}!"),
                    tags=shared_script.get("tags", ["crossover", "team-up"]),
                    partner_id=requester_id,
                    partner_name=requester_name,
                )

                # Update crossover status to completed
                await db_session.run(
                    """
                    MATCH ()-[cr:CROSSOVER_REQUEST {id: $crossover_id}]->()
                    SET cr.status = 'completed', cr.completed_at = datetime()
                    """,
                    crossover_id=crossover_id,
                )

                # Create TEAM_UP relationship for tracking
                await db_session.run(
                    """
                    MATCH (h1:Hero {id: $hero1_id}), (h2:Hero {id: $hero2_id})
                    MERGE (h1)-[t:TEAM_UP {crossover_id: $crossover_id}]-(h2)
                    ON CREATE SET t.created_at = datetime()
                    """,
                    hero1_id=requester_id,
                    hero2_id=target_id,
                    crossover_id=crossover_id,
                )

            logger.info(f"Crossover episodes generated for BOTH {requester_name} and {target_name}")

            # Send notifications to both heroes
            try:
                from genesis.presence.router import send_episode_notification

                await send_episode_notification(
                    requester_id,
                    "crossover",
                    f"Team-Up with {target_name}!",
                )
                await send_episode_notification(
                    target_id,
                    "crossover",
                    f"Team-Up with {requester_name}!",
                )
            except Exception as e:
                logger.warning(f"Failed to send crossover notifications: {e}")

        except Exception as e:
            logger.error(f"Failed to generate crossover episodes: {e}")

    background_tasks.add_task(generate_crossover_episodes)

    return {
        "message": "Crossover accepted! Episode generation started.",
        "crossover_id": crossover_id,
    }


@router.post("/crossover/{crossover_id}/decline")
async def decline_crossover(
    crossover_id: str,
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Decline a crossover request."""
    query = """
    MATCH (requester:Hero)-[cr:CROSSOVER_REQUEST {id: $crossover_id, status: 'pending'}]->(target:Hero {user_id: $user_id})
    SET cr.status = 'declined', cr.declined_at = datetime()
    RETURN cr.id as id
    """
    result = await session.run(query, crossover_id=crossover_id, user_id=current_user["id"])
    record = await result.single()
    if not record:
        raise ValueError("Crossover request not found or already processed")

    return {"message": "Crossover request declined"}


@router.delete("/crossover/{crossover_id}")
async def cancel_crossover(
    crossover_id: str,
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Cancel a pending crossover request (requester only)."""
    query = """
    MATCH (requester:Hero {user_id: $user_id})-[cr:CROSSOVER_REQUEST {id: $crossover_id, status: 'pending'}]->(target:Hero)
    DELETE cr
    RETURN true as deleted
    """
    result = await session.run(query, crossover_id=crossover_id, user_id=current_user["id"])
    record = await result.single()
    if not record:
        raise ValueError("Crossover request not found or you're not the requester")

    return {"message": "Crossover request cancelled"}


@router.get("/crossover/history", response_model=list[CrossoverResponse])
async def get_crossover_history(
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[CrossoverResponse]:
    """Get history of crossover episodes."""
    query = """
    MATCH (hero:Hero {user_id: $user_id})
    MATCH (hero)-[cr:CROSSOVER_REQUEST]-(other:Hero)
    WHERE cr.status = 'completed'
    RETURN cr.id as id,
           CASE WHEN startNode(cr) = hero THEN hero.id ELSE other.id END as requester_hero_id,
           CASE WHEN startNode(cr) = hero THEN hero.hero_name ELSE other.hero_name END as requester_hero_name,
           CASE WHEN endNode(cr) = hero THEN hero.id ELSE other.id END as target_hero_id,
           CASE WHEN endNode(cr) = hero THEN hero.hero_name ELSE other.hero_name END as target_hero_name,
           cr.status as status, cr.message as message, cr.created_at as created_at,
           cr.episode_id as episode_id
    ORDER BY cr.completed_at DESC
    LIMIT $limit
    """
    result = await session.run(query, user_id=current_user["id"], limit=limit)
    records = await result.fetch(limit)
    return [
        CrossoverResponse(
            id=r["id"],
            requester_hero_id=r["requester_hero_id"],
            requester_hero_name=r["requester_hero_name"],
            target_hero_id=r["target_hero_id"],
            target_hero_name=r["target_hero_name"],
            status=CrossoverStatus(r["status"]),
            message=r["message"],
            created_at=r["created_at"],
            episode_id=r["episode_id"],
        )
        for r in records
    ]
