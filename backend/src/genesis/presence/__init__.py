"""Real-time presence module for WebSocket connections."""

from genesis.presence.manager import PresenceManager
from genesis.presence.router import router

__all__ = ["PresenceManager", "router"]
