from fastapi.testclient import TestClient

from articleops_studio.main import app


client = TestClient(app)
FORBIDDEN_SITE_TOKEN = "chem" + "17"


def test_home_page_loads() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "ArticleOps Studio" in response.text or "frontend has not been built" in response.text


def test_favicon_route_exists() -> None:
    response = client.get("/favicon.svg")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")


def test_generate_success() -> None:
    response = client.post(
        "/api/schedules/generate",
        json={
            "start_time": "10:00",
            "end_time": "11:15",
            "task_count": 4,
            "interval_min": 15,
            "products": ["A", "B", "C", "D"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert len(payload["items"]) == 4
    assert "任务：发布一篇文章" in payload["text"]
    assert FORBIDDEN_SITE_TOKEN not in payload["text"].lower()
    assert payload["template_name"] == "openclaw-scheduled-article-publish"


def test_generate_rejects_invalid_time() -> None:
    response = client.post(
        "/api/schedules/generate",
        json={
            "start_time": "12:99",
            "end_time": "13:30",
            "task_count": 1,
            "interval_min": 10,
            "products": ["A"],
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["success"] is False
    assert "start_time" in payload["error"]


def test_generate_rejects_tight_schedule() -> None:
    response = client.post(
        "/api/schedules/generate",
        json={
            "start_time": "10:00",
            "end_time": "10:10",
            "task_count": 3,
            "interval_min": 10,
            "products": ["A", "B", "C"],
        },
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["success"] is False
    assert "时间范围不足" in payload["error"]


def test_template_current() -> None:
    response = client.get("/api/templates/current")

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "openclaw-scheduled-article-publish"
    assert FORBIDDEN_SITE_TOKEN not in payload["content"].lower()
    assert "账号与页面上下文" in payload["content"]


def test_template_current_uses_locale() -> None:
    response = client.get("/api/templates/current?locale=en-US")

    assert response.status_code == 200
    payload = response.json()
    assert payload["locale"] == "en-US"
    assert "Please set up scheduled article publishing tasks" in payload["content"]
    assert FORBIDDEN_SITE_TOKEN not in payload["content"].lower()
    assert "it-IT" in payload["available_locales"]


def test_docs_index_loads_readme() -> None:
    response = client.get("/api/docs")

    assert response.status_code == 200
    payload = response.json()
    assert any(item["slug"] == "README.md" for item in payload["documents"])


def test_database_admin_summary_lists_tables() -> None:
    response = client.get("/api/admin/database/summary")

    assert response.status_code == 200
    payload = response.json()
    assert any(item["name"] == "schedule_batches" for item in payload["tables"])
