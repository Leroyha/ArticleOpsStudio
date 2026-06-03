from __future__ import annotations

from datetime import datetime, time

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


SupportedLocale = Literal["zh-CN", "zh-TW", "ja-JP", "ko-KR", "en-US", "fr-FR", "it-IT"]


class GenerateRequest(BaseModel):
    start_time: time
    end_time: time
    task_count: int = Field(..., gt=0, le=50, description="任务数量")
    interval_min: int = Field(..., gt=0, le=720, description="最小间隔，单位分钟")
    products: list[str] = Field(..., min_length=1, description="产品名称列表")
    manual_times: list[str] | None = Field(default=None, description="可选手动时间列表")
    locale: SupportedLocale = Field(default="zh-CN", description="模板语言")

    @field_validator("products")
    @classmethod
    def validate_products(cls, values: list[str]) -> list[str]:
        cleaned = [value.strip() for value in values]
        if any(not value for value in cleaned):
            raise ValueError("产品名称不能为空。")
        return cleaned


class ScheduleItemResponse(BaseModel):
    index: int
    time: str
    product: str


class GenerateResponse(BaseModel):
    success: bool
    text: str
    items: list[ScheduleItemResponse]
    template_name: str
    template_version: str
    template_hash: str
    locale: SupportedLocale = "zh-CN"


class SaveScheduleRequest(GenerateRequest):
    batch_name: str | None = Field(default=None, max_length=160)
    rendered_text: str = Field(..., min_length=1)


class SaveScheduleResponse(BaseModel):
    success: bool
    batch_id: int
    item_count: int


class ProductStat(BaseModel):
    product_name: str
    usage_count: int
    first_used_at: datetime | None
    last_used_at: datetime | None


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    database_path: str
    database_ready: bool


class TemplateResponse(BaseModel):
    name: str
    version: str
    hash: str
    content: str
    locale: SupportedLocale = "zh-CN"
    available_locales: list[str] = Field(default_factory=list)


class AdminWriteRequest(BaseModel):
    values: dict[str, Any] = Field(default_factory=dict)
    confirm: str | None = None
