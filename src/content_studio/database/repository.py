"""Async SQLite database repository for AI Content Studio."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
import aiosqlite

from content_studio.models.project import Project, ProjectCreate, ProjectUpdate
from content_studio.models.content import (
    ContentType,
    ContentStatus,
    Tone,
    ContentItem,
    ContentItemCreate,
    ContentItemUpdate,
    ContentRevision,
)

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def count_words(text: str) -> int:
    return len(text.split()) if text else 0


class ContentStudioRepository:
    """Async repository for projects, content items, revisions, and analytics."""

    def __init__(self, db_path: Path):
        self.db_path = str(db_path)

    async def init_db(self) -> None:
        """Initialize database schema."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS content_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    body TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    status TEXT DEFAULT 'draft',
                    tone TEXT DEFAULT 'professional',
                    tags_json TEXT DEFAULT '[]',
                    word_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                );
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS content_revisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id INTEGER NOT NULL,
                    revision_number INTEGER NOT NULL,
                    body TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (content_id) REFERENCES content_items(id) ON DELETE CASCADE
                );
            """)

            await db.commit()
            logger.info("AI Content Studio database schema initialized.")

    # Project Operations
    async def create_project(self, payload: ProjectCreate) -> Project:
        async with aiosqlite.connect(self.db_path) as db:
            now_iso = utc_now().isoformat()
            cursor = await db.execute(
                "INSERT INTO projects (name, description, created_at) VALUES (?, ?, ?)",
                (payload.name, payload.description or "", now_iso),
            )
            await db.commit()
            return Project(
                id=cursor.lastrowid,
                name=payload.name,
                description=payload.description or "",
                created_at=utc_now(),
            )

    async def get_projects(self) -> List[Project]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT id, name, description, created_at FROM projects ORDER BY id DESC") as cursor:
                rows = await cursor.fetchall()
                return [
                    Project(
                        id=r[0],
                        name=r[1],
                        description=r[2] or "",
                        created_at=datetime.fromisoformat(r[3]) if isinstance(r[3], str) else r[3],
                    )
                    for r in rows
                ]

    async def get_project(self, project_id: int) -> Optional[Project]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, name, description, created_at FROM projects WHERE id = ?",
                (project_id,),
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                return Project(
                    id=row[0],
                    name=row[1],
                    description=row[2] or "",
                    created_at=datetime.fromisoformat(row[3]) if isinstance(row[3], str) else row[3],
                )

    async def update_project(self, project_id: int, payload: ProjectUpdate) -> Optional[Project]:
        existing = await self.get_project(project_id)
        if not existing:
            return None
        new_name = payload.name if payload.name is not None else existing.name
        new_desc = payload.description if payload.description is not None else existing.description

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE projects SET name = ?, description = ? WHERE id = ?",
                (new_name, new_desc, project_id),
            )
            await db.commit()
        return await self.get_project(project_id)

    async def delete_project(self, project_id: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            await db.commit()
            return cursor.rowcount > 0

    # Content Operations
    async def create_content_item(self, payload: ContentItemCreate) -> ContentItem:
        now_iso = utc_now().isoformat()
        words = count_words(payload.body)
        tags_raw = json.dumps(payload.tags)

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO content_items (
                    project_id, title, body, content_type, status, tone, tags_json, word_count, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.project_id,
                    payload.title,
                    payload.body,
                    payload.content_type.value,
                    ContentStatus.DRAFT.value,
                    payload.tone.value,
                    tags_raw,
                    words,
                    now_iso,
                    now_iso,
                ),
            )
            item_id = cursor.lastrowid

            # Create initial revision
            await db.execute(
                """
                INSERT INTO content_revisions (content_id, revision_number, body, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (item_id, 1, payload.body, now_iso),
            )
            await db.commit()

            return ContentItem(
                id=item_id,
                project_id=payload.project_id,
                title=payload.title,
                body=payload.body,
                content_type=payload.content_type,
                status=ContentStatus.DRAFT,
                tone=payload.tone,
                tags=payload.tags,
                word_count=words,
                created_at=utc_now(),
                updated_at=utc_now(),
            )

    async def get_content_items(
        self,
        project_id: Optional[int] = None,
        content_type: Optional[ContentType] = None,
        status: Optional[ContentStatus] = None,
        search: Optional[str] = None,
    ) -> List[ContentItem]:
        query = (
            "SELECT id, project_id, title, body, content_type, status, tone, tags_json, word_count, created_at, updated_at "
            "FROM content_items WHERE 1=1"
        )
        params = []

        if project_id is not None:
            query += " AND project_id = ?"
            params.append(project_id)
        if content_type is not None:
            query += " AND content_type = ?"
            params.append(content_type.value)
        if status is not None:
            query += " AND status = ?"
            params.append(status.value)
        if search:
            query += " AND (title LIKE ? OR body LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term])

        query += " ORDER BY id DESC"

        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                results = []
                for r in rows:
                    raw_tags = json.loads(r[7]) if r[7] else []
                    results.append(
                        ContentItem(
                            id=r[0],
                            project_id=r[1],
                            title=r[2],
                            body=r[3],
                            content_type=ContentType(r[4]),
                            status=ContentStatus(r[5]),
                            tone=Tone(r[6]),
                            tags=raw_tags,
                            word_count=r[8],
                            created_at=datetime.fromisoformat(r[9]) if isinstance(r[9], str) else r[9],
                            updated_at=datetime.fromisoformat(r[10]) if isinstance(r[10], str) else r[10],
                        )
                    )
                return results

    async def get_content_item(self, item_id: int) -> Optional[ContentItem]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT id, project_id, title, body, content_type, status, tone, tags_json, word_count, created_at, updated_at
                FROM content_items WHERE id = ?
                """,
                (item_id,),
            ) as cursor:
                r = await cursor.fetchone()
                if not r:
                    return None
                raw_tags = json.loads(r[7]) if r[7] else []
                return ContentItem(
                    id=r[0],
                    project_id=r[1],
                    title=r[2],
                    body=r[3],
                    content_type=ContentType(r[4]),
                    status=ContentStatus(r[5]),
                    tone=Tone(r[6]),
                    tags=raw_tags,
                    word_count=r[8],
                    created_at=datetime.fromisoformat(r[9]) if isinstance(r[9], str) else r[9],
                    updated_at=datetime.fromisoformat(r[10]) if isinstance(r[10], str) else r[10],
                )

    async def update_content_item(self, item_id: int, payload: ContentItemUpdate) -> Optional[ContentItem]:
        existing = await self.get_content_item(item_id)
        if not existing:
            return None

        new_title = payload.title if payload.title is not None else existing.title
        new_body = payload.body if payload.body is not None else existing.body
        new_type = payload.content_type.value if payload.content_type is not None else existing.content_type.value
        new_status = payload.status.value if payload.status is not None else existing.status.value
        new_tone = payload.tone.value if payload.tone is not None else existing.tone.value
        new_tags = payload.tags if payload.tags is not None else existing.tags
        new_words = count_words(new_body)
        now_iso = utc_now().isoformat()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                UPDATE content_items
                SET title = ?, body = ?, content_type = ?, status = ?, tone = ?, tags_json = ?, word_count = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    new_title,
                    new_body,
                    new_type,
                    new_status,
                    new_tone,
                    json.dumps(new_tags),
                    new_words,
                    now_iso,
                    item_id,
                ),
            )

            # If body changed, store new revision
            if payload.body is not None and payload.body != existing.body:
                cursor = await db.execute(
                    "SELECT MAX(revision_number) FROM content_revisions WHERE content_id = ?",
                    (item_id,),
                )
                curr_rev = (await cursor.fetchone())[0] or 1
                await db.execute(
                    """
                    INSERT INTO content_revisions (content_id, revision_number, body, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (item_id, curr_rev + 1, new_body, now_iso),
                )

            await db.commit()

        return await self.get_content_item(item_id)

    async def delete_content_item(self, item_id: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM content_items WHERE id = ?", (item_id,))
            await db.commit()
            return cursor.rowcount > 0

    # Revision Operations
    async def get_revisions(self, content_id: int) -> List[ContentRevision]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, content_id, revision_number, body, created_at FROM content_revisions WHERE content_id = ? ORDER BY revision_number ASC",
                (content_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    ContentRevision(
                        id=r[0],
                        content_id=r[1],
                        revision_number=r[2],
                        body=r[3],
                        created_at=datetime.fromisoformat(r[4]) if isinstance(r[4], str) else r[4],
                    )
                    for r in rows
                ]

    # Analytics Operations
    async def get_analytics_summary(self, project_id: Optional[int] = None) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            base_where = " WHERE 1=1"
            params = []
            if project_id is not None:
                base_where += " AND project_id = ?"
                params.append(project_id)

            # Total items & words
            cursor = await db.execute(
                f"SELECT COUNT(*), COALESCE(SUM(word_count), 0) FROM content_items{base_where}",
                params,
            )
            r = await cursor.fetchone()
            total_items = r[0]
            total_words = r[1]

            # By status
            status_counts = {}
            for st in ContentStatus:
                st_params = list(params) + [st.value]
                cursor = await db.execute(
                    f"SELECT COUNT(*) FROM content_items{base_where} AND status = ?",
                    st_params,
                )
                status_counts[st.value] = (await cursor.fetchone())[0]

            # By channel
            channel_counts = {}
            for ct in ContentType:
                ct_params = list(params) + [ct.value]
                cursor = await db.execute(
                    f"SELECT COUNT(*) FROM content_items{base_where} AND content_type = ?",
                    ct_params,
                )
                channel_counts[ct.value] = (await cursor.fetchone())[0]

            return {
                "project_id": project_id,
                "total_items": total_items,
                "total_words": total_words,
                "status_distribution": status_counts,
                "channel_distribution": channel_counts,
            }
