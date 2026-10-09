"""Server runner entrypoint for AI Content Studio."""

import uvicorn
from content_studio.config import get_settings


def start():
    """Launch Uvicorn server with application factory."""
    settings = get_settings()
    uvicorn.run(
        "content_studio.app:create_app",
        factory=True,
        host=settings.host,
        port=settings.port,
        reload=settings.app_env == "development",
        log_level=settings.log_level.lower(),
    )


main = start


if __name__ == "__main__":
    start()
