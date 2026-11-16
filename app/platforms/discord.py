"""
Discord platform adapter.

Posts a message to a Discord channel using an Incoming Webhook.
No bot token is required – just a webhook URL created in channel settings.

API Reference: https://discord.com/developers/docs/resources/webhook#execute-webhook

Setup:
    1. Open your Discord server.
    2. Go to Channel Settings > Integrations > Webhooks > New Webhook.
    3. Copy the Webhook URL and set it as DISCORD_WEBHOOK_URL in .env.
"""
import httpx
from datetime import datetime, timezone
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.config import settings


class DiscordPlatform(BasePlatform):
    name = "Discord"

    async def post(self, message: str) -> PlatformResult:
        now = datetime.now(timezone.utc)
        try:
            if not settings.DISCORD_WEBHOOK_URL:
                raise ValueError(
                    "DISCORD_WEBHOOK_URL is not configured. "
                    "Create a webhook in your Discord channel settings."
                )

            # Validate it looks like a Discord webhook URL
            if "discord.com/api/webhooks/" not in settings.DISCORD_WEBHOOK_URL:
                raise ValueError(
                    "DISCORD_WEBHOOK_URL does not look like a valid Discord webhook URL."
                )

            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    settings.DISCORD_WEBHOOK_URL,
                    json={
                        "content": message,
                        "username": "AutoPostBot",
                    },
                    # ?wait=true instructs Discord to return the created message object
                    params={"wait": "true"},
                    timeout=15,
                )
                resp.raise_for_status()
                data = resp.json()

                # Build a jump-to-message URL from the returned channel & message IDs
                guild_id   = data.get("guild_id")
                channel_id = data.get("channel_id")
                message_id = data.get("id")

                posted_url = None
                if guild_id and channel_id and message_id:
                    posted_url = (
                        f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"
                    )
                elif channel_id and message_id:
                    # DM channel (no guild) – rare for webhooks but handle it
                    posted_url = (
                        f"https://discord.com/channels/@me/{channel_id}/{message_id}"
                    )

                return PlatformResult(
                    platform=self.name,
                    status="success",
                    posted_url=posted_url,
                    public_access=False,   # Discord channels require server membership
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

