"""Base class for AI Agent Rooms."""

from abc import ABC, abstractmethod
from typing import Any


class BaseRoom(ABC):
    """Abstract base class for content generation rooms."""

    @abstractmethod
    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process input and generate output."""
        pass

    @abstractmethod
    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input data before processing."""
        pass

    @abstractmethod
    def get_output_schema(self) -> dict[str, Any]:
        """Return the expected output schema."""
        pass
