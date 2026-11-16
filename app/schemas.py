"""
app/schemas.py
──────────────
Pydantic v2 request / response models with full input validation.
"""
import re
from urllib.parse import urlparse
from typing import List, Optional
from pydantic import BaseModel, field_validator


# ── URL helpers ───────────────────────────────────────────────────────────────

_URL_PATTERN = re.compile(r"https?://[^\s]+")


def _find_urls(text: str) -> List[str]:
    """Return every http/https URL found in *text*."""
    return _URL_PATTERN.findall(text)


def _is_valid_url(url: str) -> bool:
    """True when *url* has a valid scheme and a non-empty network location."""
    try:
        p = urlparse(url)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False


# ── Request model ─────────────────────────────────────────────────────────────

class PostingRequest(BaseModel):
    """
    Payload accepted by POST /posting.

    Rules
    -----
    - message: 1–200 characters, containing exactly one valid HTTP/HTTPS URL.
    """
    message: str

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()

        # 1. Must not be empty
        if not value:
            raise ValueError("Message must not be empty.")

        # 2. Must not exceed 200 characters
        if len(value) > 200:
            raise ValueError(
                f"Message must not exceed 200 characters "
                f"(received {len(value)} characters)."
            )

        # 3. Must contain exactly one CTA URL
        urls = _find_urls(value)
        if not urls:
            raise ValueError(
                "Message must contain exactly one CTA link. No URL was found."
            )
        if len(urls) > 1:
            raise ValueError(
                f"Message must contain exactly one CTA link, "
                f"but {len(urls)} URLs were found."
            )

        # 4. The URL must be well-formed
        if not _is_valid_url(urls[0]):
            raise ValueError(
                f"The URL '{urls[0]}' is not a valid HTTP/HTTPS URL."
            )

        return value


# ── Response models ───────────────────────────────────────────────────────────

class PlatformResult(BaseModel):
    """Result for one platform posting attempt."""
    platform:      str
    status:        str            # "success" | "failed"
    posted_url:    Optional[str] = None
    public_access: bool          = False
    date:          Optional[str] = None   # "YYYY-MM-DD"
    time:          Optional[str] = None   # "HH:MM:SS"
    error:         Optional[str] = None


class PostingResponse(BaseModel):
    """Full response returned by POST /posting."""
    success: bool
    results: List[PlatformResult]
