"""
app/platforms/reddit.py
───────────────────────
Reddit adapter – OAuth2 "password" grant → self-post to a subreddit.

API docs : https://www.reddit.com/dev/api/#POST_api_submit
OAuth2   : https://github.com/reddit-archive/reddit/wiki/OAuth2
"""
import httpx
from datetime import datetime, timezone
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.config import settings


class RedditPlatform(BasePlatform):
    name = "Reddit"

    _TOKEN_URL  = "https://www.reddit.com/api/v1/access_token"
    _SUBMIT_URL = "https://oauth.reddit.com/api/submit"

    # ── private helpers ───────────────────────────────────────────────────────

    def _check_config(self) -> None:
        missing = [
            k for k, v in {
                "REDDIT_CLIENT_ID":     settings.REDDIT_CLIENT_ID,
                "REDDIT_CLIENT_SECRET": settings.REDDIT_CLIENT_SECRET,
                "REDDIT_USERNAME":      settings.REDDIT_USERNAME,
                "REDDIT_PASSWORD":      settings.REDDIT_PASSWORD,
            }.items() if not v
        ]
        if missing:
            raise ValueError(
                f"Reddit: missing credentials in .env → {', '.join(missing)}"
            )

    async def _get_token(self, client: httpx.AsyncClient) -> str:
        """Exchange username/password for a bearer access token."""
        resp = await client.post(
            self._TOKEN_URL,
            data={
                "grant_type": "password",
                "username":   settings.REDDIT_USERNAME,
                "password":   settings.REDDIT_PASSWORD,
            },
            auth=(settings.REDDIT_CLIENT_ID, settings.REDDIT_CLIENT_SECRET),
            headers={"User-Agent": settings.REDDIT_USER_AGENT},
            timeout=15,
        )
        resp.raise_for_status()
        body = resp.json()
        if "access_token" not in body:
            raise ValueError(f"Reddit token exchange failed: {body}")
        return body["access_token"]

    # ── public interface ──────────────────────────────────────────────────────

    async def post(self, message: str) -> PlatformResult:
        now = datetime.now(timezone.utc)
        try:
            self._check_config()

            async with httpx.AsyncClient() as client:
                token = await self._get_token(client)

                resp = await client.post(
                    self._SUBMIT_URL,
                    # Reddit's submit endpoint expects form-encoded data, not JSON
                    data={
                        "sr":       settings.REDDIT_SUBREDDIT,
                        "kind":     "self",
                        "title":    message[:300],
                        "text":     message,
                        "resubmit": "true",
                        "nsfw":     "false",
                        "spoiler":  "false",
                    },
                    headers={
                        "Authorization": f"bearer {token}",
                        "User-Agent":    settings.REDDIT_USER_AGENT,
                    },
                    timeout=20,
                )
                resp.raise_for_status()
                body = resp.json()

                # Reddit wraps results: {"json": {"errors": [], "data": {"url": ...}}}
                api_errors = body.get("json", {}).get("errors", [])
                if api_errors:
                    raise ValueError(f"Reddit API errors: {api_errors}")

                post_url = body.get("json", {}).get("data", {}).get("url")
                if not post_url:
                    raise ValueError(
                        f"Reddit did not return a post URL. Response: {body}"
                    )

            return PlatformResult(
                platform=self.name,
                status="success",
                posted_url=post_url,
                public_access=True,
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
