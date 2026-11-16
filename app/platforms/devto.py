"""
Dev.to (Forem) platform adapter.

Creates and immediately publishes an article using the Dev.to Articles API.

API Reference: https://developers.forem.com/api/v1#tag/articles/operation/createArticle

Setup:
    1. Go to https://dev.to/settings/extensions
    2. Generate an API key under "DEV API Keys"
    3. Set DEVTO_API_KEY in .env
"""
import httpx
from datetime import datetime, timezone
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.config import settings


class DevtoPlatform(BasePlatform):
    name = "Dev.to"

    ARTICLES_URL = "https://dev.to/api/articles"

    async def post(self, message: str) -> PlatformResult:
        now = datetime.now(timezone.utc)
        try:
            if not settings.DEVTO_API_KEY:
                raise ValueError(
                    "Dev.to API key is not configured. "
                    "Set DEVTO_API_KEY in .env"
                )

            # Build a title from the first sentence / 60 chars of the message
            title = message.split(".")[0].strip()
            if len(title) > 100:
                title = title[:97] + "…"
            elif not title:
                title = message[:60].rstrip() + ("…" if len(message) > 60 else "")

            payload = {
                "article": {
                    "title": title,
                    "body_markdown": message,
                    "published": True,
                    "tags": ["automation", "api", "python", "fastapi"],
                }
            }

            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    self.ARTICLES_URL,
                    json=payload,
                    headers={
                        "api-key": settings.DEVTO_API_KEY,
                        "Content-Type": "application/json",
                        "Accept": "application/vnd.forem.api-v1+json",
                    },
                    timeout=20,
                )
                resp.raise_for_status()
                data = resp.json()

                posted_url = data.get("url")
                if not posted_url:
                    raise ValueError(
                        f"Dev.to did not return an article URL. Response: {data}"
                    )

                return PlatformResult(
                    platform=self.name,
                    status="success",
                    posted_url=posted_url,
                    public_access=True,
                    date=now.strftime("%Y-%m-%d"),
                    time=now.strftime("%H:%M:%S"),
                    error=None,
                )

        except Exception as exc:
            return PlatformResult(
                platform=self.name,
                status="failed",
                posted_url=None,
                public_access=False,
                date=now.strftime("%Y-%m-%d"),
                time=now.strftime("%H:%M:%S"),
                error=str(exc),
            )

