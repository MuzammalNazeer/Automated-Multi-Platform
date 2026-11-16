"""
app/platforms/telegram.py
─────────────────────────
Telegram adapter – Bot API sendMessage to a chat/channel.

API docs: https://core.telegram.org/bots/api#sendmessage

Setup
-----
1. Create a bot with @BotFather and copy the HTTP API token.
2. Add the bot as an admin to your channel.
3. Set TELEGRAM_CHAT_ID to @channel_username (public) or the numeric chat id.
"""
import httpx
from datetime import datetime, timezone
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.config import settings


class TelegramPlatform(BasePlatform):
    name = "Telegram"

    _API_BASE = "https://api.telegram.org"

    async def post(self, message: str) -> PlatformResult:
        now = datetime.now(timezone.utc)
        try:
            if not settings.TELEGRAM_BOT_TOKEN:
                raise ValueError(
                    "Telegram: TELEGRAM_BOT_TOKEN is not set in .env"
                )
            if not settings.TELEGRAM_CHAT_ID:
                raise ValueError(
                    "Telegram: TELEGRAM_CHAT_ID is not set in .env"
                )

            url = f"{self._API_BASE}/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    url,
                    json={
                        "chat_id":                  settings.TELEGRAM_CHAT_ID,
                        "text":                     message,
                        "parse_mode":               "HTML",
                        "disable_web_page_preview": False,
                    },
                    timeout=15,
                )
                resp.raise_for_status()
                body = resp.json()

            if not body.get("ok"):
                raise ValueError(
                    f"Telegram error [{body.get('error_code')}]: "
                    f"{body.get('description')}"
                )

            msg_id      = body["result"]["message_id"]
            chat_id_str = str(settings.TELEGRAM_CHAT_ID).strip()

            # Build a public deep-link only for public @username channels
            if chat_id_str.startswith("@"):
                channel = chat_id_str.lstrip("@")
                posted_url = f"https://t.me/{channel}/{msg_id}"
                public     = True
            else:
                posted_url = None   # private groups have no stable public URL
                public     = False

            return PlatformResult(
                platform=self.name,
                status="success",
                posted_url=posted_url,
                public_access=public,
                date=now.strftime("%Y-%m-%d"),
                time=now.strftime("%H:%M:%S"),
            )

        except Exception as exc:
            return PlatformResult(
                platform=self.name,
                status="failed",
                date=now.strftime("%Y-%m-%d"),
                time=now.strftime("%H:%M:%S"),
                error=str(exc),
            )
