import html

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.politicians import Politician
from app.models.promises import ModerationStatus, Promise

router = APIRouter(prefix="/og", tags=["og"])


@router.get("/promises/{slug}", response_class=HTMLResponse)
async def og_promise(slug: str, db: AsyncSession = Depends(get_db)) -> HTMLResponse:
    """Return a minimal HTML page with OG meta tags for social bot crawlers.

    Only serves approved promises (T-03-08 — non-approved return 404).
    T-03-10: slug param is used in parameterized ORM query — no SQL injection risk.
    D-17: This endpoint is called by the reverse proxy for known bot user-agents.
    All string values are html.escaped to prevent XSS in the returned HTML.
    """
    stmt = (
        select(
            Promise,
            Politician.name_hy.label("politician_name"),
            Politician.photo_url.label("photo_url"),
        )
        .join(Politician, Politician.id == Promise.politician_id)
        .where(
            Promise.slug == slug,
            Promise.moderation_status == ModerationStatus.approved,
        )
    )
    result = await db.execute(stmt)
    row = result.first()

    if row is None:
        raise HTTPException(status_code=404, detail="Promise not found")

    promise, politician_name, photo_url = row

    title = html.escape(promise.title_hy)
    description_raw = promise.quote_hy[:150] + " — " + politician_name
    description = html.escape(description_raw)
    image_url = photo_url or "https://khostumner.am/default-og-image.png"
    canonical_url = f"https://khostumner.am/promises/{html.escape(promise.slug)}"

    og_html = f"""<!DOCTYPE html>
<html lang="hy">
<head>
  <meta charset="utf-8" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:image" content="{image_url}" />
  <meta property="og:url" content="{canonical_url}" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="Խոստումներ" />
  <title>{title}</title>
</head>
<body></body>
</html>"""

    return HTMLResponse(content=og_html, status_code=200)