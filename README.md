# Automated Multi-Platform Posting System 🚀

A **FastAPI** application that publishes a short message across **7 third-party platforms** in a single API call.

Built for the **Dxora Technologies Python Practical Test**.

---

## Platforms Integrated

| # | Platform | API Type | Public Post |
|---|----------|----------|-------------|
| 1 | **Reddit** | REST (OAuth 2.0 Password Flow) | ✅ Yes |
| 2 | **Telegram** | Bot API | ✅ Public channels |
| 3 | **Dev.to** | REST (Articles API) | ✅ Yes |
| 4 | **Hashnode** | GraphQL v2 | ✅ Yes |
| 5 | **Discord** | Webhook | ⚠️ Members only |
| 6 | **LinkedIn** | UGC Posts API (OAuth 2.0) | ✅ Yes |
| 7 | **Mastodon** | REST (Statuses API) | ✅ Yes |

---

## Project Structure

```
automated-posting/
│
├── app/
│   ├── main.py               # FastAPI app & /posting endpoint
│   ├── schemas.py            # Pydantic request/response models + validation
│   ├── config.py             # Settings loaded from environment variables
│   ├── platforms/
│   │   ├── base.py           # Abstract base class for all adapters
│   │   ├── reddit.py         # Reddit adapter
│   │   ├── telegram.py       # Telegram adapter
│   │   ├── devto.py          # Dev.to adapter
│   │   ├── hashnode.py       # Hashnode adapter
│   │   ├── discord.py        # Discord adapter
│   │   ├── linkedin.py       # LinkedIn adapter
│   │   └── mastodon.py       # Mastodon adapter
│   └── services/
│       └── posting_service.py  # Orchestrates all platforms concurrently
│
├── tests/
│   └── test_posting.py       # Pytest async test suite
│
├── .env.example              # Template for environment variables
├── .gitignore
├── pytest.ini                # asyncio_mode = auto
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python 3.10+
- pip

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/automated-posting.git
cd automated-posting
```

### 2. Create and activate a virtual environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API credentials

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Open `.env` and replace each placeholder with your actual API key / token.
See [Getting API Credentials](#getting-api-credentials) below for step-by-step instructions.

### 5. Start the server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload
```

The API is now running at **http://localhost:4000**

---

## API Usage

### Interactive Docs (Swagger UI)

Open **http://localhost:4000/docs** in your browser.

### Endpoint

```
POST http://localhost:4000/posting
Content-Type: application/json
```

### Request Body

```json
{
  "message": "Check out our latest business platform and grow your online visibility. https://example.com"
}
```

### Input Validation Rules

| Rule | Detail |
|------|--------|
| Max length | 200 characters |
| URL | Exactly **one** valid `http://` or `https://` link must be present |
| URL validity | The URL must be well-formed |

### Sample cURL Request

```bash
curl -X POST "http://localhost:4000/posting" \
  -H "Content-Type: application/json" \
  -d '{"message": "Check out our latest business platform. https://example.com"}'
```

### Sample Response

```json
{
  "success": true,
  "results": [
    {
      "platform": "Reddit",
      "status": "success",
      "posted_url": "https://www.reddit.com/r/test/comments/abc123/check_out_our_latest_business_platform/",
      "public_access": true,
      "date": "2026-11-16",
      "time": "18:30:00",
      "error": null
    },
    {
      "platform": "Telegram",
      "status": "success",
      "posted_url": "https://t.me/mychannel/42",
      "public_access": true,
      "date": "2026-11-16",
      "time": "18:30:01",
      "error": null
    },
    {
      "platform": "Dev.to",
      "status": "success",
      "posted_url": "https://dev.to/username/check-out-our-latest-business-platform-xyz",
      "public_access": true,
      "date": "2026-11-16",
      "time": "18:30:01",
      "error": null
    },
    {
      "platform": "Hashnode",
      "status": "success",
      "posted_url": "https://yourblog.hashnode.dev/check-out-our-latest-business-platform",
      "public_access": true,
      "date": "2026-11-16",
      "time": "18:30:02",
      "error": null
    },
    {
      "platform": "Discord",
      "status": "success",
      "posted_url": "https://discord.com/channels/@me/987654321/111222333",
      "public_access": false,
      "date": "2026-11-16",
      "time": "18:30:01",
      "error": null
    },
    {
      "platform": "LinkedIn",
      "status": "success",
      "posted_url": "https://www.linkedin.com/feed/update/urn:li:ugcPost:999888777/",
      "public_access": true,
      "date": "2026-11-16",
      "time": "18:30:02",
      "error": null
    },
    {
      "platform": "Mastodon",
      "status": "success",
      "posted_url": "https://mastodon.social/@username/112345678901234567",
      "public_access": true,
      "date": "2026-11-16",
      "time": "18:30:01",
      "error": null
    }
  ]
}
```

### Validation Error Response (422)

```json
{
  "success": false,
  "detail": "Input validation failed.",
  "errors": [
    {
      "field": "body -> message",
      "message": "Value error, Message must not exceed 200 characters (current length: 215)."
    }
  ]
}
```

---

## Running Tests

```bash
pytest tests/ -v
```

Expected output:

```
tests/test_posting.py::test_health_check              PASSED
tests/test_posting.py::test_valid_message_returns_results PASSED
tests/test_posting.py::test_message_too_long           PASSED
tests/test_posting.py::test_message_without_url        PASSED
tests/test_posting.py::test_message_with_multiple_urls PASSED
tests/test_posting.py::test_missing_message_field      PASSED
tests/test_posting.py::test_response_structure         PASSED
```

---

## Getting API Credentials

### Reddit
1. Go to https://www.reddit.com/prefs/apps
2. Click **Create Another App** → choose **script**
3. Copy `client_id` (under the app name) and `client_secret`
4. Use your Reddit `username` and `password`
5. Set `REDDIT_SUBREDDIT` to any subreddit you moderate (or use `test`)

### Telegram
1. Message `@BotFather` on Telegram → `/newbot`
2. Copy the **HTTP API token**
3. Add the bot to your channel as an admin
4. Set `TELEGRAM_CHAT_ID` to `@your_channel_username` (for public channels)

### Dev.to
1. Go to https://dev.to/settings/extensions
2. Generate a new **API Key**

### Hashnode
1. Go to https://hashnode.com/settings/developer
2. Generate a **Personal Access Token**
3. Find your **Publication ID** in your blog's dashboard URL

### Discord
1. Open your server → channel Settings → **Integrations** → **Webhooks**
2. Click **New Webhook** and copy the URL

### LinkedIn
1. Create a LinkedIn App at https://www.linkedin.com/developers/apps
2. Request the **w_member_social** OAuth scope
3. Generate an access token via the OAuth 2.0 authorization flow
4. Find your Person URN (numeric ID) from the `/v2/me` endpoint

### Mastodon
1. Go to your instance's Preferences → **Development** → **New Application**
2. Grant the `write:statuses` scope
3. Copy the **Access Token**

---

## Architecture

```
POST /posting
     │
     ▼
PostingRequest (Pydantic validation)
     │  ✓ max 200 chars
     │  ✓ exactly 1 URL
     ▼
posting_service.post_to_all_platforms()
     │  asyncio.gather() – all platforms run concurrently
     ├──► RedditPlatform.post()
     ├──► TelegramPlatform.post()
     ├──► DevtoPlatform.post()
     ├──► HashnodePlatform.post()
     ├──► DiscordPlatform.post()
     ├──► LinkedInPlatform.post()
     └──► MastodonPlatform.post()
              │  Each catches its own errors
              ▼
         [PlatformResult, ...]
              │
              ▼
         PostingResponse
```

- **Concurrent**: all platform calls are made simultaneously with `asyncio.gather`
- **Fault-isolated**: one failing platform never affects the others
- **Extensible**: add new platforms by subclassing `BasePlatform` and registering in `posting_service.py`

---

## Security Notes

- All credentials are stored in `.env` (never committed)
- `.gitignore` excludes `.env`
- `.env.example` is committed as a template with placeholder values only

---

## License

MIT

