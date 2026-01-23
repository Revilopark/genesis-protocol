"""WebSocket router for real-time presence and notifications."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from neo4j import AsyncSession

from genesis.core.database import get_db
from genesis.core.security import decode_access_token
from genesis.presence.manager import presence_manager

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_hero_from_token(token: str, session: AsyncSession) -> dict[str, str] | None:
    """Validate JWT token and get hero information.

    Args:
        token: JWT access token
        session: Database session

    Returns:
        Hero information dict or None if invalid
    """
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            return None

        # Get hero for this user
        result = await session.run(
            """
            MATCH (h:Hero {user_id: $user_id})
            RETURN h.id as hero_id, h.hero_name as hero_name
            """,
            user_id=user_id,
        )
        record = await result.single()
        if not record:
            return None

        return {
            "user_id": user_id,
            "hero_id": record["hero_id"],
            "hero_name": record["hero_name"],
        }
    except Exception as e:
        logger.warning(f"Token validation failed: {e}")
        return None


async def get_friend_ids(hero_id: str, session: AsyncSession) -> list[str]:
    """Get list of friend hero IDs for a hero.

    Args:
        hero_id: The hero's ID
        session: Database session

    Returns:
        List of friend hero IDs
    """
    result = await session.run(
        """
        MATCH (h:Hero {id: $hero_id})-[c:CONNECTED_TO {status: 'approved'}]-(friend:Hero)
        RETURN friend.id as friend_id
        """,
        hero_id=hero_id,
    )
    records = await result.fetch(100)
    return [r["friend_id"] for r in records]


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Annotated[str, Query()],
) -> None:
    """WebSocket endpoint for real-time presence and notifications.

    Connect with: ws://host/api/v1/presence/ws?token=<jwt_token>

    Message Types (Client -> Server):
    - ping: Heartbeat (responds with pong)
    - get_friends_status: Request friend online statuses
    - activity: Report activity (e.g., {"type": "activity", "activity": "reading_episode"})
    - subscribe_friends: Update friend subscriptions

    Message Types (Server -> Client):
    - pong: Heartbeat response
    - friends_status: Friend status list
    - friend_online: A friend came online
    - friend_offline: A friend went offline
    - friend_activity: A friend did something notable
    - notification: System notification
    - episode_ready: New episode is ready
    - crossover_invite: Friend wants to team up
    """
    # Get database session for auth
    from genesis.core.database import get_session

    async with get_session() as session:
        # Validate token and get hero info
        hero_info = await get_hero_from_token(token, session)
        if not hero_info:
            await websocket.close(code=4001, reason="Invalid or expired token")
            return

        hero_id = hero_info["hero_id"]

        # Get friend list for subscriptions
        friend_ids = await get_friend_ids(hero_id, session)

    # Connect to presence manager
    await presence_manager.connect(websocket, hero_id, friend_ids)

    try:
        # Send initial friend statuses
        statuses = await presence_manager.get_friend_statuses(hero_id)
        await websocket.send_json({
            "type": "connected",
            "hero_id": hero_id,
            "friends_online": [s for s in statuses if s["is_online"]],
        })

        # Message loop
        while True:
            try:
                data = await websocket.receive_json()
                response = await presence_manager.handle_incoming_message(hero_id, data)
                if response:
                    await websocket.send_json(response)
            except ValueError:
                # Invalid JSON, send error
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON message",
                })

    except WebSocketDisconnect:
        logger.info(f"Hero {hero_id} WebSocket disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error for hero {hero_id}: {e}")
    finally:
        await presence_manager.disconnect(hero_id)


@router.get("/online-count")
async def get_online_count() -> dict[str, int]:
    """Get the current number of online users."""
    return {"online_count": presence_manager.get_online_count()}


@router.get("/status/{hero_id}")
async def get_hero_status(hero_id: str) -> dict[str, bool]:
    """Check if a specific hero is online."""
    return {"is_online": presence_manager.is_online(hero_id)}


# Utility function for other modules to send notifications
async def send_episode_notification(
    hero_id: str,
    episode_id: str,
    episode_title: str,
) -> bool:
    """Send notification that a new episode is ready.

    Args:
        hero_id: The hero's ID
        episode_id: The new episode's ID
        episode_title: The episode title

    Returns:
        True if notification was sent
    """
    return await presence_manager.send_notification(
        hero_id,
        "episode_ready",
        {"episode_id": episode_id, "title": episode_title},
    )


async def send_crossover_invite(
    target_hero_id: str,
    from_hero_id: str,
    from_hero_name: str,
) -> bool:
    """Send a crossover team-up invitation.

    Args:
        target_hero_id: The hero to invite
        from_hero_id: The inviting hero's ID
        from_hero_name: The inviting hero's name

    Returns:
        True if notification was sent
    """
    return await presence_manager.send_notification(
        target_hero_id,
        "crossover_invite",
        {"from_hero_id": from_hero_id, "from_hero_name": from_hero_name},
    )


async def broadcast_global_event(
    event_title: str,
    event_description: str,
    event_type: str = "canon_event",
    significance: float = 50.0,
) -> int:
    """Broadcast a global canon event to all online users.

    Args:
        event_title: The event title
        event_description: Brief description
        event_type: Type of event (canon_event, global_arc, emergency)
        significance: Event significance score

    Returns:
        Number of users notified
    """
    logger.info(f"Broadcasting global event: {event_title} to all connected users")

    data = {
        "event_title": event_title,
        "event_description": event_description,
        "event_type": event_type,
        "significance": significance,
    }

    sent_count = await presence_manager.broadcast_to_all("global_event", data)

    logger.info(f"Global event '{event_title}' broadcast to {sent_count} users")
    return sent_count


async def broadcast_arc_update(
    arc_title: str,
    current_phase: int,
    total_phases: int,
    phase_description: str,
) -> int:
    """Broadcast a global arc phase update to all online users.

    Args:
        arc_title: The arc title
        current_phase: Current phase number
        total_phases: Total number of phases
        phase_description: Description of current phase

    Returns:
        Number of users notified
    """
    data = {
        "arc_title": arc_title,
        "current_phase": current_phase,
        "total_phases": total_phases,
        "phase_description": phase_description,
    }

    return await presence_manager.broadcast_to_all("arc_update", data)
