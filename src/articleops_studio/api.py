from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter

from . import __version__
from .database_admin import (
    WRITE_CONFIRM_TOKEN,
    create_row,
    database_summary,
    delete_row,
    list_rows,
    list_tables,
    update_row,
)
from .docs_reader import list_documents, read_document
from .database import (
    get_database_path,
    init_database,
    list_product_stats,
    list_recent_products,
    save_schedule_batch,
)
from .models import (
    GenerateRequest,
    GenerateResponse,
    AdminWriteRequest,
    HealthResponse,
    ProductStat,
    SaveScheduleRequest,
    SaveScheduleResponse,
    ScheduleItemResponse,
    TemplateResponse,
)
from .scheduler import build_schedule_items
from .templates import (
    CURRENT_TEMPLATE_NAME,
    CURRENT_TEMPLATE_VERSION,
    current_template_hash,
    get_template_body,
    render_schedule_text,
    SUPPORTED_LOCALES,
)


router = APIRouter(prefix="/api")


def _generate(data: GenerateRequest) -> tuple[list, str]:
    items = build_schedule_items(
        start_time=data.start_time,
        end_time=data.end_time,
        task_count=data.task_count,
        min_interval=data.interval_min,
        products=data.products,
        manual_times=data.manual_times,
    )
    return items, render_schedule_text(items, locale=data.locale)


def _serialize_items(items: list) -> list[ScheduleItemResponse]:
    return [
        ScheduleItemResponse(index=item.index, time=item.time_text, product=item.product_name)
        for item in items
    ]


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    db_path = get_database_path()
    init_database(db_path)
    return HealthResponse(
        status="ok",
        app_name="ArticleOps Studio",
        version=__version__,
        database_path=str(db_path),
        database_ready=Path(db_path).exists(),
    )


@router.get("/i18n/locales")
def locales() -> dict:
    return {
        "default": "zh-CN",
        "locales": [
            {"code": "zh-CN", "label": "简体中文"},
            {"code": "zh-TW", "label": "繁體中文"},
            {"code": "ja-JP", "label": "日本語"},
            {"code": "ko-KR", "label": "한국어"},
            {"code": "en-US", "label": "English"},
            {"code": "fr-FR", "label": "Français"},
            {"code": "it-IT", "label": "Italiano"},
        ],
    }


@router.get("/docs")
def docs_index() -> dict:
    return {"documents": list_documents()}


@router.get("/docs/{slug:path}")
def docs_detail(slug: str) -> dict:
    return read_document(slug)


@router.get("/admin/database/summary")
def admin_database_summary() -> dict:
    return database_summary()


@router.get("/admin/database/tables")
def admin_database_tables() -> dict:
    return {"tables": list_tables()}


@router.get("/admin/database/tables/{table}/rows")
def admin_database_rows(
    table: str,
    page: int = 1,
    page_size: int = 50,
    search: str = "",
    sort_by: str = "id",
    sort_dir: str = "desc",
) -> dict:
    return list_rows(
        table,
        page=page,
        page_size=page_size,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


def _require_confirm(payload: AdminWriteRequest) -> None:
    if payload.confirm != WRITE_CONFIRM_TOKEN:
        raise ValueError(f"数据库写操作需要 confirm={WRITE_CONFIRM_TOKEN}")


@router.post("/admin/database/tables/{table}/rows")
def admin_create_row(table: str, payload: AdminWriteRequest) -> dict:
    _require_confirm(payload)
    row_id = create_row(table, payload.values)
    return {"success": True, "id": row_id}


@router.patch("/admin/database/tables/{table}/rows/{row_id}")
def admin_update_row(table: str, row_id: int, payload: AdminWriteRequest) -> dict:
    _require_confirm(payload)
    update_row(table, row_id, payload.values)
    return {"success": True}


@router.delete("/admin/database/tables/{table}/rows/{row_id}")
def admin_delete_row(table: str, row_id: int, confirm: str = "") -> dict:
    if confirm != WRITE_CONFIRM_TOKEN:
        raise ValueError(f"数据库删除操作需要 confirm={WRITE_CONFIRM_TOKEN}")
    delete_row(table, row_id)
    return {"success": True}


@router.post("/schedules/generate", response_model=GenerateResponse)
def generate_schedule(data: GenerateRequest) -> GenerateResponse:
    items, text = _generate(data)
    return GenerateResponse(
        success=True,
        text=text,
        items=_serialize_items(items),
        template_name=CURRENT_TEMPLATE_NAME,
        template_version=CURRENT_TEMPLATE_VERSION,
        template_hash=current_template_hash(data.locale),
        locale=data.locale,
    )


@router.post("/schedules/save", response_model=SaveScheduleResponse)
def save_schedule(data: SaveScheduleRequest) -> SaveScheduleResponse:
    init_database()
    items, _ = _generate(data)
    batch_id = save_schedule_batch(
        items=items,
        start_time=data.start_time.strftime("%H:%M"),
        end_time=data.end_time.strftime("%H:%M"),
        interval_min=data.interval_min,
        rendered_text=data.rendered_text,
        batch_name=data.batch_name,
        template_locale=data.locale,
        template_hash=current_template_hash(data.locale),
    )
    return SaveScheduleResponse(success=True, batch_id=batch_id, item_count=len(items))


@router.get("/products/stats", response_model=list[ProductStat])
def product_stats(limit: int = 100) -> list[ProductStat]:
    init_database()
    return [
        ProductStat(
            product_name=row["product_name"],
            usage_count=row["usage_count"],
            first_used_at=row["first_used_at"],
            last_used_at=row["last_used_at"],
        )
        for row in list_product_stats(limit=limit)
    ]


@router.get("/products/recent", response_model=list[str])
def recent_products(limit: int = 20) -> list[str]:
    init_database()
    return list_recent_products(limit=limit)


@router.get("/templates/current", response_model=TemplateResponse)
def current_template(locale: str = "zh-CN") -> TemplateResponse:
    return TemplateResponse(
        name=CURRENT_TEMPLATE_NAME,
        version=CURRENT_TEMPLATE_VERSION,
        hash=current_template_hash(locale),
        content=get_template_body(locale),
        locale=locale if locale in SUPPORTED_LOCALES else "zh-CN",
        available_locales=list(SUPPORTED_LOCALES),
    )


@router.post("/templates/preview", response_model=GenerateResponse)
def template_preview(data: GenerateRequest) -> GenerateResponse:
    return generate_schedule(data)
