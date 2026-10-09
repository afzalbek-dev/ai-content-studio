"""AI Content Generation and Repurposing API routes."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from content_studio.models.content import ContentType, ContentItemCreate
from content_studio.models.generation import (
    GenerateRequest,
    GenerateResponse,
    RepurposeRequest,
    RepurposeResponse,
)
from content_studio.database.repository import ContentStudioRepository
from content_studio.engine.blog_generator import BlogGenerator
from content_studio.engine.social_generator import SocialGenerator
from content_studio.engine.video_script_generator import VideoScriptGenerator
from content_studio.engine.repurposer import ContentRepurposer
from content_studio.api.dependencies import (
    get_repo,
    get_repurposer,
    get_blog_generator,
    get_social_generator,
    get_video_generator,
)

router = APIRouter(prefix="/generator", tags=["Generator"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_content(
    payload: GenerateRequest,
    save_to_project_id: Optional[int] = Query(None, description="Optional Project ID to save draft into"),
    repo: ContentStudioRepository = Depends(get_repo),
    blog_gen: BlogGenerator = Depends(get_blog_generator),
    social_gen: SocialGenerator = Depends(get_social_generator),
    video_gen: VideoScriptGenerator = Depends(get_video_generator),
):
    """Generate channel-optimized AI content with optional project auto-saving."""
    if payload.content_type == ContentType.BLOG:
        res = await blog_gen.generate(
            topic=payload.topic,
            tone=payload.tone,
            target_audience=payload.target_audience or "General",
            keywords=payload.keywords,
            length_constraint=payload.length_constraint or "medium",
        )
    elif payload.content_type == ContentType.VIDEO_SCRIPT:
        res = await video_gen.generate(
            topic=payload.topic,
            tone=payload.tone,
            keywords=payload.keywords,
        )
    else:
        res = await social_gen.generate(
            topic=payload.topic,
            content_type=payload.content_type,
            tone=payload.tone,
            keywords=payload.keywords,
        )

    if save_to_project_id:
        proj = await repo.get_project(save_to_project_id)
        if not proj:
            raise HTTPException(status_code=404, detail="Target project not found")
        item = await repo.create_content_item(
            ContentItemCreate(
                project_id=save_to_project_id,
                title=res.title,
                body=res.body,
                content_type=res.content_type,
                tags=payload.keywords,
                tone=payload.tone,
            )
        )
        res.metadata["saved_content_id"] = str(item.id)

    return res


@router.post("/repurpose", response_model=RepurposeResponse)
async def repurpose_content(
    payload: RepurposeRequest,
    save_to_project_id: Optional[int] = Query(None, description="Optional Project ID to auto-save assets"),
    repo: ContentStudioRepository = Depends(get_repo),
    repurposer: ContentRepurposer = Depends(get_repurposer),
):
    """Repurpose source text across multiple social and video channels."""
    if save_to_project_id:
        proj = await repo.get_project(save_to_project_id)
        if not proj:
            raise HTTPException(status_code=404, detail="Target project not found")

    result = await repurposer.repurpose(payload)

    if save_to_project_id:
        for item in result.items:
            await repo.create_content_item(
                ContentItemCreate(
                    project_id=save_to_project_id,
                    title=item.title,
                    body=item.body,
                    content_type=item.content_type,
                    tone=payload.tone,
                )
            )

    return result
