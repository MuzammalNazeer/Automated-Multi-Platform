"""
Mastodon platform adapter.

Posts a public status ("toot") to any Mastodon-compatible fediverse instance.

API Reference: https://docs.joinmastodon.org/methods/statuses/#create

Setup:
    1. Log in to your Mastodon instance (default: mastodon.social).
    2. Go to Preferences > Development > New Application.
    3. Grant the write:statuses scope.
    4. Copy the Access Token under "Your access token".
    5. Set MASTODON_ACCESS_TOKEN (and optionally MASTODON_INSTANCE_URL) in .env.
"""
import httpx
from datetime import datetime, timezone
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.config import settings


class MastodonPlatform(BasePlatform):
    name = "Mastodon"

    async def post(self, message: str) -> PlatformResult:
        now = datetime.now(timezone.utc)
        try:
            if not settings.MASTODON_ACCESS_TOKEN:
                raise ValueError(
                    "MASTODON_ACCESS_TOKEN is not configured. "
                    "Generate one at: your-instance/settings/applications"
                )

            # Mastodon statuses are limited to 500 characters by default.
            # Our message is capped at 200 chars so we're safely under the limit.
            base_url = settings.MASTODON_INSTANCE_URL.rstrip("/")
            endpoint = f"{base_url}/api/v1/statuses"

            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    endpoint,
                    json={
                        "status": message,
                        "visibility": "public",   # public | unlisted | private | direct
                    },
                    headers={
                        "Authorization": f"Bearer {settings.MASTODON_ACCESS_TOKEN}",
                        "Content-Type": "application/json",
                    },
                    timeout=15,
                )
                resp.raise_for_status()
                data = resp.json()

                posted_url = data.get("url")
                if not posted_url:
                    raise ValueError(
                        f"Mastodon did not return a status URL. Response: {data}"
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

