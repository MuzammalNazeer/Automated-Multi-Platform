"""
FastAPI application entry point.

Start the server with:
    uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.schemas import PostingRequest, PostingResponse
from app.services.posting_service import post_to_all_platforms

# ── App instance ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="Automated Multi-Platform Posting System",
    description=(
        "A FastAPI service that publishes a short message across **7 third-party "
        "platforms** (Reddit, Telegram, Dev.to, Hashnode, Discord, LinkedIn, Mastodon) "
        "in a single API call.\n\n"
        "Built for the **Dxora Technologies Python Practical Test**."
    ),
    version="1.0.0",
    contact={
        "name": "Dxora Technologies – Practical Test",
        "email": "hr@chivoxai.com",
    },
    license_info={"name": "MIT"},
)


# ── Custom validation error handler ──────────────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return a clean, human-readable 422 body for every validation failure."""
    errors = []
    for error in exc.errors():
        # Remove internal Pydantic prefix noise from location
        loc = [str(l) for l in error["loc"] if l not in ("body",)]
        errors.append({
            "field": " -> ".join(loc) if loc else "message",
            "message": error["msg"].removeprefix("Value error, "),
        })
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "detail": "Input validation failed.",
            "errors": errors,
        },
    )


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"], summary="Health check")
async def health_check():
    """Returns service status. Use to verify the server is running."""
    return {
        "status": "ok",
        "message": "Automated Multi-Platform Posting System is running.",
        "version": "1.0.0",
        "docs": "http://localhost:4000/docs",
    }


@app.post(
    "/posting",
    response_model=PostingResponse,
    summary="Post a message to all configured platforms",
    tags=["Posting"],
    responses={
        200: {"description": "Posting results for each platform (some may have failed)"},
        422: {"description": "Validation error – message too long, missing URL, or invalid URL"},
    },
)
async def post_message(payload: PostingRequest) -> PostingResponse:
    """
    Accepts a JSON body with a **message** field and publishes it
    to all configured third-party platforms **concurrently**.

    ### Validation rules
    | Rule | Detail |
    |------|--------|
    | Max length | 200 characters |
    | CTA link | Exactly **one** `http://` or `https://` URL required |
    | URL validity | Must have a valid scheme and domain |

    ### Platform fault isolation
    If one platform fails (wrong credentials, API down, rate-limited),
    the remaining platforms still receive the message.
    """
    results = await post_to_all_platforms(payload.message)

    # overall success = at least one platform posted successfully
    overall_success = any(r.status == "success" for r in results)

    return PostingResponse(success=overall_success, results=results)

