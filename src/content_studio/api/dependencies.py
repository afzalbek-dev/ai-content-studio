"""Shared FastAPI dependencies for AI Content Studio."""

from fastapi import Request
from content_studio.database.repository import ContentStudioRepository
from content_studio.engine.blog_generator import BlogGenerator
from content_studio.engine.social_generator import SocialGenerator
from content_studio.engine.video_script_generator import VideoScriptGenerator
from content_studio.engine.repurposer import ContentRepurposer


def get_repo(request: Request) -> ContentStudioRepository:
    """Retrieve database repository from application state."""
    return request.app.state.repo


def get_repurposer(request: Request) -> ContentRepurposer:
    """Retrieve repurposer engine from application state."""
    return request.app.state.repurposer


def get_blog_generator(request: Request) -> BlogGenerator:
    """Retrieve blog generator engine from application state."""
    return request.app.state.blog_gen


def get_social_generator(request: Request) -> SocialGenerator:
    """Retrieve social media generator engine from application state."""
    return request.app.state.social_gen


def get_video_generator(request: Request) -> VideoScriptGenerator:
    """Retrieve video script generator engine from application state."""
    return request.app.state.video_gen
