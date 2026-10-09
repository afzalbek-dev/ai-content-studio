"""API routers for AI Content Studio."""

from content_studio.api.routes_projects import router as projects_router
from content_studio.api.routes_content import router as content_router
from content_studio.api.routes_generator import router as generator_router
from content_studio.api.routes_export import router as export_router
from content_studio.api.routes_analytics import router as analytics_router

__all__ = [
    "projects_router",
    "content_router",
    "generator_router",
    "export_router",
    "analytics_router",
]
