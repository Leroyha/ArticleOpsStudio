from __future__ import annotations

from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
import sqlite3
from typing import Iterator

from .scheduler import ScheduleItem
from .templates import CURRENT_TEMPLATE_NAME, CURRENT_TEMPLATE_VERSION, current_template_hash
from .runtime import runtime_file


DEFAULT_DB_RELATIVE_PATH = ("data", "articleops.sqlite")


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS template_versions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  version TEXT NOT NULL,
  content_hash TEXT NOT NULL UNIQUE,
  content TEXT NOT NULL,
  created_at TEXT NOT NULL,
  is_active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS schedule_batches (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  batch_name TEXT,
  task_count INTEGER NOT NULL,
  start_time TEXT NOT NULL,
  end_time TEXT NOT NULL,
  interval_min INTEGER NOT NULL,
  rendered_text TEXT NOT NULL,
  template_locale TEXT NOT NULL DEFAULT 'zh-CN',
  template_hash TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS schedule_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  batch_id INTEGER NOT NULL,
  position INTEGER NOT NULL,
  scheduled_time TEXT NOT NULL,
  product_name TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(batch_id) REFERENCES schedule_batches(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS product_usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_name TEXT NOT NULL UNIQUE,
  usage_count INTEGER NOT NULL DEFAULT 0,
  first_used_at TEXT NOT NULL,
  last_used_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_schedule_batches_created_at ON schedule_batches(created_at);
CREATE INDEX IF NOT EXISTS idx_schedule_items_product_name ON schedule_items(product_name);
CREATE INDEX IF NOT EXISTS idx_schedule_items_scheduled_time ON schedule_items(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_product_usage_last_used_at ON product_usage(last_used_at);
"""


def utc_now_text() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def get_database_path() -> Path:
    return runtime_file(*DEFAULT_DB_RELATIVE_PATH)


@contextmanager
def connect(db_path: Path | None = None) -> Iterator[sqlite3.Connection]:
    path = db_path or get_database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
    finally:
        connection.close()


def init_database(db_path: Path | None = None, template_content: str | None = None) -> None:
    from .templates import TEMPLATE_BODY

    with connect(db_path) as db:
        db.executescript(SCHEMA_SQL)
        _ensure_schedule_batch_columns(db)
        content = template_content or TEMPLATE_BODY
        content_hash = current_template_hash()
        db.execute(
            "UPDATE template_versions SET is_active = 0 WHERE content_hash <> ?",
            (content_hash,),
        )
        db.execute(
            """
            INSERT INTO template_versions
              (name, version, content_hash, content, created_at, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
            ON CONFLICT(content_hash) DO UPDATE SET
              name = excluded.name,
              version = excluded.version,
              content = excluded.content,
              is_active = 1
            """,
            (
                CURRENT_TEMPLATE_NAME,
                CURRENT_TEMPLATE_VERSION,
                content_hash,
                content,
                utc_now_text(),
            ),
        )
        db.commit()


def _ensure_schedule_batch_columns(db: sqlite3.Connection) -> None:
    columns = {
        str(row["name"])
        for row in db.execute("PRAGMA table_info(schedule_batches)").fetchall()
    }
    if "template_locale" not in columns:
        db.execute("ALTER TABLE schedule_batches ADD COLUMN template_locale TEXT NOT NULL DEFAULT 'zh-CN'")


def save_schedule_batch(
    *,
    items: list[ScheduleItem],
    start_time: str,
    end_time: str,
    interval_min: int,
    rendered_text: str,
    batch_name: str | None = None,
    template_locale: str = "zh-CN",
    template_hash: str | None = None,
    db_path: Path | None = None,
) -> int:
    now = utc_now_text()
    with connect(db_path) as db:
        cursor = db.execute(
            """
            INSERT INTO schedule_batches
              (batch_name, task_count, start_time, end_time, interval_min, rendered_text,
               template_locale, template_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                batch_name,
                len(items),
                start_time,
                end_time,
                interval_min,
                rendered_text,
                template_locale,
                template_hash or current_template_hash(template_locale),
                now,
            ),
        )
        batch_id = int(cursor.lastrowid)
        db.executemany(
            """
            INSERT INTO schedule_items
              (batch_id, position, scheduled_time, product_name, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            [(batch_id, item.index, item.time_text, item.product_name, now) for item in items],
        )
        for item in items:
            db.execute(
                """
                INSERT INTO product_usage (product_name, usage_count, first_used_at, last_used_at)
                VALUES (?, 1, ?, ?)
                ON CONFLICT(product_name) DO UPDATE SET
                  usage_count = usage_count + 1,
                  last_used_at = excluded.last_used_at
                """,
                (item.product_name, now, now),
            )
        db.commit()
        return batch_id


def list_product_stats(limit: int = 100, db_path: Path | None = None) -> list[sqlite3.Row]:
    with connect(db_path) as db:
        return list(
            db.execute(
                """
                SELECT product_name, usage_count, first_used_at, last_used_at
                FROM product_usage
                ORDER BY usage_count DESC, last_used_at DESC
                LIMIT ?
                """,
                (limit,),
            )
        )


def list_recent_products(limit: int = 20, db_path: Path | None = None) -> list[str]:
    with connect(db_path) as db:
        rows = db.execute(
            """
            SELECT product_name
            FROM product_usage
            ORDER BY last_used_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [str(row["product_name"]) for row in rows]
