"""
Posting service – orchestrates all platform adapters concurrently.

Each platform is called with asyncio.gather so they all run in parallel.
A failure on one platform never blocks the others.
"""
import asyncio
from typing import List
from app.schemas import PlatformResult
from app.platforms.reddit import RedditPlatform
from app.platforms.telegram import TelegramPlatform
from app.platforms.devto import DevtoPlatform
from app.platforms.hashnode import HashnodePlatform
from app.platforms.discord import DiscordPlatform
from app.platforms.linkedin import LinkedInPlatform
from app.platforms.mastodon import MastodonPlatform


# Registry of all active platform adapters
PLATFORMS = [
    RedditPlatform(),
    TelegramPlatform(),
    DevtoPlatform(),
    HashnodePlatform(),
    DiscordPlatform(),
    LinkedInPlatform(),
    MastodonPlatform(),
]


async def post_to_all_platforms(message: str) -> List[PlatformResult]:
    """
    Post *message* to every registered platform concurrently.

    Returns a list of PlatformResult objects (one per platform).
    Errors inside individual adapters are captured inside each adapter
    and returned as a failed result – this function never raises.
    """
    tasks = [platform.post(message) for platform in PLATFORMS]
    results: List[PlatformResult] = await asyncio.gather(*tasks)
    return list(results)

