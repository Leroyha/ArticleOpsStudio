from __future__ import annotations

from hashlib import sha256

import pytest

from articleops_studio.database import connect, init_database
from articleops_studio.database_admin import create_row, delete_row, list_rows, update_row
from articleops_studio.templates import CURRENT_TEMPLATE_NAME, TEMPLATE_BODY, current_template_hash


FORBIDDEN_SITE_TOKEN = "chem" + "17"


def prepare_runtime(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("ARTICLEOPS_RUNTIME_DIR", str(tmp_path / "runtime"))
    init_database()


def test_init_database_stores_current_generic_template(tmp_path, monkeypatch) -> None:
    prepare_runtime(tmp_path, monkeypatch)

    with connect() as db:
        row = db.execute(
            "SELECT name, content, content_hash FROM template_versions WHERE is_active = 1"
        ).fetchone()

    assert row["name"] == CURRENT_TEMPLATE_NAME
    assert row["content"] == TEMPLATE_BODY
    assert row["content_hash"] == current_template_hash()
    assert FORBIDDEN_SITE_TOKEN not in row["content"].lower()


def test_init_database_deactivates_stale_active_templates(tmp_path, monkeypatch) -> None:
    prepare_runtime(tmp_path, monkeypatch)
    old_content = "过时的专用模板内容"
    old_hash = sha256(old_content.encode("utf-8")).hexdigest()

    with connect() as db:
        db.execute(
            """
            INSERT INTO template_versions
              (name, version, content_hash, content, created_at, is_active)
            VALUES ('old-template', '2026.01.01', ?, ?, '2026-01-01T00:00:00+00:00', 1)
            """,
            (old_hash, old_content),
        )
        db.commit()

    init_database()

    with connect() as db:
        active_rows = db.execute(
            "SELECT name, content FROM template_versions WHERE is_active = 1"
        ).fetchall()
        stale_row = db.execute(
            "SELECT is_active FROM template_versions WHERE name = 'old-template'"
        ).fetchone()

    assert [(row["name"], row["content"]) for row in active_rows] == [
        (CURRENT_TEMPLATE_NAME, TEMPLATE_BODY)
    ]
    assert stale_row["is_active"] == 0


def test_database_admin_rejects_unknown_table(tmp_path, monkeypatch) -> None:
    prepare_runtime(tmp_path, monkeypatch)

    with pytest.raises(ValueError, match="不允许访问数据库表"):
        list_rows("sqlite_master")


def test_database_admin_rejects_empty_write_payload(tmp_path, monkeypatch) -> None:
    prepare_runtime(tmp_path, monkeypatch)

    with pytest.raises(ValueError, match="没有可写入的字段"):
        create_row("product_usage", {"id": 99, "unknown": "ignored"})


def test_database_admin_rejects_missing_delete_target(tmp_path, monkeypatch) -> None:
    prepare_runtime(tmp_path, monkeypatch)

    with pytest.raises(ValueError, match="未找到要删除的记录"):
        delete_row("product_usage", 999999)


def test_template_content_update_recomputes_hash(tmp_path, monkeypatch) -> None:
    prepare_runtime(tmp_path, monkeypatch)
    content = "新的通用模板内容"

    with connect() as db:
        row_id = db.execute("SELECT id FROM template_versions LIMIT 1").fetchone()["id"]

    update_row("template_versions", row_id, {"content": content})

    with connect() as db:
        row = db.execute(
            "SELECT content, content_hash FROM template_versions WHERE id = ?",
            (row_id,),
        ).fetchone()

    assert row["content"] == content
    assert row["content_hash"] == sha256(content.encode("utf-8")).hexdigest()
