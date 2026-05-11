from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from app.models.task import DownloadTask


class HistoryRepository:
    """历史记录仓库：负责把任务状态写入/读取 SQLite。"""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_schema(self) -> None:
        """初始化表结构；重复调用是安全的。"""
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS history (
                    id TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    status TEXT NOT NULL,
                    progress REAL NOT NULL,
                    speed TEXT,
                    eta TEXT,
                    error TEXT,
                    result_path TEXT,
                    output_dir TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def upsert_task(self, task: DownloadTask) -> None:
        """插入或更新一条任务记录。"""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO history (
                    id, url, status, progress, speed, eta, error, result_path, output_dir, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status=excluded.status,
                    progress=excluded.progress,
                    speed=excluded.speed,
                    eta=excluded.eta,
                    error=excluded.error,
                    result_path=excluded.result_path,
                    updated_at=excluded.updated_at
                """,
                (
                    task.id,
                    task.url,
                    task.status.value,
                    task.progress,
                    task.speed,
                    task.eta,
                    task.error,
                    task.result_path,
                    task.output_dir,
                    task.created_at.isoformat(),
                    task.updated_at.isoformat(),
                ),
            )
            conn.commit()

    def list_history(self, limit: int = 200) -> list[dict[str, Any]]:
        """按更新时间倒序返回历史记录。"""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, url, status, progress, speed, eta, error, result_path, output_dir, created_at, updated_at
                FROM history
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        keys = [
            "id",
            "url",
            "status",
            "progress",
            "speed",
            "eta",
            "error",
            "result_path",
            "output_dir",
            "created_at",
            "updated_at",
        ]
        return [dict(zip(keys, row, strict=False)) for row in rows]
