from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
import shutil
import sqlite3
from typing import Any

from .database import connect, get_database_path, init_database
from .runtime import ensure_runtime_layout


ALLOWED_TABLES = {"template_versions", "schedule_batches", "schedule_items", "product_usage"}
WRITE_CONFIRM_TOKEN = "CONFIRM"


def _quote_identifier(name: str) -> str:
    if name not in ALLOWED_TABLES:
        raise ValueError(f"不允许访问数据库表：{name}")
    return f'"{name}"'


def _table_columns(db: sqlite3.Connection, table: str) -> list[dict[str, Any]]:
    _quote_identifier(table)
    rows = db.execute(f"PRAGMA table_info({_quote_identifier(table)})").fetchall()
    return [
        {
            "name": row["name"],
            "type": row["type"],
            "notnull": bool(row["notnull"]),
            "default": row["dflt_value"],
            "pk": bool(row["pk"]),
        }
        for row in rows
    ]


def _column_names(db: sqlite3.Connection, table: str) -> set[str]:
    return {column["name"] for column in _table_columns(db, table)}


def _writable_values(db: sqlite3.Connection, table: str, values: dict[str, Any]) -> dict[str, Any]:
    columns = _column_names(db, table)
    cleaned = {key: value for key, value in values.items() if key in columns and key != "id"}
    if table == "template_versions" and "content" in cleaned:
        cleaned["content_hash"] = sha256(str(cleaned["content"]).encode("utf-8")).hexdigest()
    return cleaned


def backup_database(reason: str = "manual") -> Path:
    init_database()
    layout = ensure_runtime_layout()
    source = get_database_path()
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S-%f")
    target = layout.backups / f"articleops-{timestamp}-{reason}.sqlite"
    shutil.copy2(source, target)
    return target


def list_tables(db: sqlite3.Connection | None = None) -> list[dict[str, Any]]:
    init_database()
    owns_connection = db is None
    connection = db or sqlite3.connect(get_database_path())
    connection.row_factory = sqlite3.Row
    try:
        result = []
        for table in sorted(ALLOWED_TABLES):
            count = connection.execute(
                f"SELECT COUNT(*) AS count FROM {_quote_identifier(table)}"
            ).fetchone()["count"]
            result.append({"name": table, "count": count, "columns": _table_columns(connection, table)})
        return result
    finally:
        if owns_connection:
            connection.close()


def database_summary() -> dict[str, Any]:
    init_database()
    path = get_database_path()
    return {
        "path": str(path),
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "tables": list_tables(),
        "backup_dir": str(ensure_runtime_layout().backups),
    }


def list_rows(
    table: str,
    *,
    page: int = 1,
    page_size: int = 50,
    search: str = "",
    sort_by: str = "id",
    sort_dir: str = "desc",
) -> dict[str, Any]:
    init_database()
    page = max(1, page)
    page_size = min(max(1, page_size), 200)
    offset = (page - 1) * page_size
    direction = "ASC" if sort_dir.lower() == "asc" else "DESC"
    with connect() as db:
        columns = _column_names(db, table)
        if sort_by not in columns:
            sort_by = "id" if "id" in columns else sorted(columns)[0]
        where_sql = ""
        params: list[Any] = []
        if search:
            text_columns = [
                column["name"]
                for column in _table_columns(db, table)
                if "TEXT" in str(column["type"]).upper()
            ]
            if text_columns:
                where_sql = " WHERE " + " OR ".join(f'"{column}" LIKE ?' for column in text_columns)
                params.extend([f"%{search}%"] * len(text_columns))
        quoted_table = _quote_identifier(table)
        total = db.execute(f"SELECT COUNT(*) AS count FROM {quoted_table}{where_sql}", params).fetchone()["count"]
        rows = db.execute(
            f'SELECT * FROM {quoted_table}{where_sql} ORDER BY "{sort_by}" {direction} LIMIT ? OFFSET ?',
            [*params, page_size, offset],
        ).fetchall()
        return {
            "table": table,
            "page": page,
            "page_size": page_size,
            "total": total,
            "rows": [dict(row) for row in rows],
            "columns": _table_columns(db, table),
        }


def create_row(table: str, values: dict[str, Any]) -> int:
    init_database()
    backup_database("before-insert")
    with connect() as db:
        cleaned = _writable_values(db, table, values)
        if not cleaned:
            raise ValueError("没有可写入的字段。")
        columns = list(cleaned)
        placeholders = ", ".join("?" for _ in columns)
        names = ", ".join(f'"{column}"' for column in columns)
        cursor = db.execute(
            f"INSERT INTO {_quote_identifier(table)} ({names}) VALUES ({placeholders})",
            [cleaned[column] for column in columns],
        )
        db.commit()
        return int(cursor.lastrowid)


def update_row(table: str, row_id: int, values: dict[str, Any]) -> None:
    init_database()
    backup_database("before-update")
    with connect() as db:
        cleaned = _writable_values(db, table, values)
        if not cleaned:
            raise ValueError("没有可更新的字段。")
        assignments = ", ".join(f'"{column}" = ?' for column in cleaned)
        cursor = db.execute(
            f"UPDATE {_quote_identifier(table)} SET {assignments} WHERE id = ?",
            [*cleaned.values(), row_id],
        )
        if cursor.rowcount == 0:
            raise ValueError("未找到要更新的记录。")
        db.commit()


def delete_row(table: str, row_id: int) -> None:
    init_database()
    backup_database("before-delete")
    with connect() as db:
        cursor = db.execute(f"DELETE FROM {_quote_identifier(table)} WHERE id = ?", (row_id,))
        if cursor.rowcount == 0:
            raise ValueError("未找到要删除的记录。")
        db.commit()
