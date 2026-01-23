"""Presence manager for tracking online users and activity."""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class PresenceManager:
    """Manages WebSocket connections and user presence state.

    This class handles:
    - Active WebSocket connections per hero
    - Online/offline status tracking
    - Activity feed broadcasting to friends
    - Real-time notifications
    """

    def __init__(self) -> None:
        """Initialize the presence manager."""
        # hero_id -> WebSocket connection
        self._connections: dict[str, WebSocket] = {}
        # hero_id -> last activity timestamp
        self._last_activity: dict[str, datetime] = {}
        # hero_id -> set of friend hero_ids
        self._friend_subscriptions: dict[str, set[str]] = {}
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

    async def connect(
        self,
        websocket: WebSocket,
        hero_id: str,
        friend_ids: list[str] | None = None,
    ) -> None:
        """Register a new WebSocket connection for a hero.

        Args:
            websocket: The WebSocket connection
            hero_id: The hero's ID
            friend_ids: List of friend hero IDs to subscribe to
        """
        await websocket.accept()

        async with self._lock:
            # Close existing connection if any
            if hero_id in self._connections:
                try:
                    await self._connections[hero_id].close()
                except Exception:
                    pass

            self._connections[hero_id] = websocket
            self._last_activity[hero_id] = datetime.now(timezone.utc)
            self._friend_subscriptions[hero_id] = set(friend_ids or [])

        logger.info(f"Hero {hero_id} connected (WebSocket)")

        # Notify friends that this hero came online
        await self._broadcast_presence_change(hero_id, online=True)

    async def disconnect(self, hero_id: str) -> None:
        """Remove a WebSocket connection.

        Args:
            hero_id: The hero's ID
        """
        async with self._lock:
            self._connections.pop(hero_id, None)
            self._last_activity.pop(hero_id, None)
            self._friend_subscriptions.pop(hero_id, None)

        logger.info(f"Hero {hero_id} disconnected (WebSocket)")

        # Notify friends that this hero went offline
        await self._broadcast_presence_change(hero_id, online=False)

    async def update_activity(self, hero_id: str, activity_type: str) -> None:
        """Update a hero's last activity and broadcast to friends.

        Args:
            hero_id: The hero's ID
            activity_type: Type of activity (e.g., "reading_episode", "viewing_friends")
        """
        async with self._lock:
            self._last_activity[hero_id] = datetime.now(timezone.utc)

        # Don't broadcast every activity update, only significant ones
        if activity_type in ("episode_completed", "achievement_unlocked", "friend_added"):
            await self._broadcast_activity(hero_id, activity_type)

    async def send_notification(
        self,
        hero_id: str,
        notification_type: str,
        data: dict[str, Any],
    ) -> bool:
        """Send a notification to a specific hero.

        Args:
            hero_id: The hero's ID
            notification_type: Type of notification
            data: Notification data

        Returns:
            True if sent successfully, False otherwise
        """
        websocket = self._connections.get(hero_id)
        if not websocket:
            return False

        try:
            message = {
                "type": notification_type,
                "data": data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            await websocket.send_json(message)
            return True
        except Exception as e:
            logger.warning(f"Failed to send notification to {hero_id}: {e}")
            await self.disconnect(hero_id)
            return False

    async def broadcast_to_friends(
        self,
        hero_id: str,
        message_type: str,
        data: dict[str, Any],
    ) -> int:
        """Broadcast a message to all online friends of a hero.

        Args:
            hero_id: The hero's ID
            message_type: Type of message
            data: Message data

        Returns:
            Number of friends who received the message
        """
        friends = self._friend_subscriptions.get(hero_id, set())
        sent_count = 0

        for friend_id in friends:
            if await self.send_notification(friend_id, message_type, data):
                sent_count += 1

        return sent_count

    async def get_online_friends(self, hero_id: str) -> list[str]:
        """Get list of online friends for a hero.

        Args:
            hero_id: The hero's ID

        Returns:
            List of online friend hero IDs
        """
        friends = self._friend_subscriptions.get(hero_id, set())
        return [fid for fid in friends if fid in self._connections]

    async def get_friend_statuses(
        self,
        hero_id: str,
    ) -> list[dict[str, Any]]:
        """Get status information for all friends of a hero.

        Args:
            hero_id: The hero's ID

        Returns:
            List of friend status dictionaries
        """
        friends = self._friend_subscriptions.get(hero_id, set())
        statuses = []

        for friend_id in friends:
            is_online = friend_id in self._connections
            last_activity = self._last_activity.get(friend_id)

            statuses.append({
                "hero_id": friend_id,
                "is_online": is_online,
                "last_activity": last_activity.isoformat() if last_activity else None,
            })

        return statuses

    def is_online(self, hero_id: str) -> bool:
        """Check if a hero is currently online.

        Args:
            hero_id: The hero's ID

        Returns:
            True if online, False otherwise
        """
        return hero_id in self._connections

    def get_online_count(self) -> int:
        """Get the total number of online users.

        Returns:
            Number of active WebSocket connections
        """
        return len(self._connections)

    def get_all_connected_hero_ids(self) -> list[str]:
        """Get list of all connected hero IDs.

        Returns:
            List of all connected hero IDs
        """
        return list(self._connections.keys())

    async def broadcast_to_all(
        self,
        message_type: str,
        data: dict[str, Any],
    ) -> int:
        """Broadcast a message to ALL connected users.

        Used for global canon events that affect everyone.

        Args:
            message_type: Type of message
            data: Message data

        Returns:
            Number of users who received the message
        """
        sent_count = 0
        failed_connections: list[str] = []

        # Get snapshot of connections to avoid modification during iteration
        connections_snapshot = list(self._connections.items())

        for hero_id, websocket in connections_snapshot:
            try:
                message = {
                    "type": message_type,
                    "data": data,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                await websocket.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.warning(f"Failed to broadcast to {hero_id}: {e}")
                failed_connections.append(hero_id)

        # Clean up failed connections
        for hero_id in failed_connections:
            await self.disconnect(hero_id)

        logger.info(f"Broadcast sent to {sent_count} users ({len(failed_connections)} failed)")
        return sent_count

    async def update_friend_subscriptions(
        self,
        hero_id: str,
        friend_ids: list[str],
    ) -> None:
        """Update the friend subscription list for a hero.

        Args:
            hero_id: The hero's ID
            friend_ids: Updated list of friend hero IDs
        """
        async with self._lock:
            self._friend_subscriptions[hero_id] = set(friend_ids)

    async def _broadcast_presence_change(
        self,
        hero_id: str,
        online: bool,
    ) -> None:
        """Broadcast presence change to friends.

        Args:
            hero_id: The hero's ID
            online: True if coming online, False if going offline
        """
        message_type = "friend_online" if online else "friend_offline"
        data = {"hero_id": hero_id}

        await self.broadcast_to_friends(hero_id, message_type, data)

    async def _broadcast_activity(
        self,
        hero_id: str,
        activity_type: str,
    ) -> None:
        """Broadcast activity update to friends.

        Args:
            hero_id: The hero's ID
            activity_type: Type of activity
        """
        data = {
            "hero_id": hero_id,
            "activity": activity_type,
        }

        await self.broadcast_to_friends(hero_id, "friend_activity", data)

    async def handle_incoming_message(
        self,
        hero_id: str,
        message: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Handle incoming WebSocket message from a hero.

        Args:
            hero_id: The hero's ID
            message: The incoming message

        Returns:
            Response message or None
        """
        message_type = message.get("type", "")

        if message_type == "ping":
            # Heartbeat
            await self.update_activity(hero_id, "ping")
            return {"type": "pong", "timestamp": datetime.now(timezone.utc).isoformat()}

        elif message_type == "get_friends_status":
            # Request friend statuses
            statuses = await self.get_friend_statuses(hero_id)
            return {"type": "friends_status", "friends": statuses}

        elif message_type == "activity":
            # Activity update
            activity_type = message.get("activity", "unknown")
            await self.update_activity(hero_id, activity_type)
            return None

        elif message_type == "subscribe_friends":
            # Update friend subscriptions
            friend_ids = message.get("friend_ids", [])
            await self.update_friend_subscriptions(hero_id, friend_ids)
            return {"type": "subscribed", "count": len(friend_ids)}

        else:
            logger.warning(f"Unknown message type from {hero_id}: {message_type}")
            return {"type": "error", "message": "Unknown message type"}


# Global presence manager instance
presence_manager = PresenceManager()
