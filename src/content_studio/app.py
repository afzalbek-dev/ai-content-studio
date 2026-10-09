"""FastAPI application factory for AI Content Studio."""

from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from content_studio.config import Settings, get_settings
from content_studio.database.repository import ContentStudioRepository
from content_studio.engine.blog_generator import BlogGenerator
from content_studio.engine.social_generator import SocialGenerator
from content_studio.engine.video_script_generator import VideoScriptGenerator
from content_studio.engine.repurposer import ContentRepurposer
from content_studio.api import (
    projects_router,
    content_router,
    generator_router,
    export_router,
    analytics_router,
)


def create_app(
    settings: Optional[Settings] = None,
    repo: Optional[ContentStudioRepository] = None,
    repurposer: Optional[ContentRepurposer] = None,
) -> FastAPI:
    """Create and configure FastAPI application instance."""
    app_settings = settings or get_settings()
    app_repo = repo or ContentStudioRepository(app_settings.sqlite_path)
    app_repurposer = repurposer or ContentRepurposer(app_settings)
    blog_gen = BlogGenerator(app_settings)
    social_gen = SocialGenerator(app_settings)
    video_gen = VideoScriptGenerator(app_settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup: initialize database schema
        await app_repo.init_db()
        yield
        # Shutdown hook

    app = FastAPI(
        title="AI Content Studio API",
        description="Autonomous AI-driven Content Generation, Editorial Hub & Cross-Channel Repurposing Engine",
        version="1.0.0",
        lifespan=lifespan,
    )

    # State injection
    app.state.settings = app_settings
    app.state.repo = app_repo
    app.state.repurposer = app_repurposer
    app.state.blog_gen = blog_gen
    app.state.social_gen = social_gen
    app.state.video_gen = video_gen

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(projects_router)
    app.include_router(content_router)
    app.include_router(generator_router)
    app.include_router(export_router)
    app.include_router(analytics_router)

    @app.get("/", tags=["Health"])
    async def root():
        return {
            "name": "AI Content Studio",
            "version": "1.0.0",
            "status": "online",
            "environment": app_settings.app_env,
        }

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "healthy", "database": "connected"}

    return app
