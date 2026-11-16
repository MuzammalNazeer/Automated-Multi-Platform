"""
app/config.py
─────────────
Loads every API credential from the .env file at project root.
Add your real values to .env (never commit that file).
"""
import os
from dotenv import load_dotenv

load_dotenv(override=True)


class Settings:
    # ── Reddit ────────────────────────────────────────────────────────────────
    # Create a "script" type app → https://www.reddit.com/prefs/apps
    REDDIT_CLIENT_ID:     str = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    REDDIT_USERNAME:      str = os.getenv("REDDIT_USERNAME", "")
    REDDIT_PASSWORD:      str = os.getenv("REDDIT_PASSWORD", "")
    REDDIT_USER_AGENT:    str = os.getenv("REDDIT_USER_AGENT", "AutoPostingBot/1.0")
    REDDIT_SUBREDDIT:     str = os.getenv("REDDIT_SUBREDDIT", "test")

    # ── Telegram ──────────────────────────────────────────────────────────────
    # Bot token from @BotFather; chat_id = @channel_username for public channels
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID:   str = os.getenv("TELEGRAM_CHAT_ID", "")

    # ── Dev.to ────────────────────────────────────────────────────────────────
    # API key → https://dev.to/settings/extensions
    DEVTO_API_KEY: str = os.getenv("DEVTO_API_KEY", "")

    # ── Hashnode ──────────────────────────────────────────────────────────────
    # Token → https://hashnode.com/settings/developer
    # Publication ID → your blog's Settings > Advanced
    HASHNODE_TOKEN:          str = os.getenv("HASHNODE_TOKEN", "")
    HASHNODE_PUBLICATION_ID: str = os.getenv("HASHNODE_PUBLICATION_ID", "")

    # ── Discord ───────────────────────────────────────────────────────────────
    # Webhook URL → channel Settings > Integrations > Webhooks > New Webhook
    DISCORD_WEBHOOK_URL: str = os.getenv("DISCORD_WEBHOOK_URL", "")

    # ── LinkedIn ──────────────────────────────────────────────────────────────
    # OAuth2 access token (scope: w_member_social)
    # Person URN: numeric ID from GET https://api.linkedin.com/v2/me
    LINKEDIN_ACCESS_TOKEN: str = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
    LINKEDIN_PERSON_URN:   str = os.getenv("LINKEDIN_PERSON_URN", "")

    # ── Mastodon ──────────────────────────────────────────────────────────────
    # Token → Preferences > Development > New Application (scope: write:statuses)
    MASTODON_ACCESS_TOKEN: str = os.getenv("MASTODON_ACCESS_TOKEN", "")
    MASTODON_INSTANCE_URL: str = os.getenv("MASTODON_INSTANCE_URL", "https://mastodon.social")


settings = Settings()
