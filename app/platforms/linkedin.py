"""
LinkedIn platform adapter.

Shares a text post on behalf of a person using the LinkedIn Share API v2
(UGC Posts endpoint) with PUBLIC visibility.

API Reference:
  https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api

Setup:
    1. Create a LinkedIn App at https://www.linkedin.com/developers/apps
    2. Add the "Share on LinkedIn" and "Sign In with LinkedIn" products.
    3. Request the OAuth 2.0 scope: w_member_social
    4. Generate an access token (3-legged OAuth or use the token generator tool).
    5. Find your Person URN: call GET https://api.linkedin.com/v2/me
       and use the numeric "id" field (NOT the full URN string).
    6. Set LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_URN in .env
"""
import httpx
from datetime import datetime, timezone
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.config import settings


class LinkedInPlatform(BasePlatform):
    name = "LinkedIn"

    UGC_POSTS_URL = "https://api.linkedin.com/v2/ugcPosts"

    async def post(self, message: str) -> PlatformResult:
        now = datetime.now(timezone.utc)
        try:
            if not settings.LINKEDIN_ACCESS_TOKEN:
                raise ValueError(
                    "LINKEDIN_ACCESS_TOKEN is not configured."
                )
            if not settings.LINKEDIN_PERSON_URN:
                raise ValueError(
                    "LINKEDIN_PERSON_URN is not configured. "
                    "Call GET https://api.linkedin.com/v2/me to retrieve your numeric ID."
                )

            # Build the full person URN; allow user to supply either format
            person_urn = settings.LINKEDIN_PERSON_URN
            if not person_urn.startswith("urn:"):
                person_urn = f"urn:li:person:{person_urn}"

            payload = {
                "author": person_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": message},
                        "shareMediaCategory": "NONE",
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                },
            }

            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    self.UGC_POSTS_URL,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {settings.LINKEDIN_ACCESS_TOKEN}",
                        "Content-Type": "application/json",
                        "X-Restli-Protocol-Version": "2.0.0",
                    },
                    timeout=20,
                )
                resp.raise_for_status()

                # LinkedIn returns the new post URN in the X-RestLi-Id response header
                post_urn = (
                    resp.headers.get("x-restli-id")
                    or resp.headers.get("X-RestLi-Id")
                )

                posted_url = None
                if post_urn:
                    # e.g. urn:li:ugcPost:7123456789012345678
                    posted_url = f"https://www.linkedin.com/feed/update/{post_urn}/"

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

