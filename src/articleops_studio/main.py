from __future__ import annotations

import logging
import sys

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from . import __version__
from .api import router
from .database import init_database
from .runtime import configure_runtime_environment, get_resource_base_dir


logger = logging.getLogger("articleops_studio")
RESOURCE_DIR = get_resource_base_dir()
FRONTEND_DIST = RESOURCE_DIR / "frontend" / "dist"
FRONTEND_PUBLIC = RESOURCE_DIR / "frontend" / "public"


def error_response(message: str, status_code: int) -> JSONResponse:
    return JSONResponse({"success": False, "error": message}, status_code=status_code)


def create_app() -> FastAPI:
    runtime_layout = configure_runtime_environment()
    logging.basicConfig(
        filename=str(runtime_layout.logs / "articleops.log"),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    init_database()
    app = FastAPI(
        title="ArticleOps Studio",
        summary="OpenClaw 通用定时发文任务模板生成与产品使用统计工具。",
        version=__version__,
    )
    app.include_router(router)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        first_error = exc.errors()[0]
        location = " -> ".join(str(part) for part in first_error.get("loc", []) if part != "body")
        message = first_error.get("msg", "请求参数不合法。")
        if location:
            message = f"{location}: {message}"
        return error_response(message, 422)

    @app.exception_handler(ValueError)
    async def handle_value_error(_: Request, exc: ValueError) -> JSONResponse:
        return error_response(str(exc), 400)

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled server error", exc_info=exc)
        return error_response("服务器内部错误，请稍后重试。", 500)

    if FRONTEND_DIST.exists():
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/favicon.svg", include_in_schema=False)
    async def favicon() -> Response:
        favicon_path = FRONTEND_PUBLIC / "favicon.svg"
        if favicon_path.exists():
            return FileResponse(favicon_path, media_type="image/svg+xml")
        return Response(content=b"", media_type="image/svg+xml")

    @app.get("/{path:path}", include_in_schema=False)
    async def spa(_: Request, path: str = "") -> Response:
        index_path = FRONTEND_DIST / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return Response("ArticleOps Studio frontend has not been built.", media_type="text/plain")

    return app


app = create_app()


def run() -> None:
    uvicorn_options = {
        "host": "127.0.0.1",
        "port": 8000,
        "reload": False,
    }
    if getattr(sys, "frozen", False):
        uvicorn_options.update({"access_log": False, "log_config": None})
    uvicorn.run("articleops_studio.main:app", **uvicorn_options)


if __name__ == "__main__":
    run()
