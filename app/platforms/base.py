"""
app/platforms/base.py
─────────────────────
Abstract base class that every platform adapter must implement.
"""
from abc import ABC, abstractmethod
from app.schemas import PlatformResult


class BasePlatform(ABC):
    """
    Contract for all platform adapters.

    - Every adapter must set a class-level `name` attribute.
    - `post()` must NEVER raise; it always returns a PlatformResult,
      capturing any exception as a failed result.
    """

    name: str = "Unknown"

    @abstractmethod
    async def post(self, message: str) -> PlatformResult:
        """Post *message* to the platform and return a PlatformResult."""
        ...
