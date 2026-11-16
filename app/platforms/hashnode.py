"""
Hashnode platform adapter.

Publishes an article to a Hashnode publication using the GraphQL API v2.

API Reference: https://apidocs.hashnode.com/

Setup:
    1. Go to https://hashnode.com/settings/developer
    2. Generate a Personal Access Token
    3. Find your Publication ID: open your blog dashboard; the ID is in
       Settings > Advanced or in the dashboard URL after /publication/
    4. Set HASHNODE_TOKEN and HASHNODE_PUBLICATION_ID in .env
"""
import httpx
from datetime import datetime, timezone
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.config import settings


class HashnodePlatform(BasePlatform):
    name = "Hashnode"

    API_URL = "https://gql.hashnode.com/"

    # GraphQL mutation to publish a post to a publication
    MUTATION = """
    mutation PublishPost($input: PublishPostInput!) {
      publishPost(input: $input) {
        post {
          id
          url
          title
        }
      }
    }
    """

    async def post(self, message: str) -> PlatformResult:
        now = datetime.now(timezone.utc)
        try:
            if not settings.HASHNODE_TOKEN:
                raise ValueError(
                    "HASHNODE_TOKEN is not configured. "
                    "Generate one at https://hashnode.com/settings/developer"
                )
            if not settings.HASHNODE_PUBLICATION_ID:
                raise ValueError(
                    "HASHNODE_PUBLICATION_ID is not configured. "
                    "Find it in your Hashnode blog's Settings > Advanced."
                )

            # Build a readable title from the message
            title = message.split(".")[0].strip()
            if len(title) > 100:
                title = title[:97] + "…"
            elif len(title) < 5:
                title = message[:80].rstrip() + ("…" if len(message) > 80 else "")

            variables = {
                "input": {
                    "title": title,
                    "contentMarkdown": message,
                    "publicationId": settings.HASHNODE_PUBLICATION_ID,
                    "tags": [],
                }
            }

            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    self.API_URL,
                    json={"query": self.MUTATION, "variables": variables},
                    headers={
                        "Authorization": settings.HASHNODE_TOKEN,
                        "Content-Type": "application/json",
                    },
                    timeout=20,
                )
                resp.raise_for_status()
                data = resp.json()

                # Surface GraphQL-level errors (HTTP 200 but with errors key)
                gql_errors = data.get("errors")
                if gql_errors:
                    messages = "; ".join(e.get("message", str(e)) for e in gql_errors)
                    raise ValueError(f"Hashnode GraphQL error: {messages}")

                post_data = (
                    data.get("data", {})
                        .get("publishPost", {})
                        .get("post", {})
                )
                posted_url = post_data.get("url")
                if not posted_url:
                    raise ValueError(
                        f"Hashnode did not return a post URL. Response: {data}"
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

