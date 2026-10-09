"""Content Export API routes supporting Markdown, HTML, and JSON formats."""

import markdown
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import HTMLResponse, PlainTextResponse

from content_studio.models.generation import ExportFormat
from content_studio.database.repository import ContentStudioRepository
from content_studio.api.dependencies import get_repo

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/{content_id}")
async def export_content(
    content_id: int,
    format: ExportFormat = Query(ExportFormat.MARKDOWN, description="Export format: markdown, html, json"),
    repo: ContentStudioRepository = Depends(get_repo),
):
    """Export formatted content for publishing, CMS import, or documentation."""
    item = await repo.get_content_item(content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")

    if format == ExportFormat.MARKDOWN:
        return PlainTextResponse(
            content=item.body,
            media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="content_{content_id}.md"'},
        )

    elif format == ExportFormat.HTML:
        body_html = markdown.markdown(
            item.body,
            extensions=["fenced_code", "tables"],
        )
        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{item.title}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #24292e; }}
    h1, h2, h3 {{ color: #1a1f2c; }}
    code {{ background: #f6f8fa; padding: 2px 5px; border-radius: 4px; }}
    pre {{ background: #f6f8fa; padding: 16px; border-radius: 6px; overflow-x: auto; }}
    blockquote {{ border-left: 4px solid #0366d6; margin: 0; padding-left: 16px; color: #586069; }}
    hr {{ border: 0; height: 1px; background: #e1e4e8; margin: 24px 0; }}
  </style>
</head>
<body>
  {body_html}
</body>
</html>"""
        return HTMLResponse(content=full_html)

    else:
        return {
            "id": item.id,
            "project_id": item.project_id,
            "title": item.title,
            "body": item.body,
            "content_type": item.content_type.value,
            "status": item.status.value,
            "tone": item.tone.value,
            "word_count": item.word_count,
            "tags": item.tags,
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat(),
        }
