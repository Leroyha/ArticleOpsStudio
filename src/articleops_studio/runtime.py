from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ENV_VAR = "ARTICLEOPS_RUNTIME_DIR"
RUNTIME_DIR_NAME = "articleops-runtime"


@dataclass(frozen=True)
class RuntimeLayout:
    root: Path
    data: Path
    logs: Path
    cache: Path
    temp: Path
    exports: Path
    evidence: Path
    backups: Path
    docs: Path


def get_application_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return APP_ROOT


def get_resource_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        bundle_dir = getattr(sys, "_MEIPASS", None)
        if bundle_dir:
            return Path(bundle_dir).resolve()
        return get_application_base_dir()
    return APP_ROOT


def get_runtime_root() -> Path:
    configured = os.environ.get(RUNTIME_ENV_VAR)
    if configured:
        return Path(configured).expanduser().resolve()
    return get_application_base_dir() / RUNTIME_DIR_NAME


def get_runtime_layout(root: Path | None = None) -> RuntimeLayout:
    runtime_root = (root or get_runtime_root()).resolve()
    return RuntimeLayout(
        root=runtime_root,
        data=runtime_root / "data",
        logs=runtime_root / "logs",
        cache=runtime_root / "cache",
        temp=runtime_root / "temp",
        exports=runtime_root / "exports",
        evidence=runtime_root / "evidence",
        backups=runtime_root / "backups",
        docs=runtime_root / "docs",
    )


def ensure_runtime_layout(root: Path | None = None) -> RuntimeLayout:
    layout = get_runtime_layout(root)
    for directory in (
        layout.root,
        layout.data,
        layout.logs,
        layout.cache,
        layout.temp,
        layout.exports,
        layout.evidence,
        layout.backups,
        layout.docs,
    ):
        directory.mkdir(parents=True, exist_ok=True)
    return layout


def runtime_file(*parts: str) -> Path:
    return get_runtime_root().joinpath(*parts)


def configure_runtime_environment(root: Path | None = None) -> RuntimeLayout:
    layout = ensure_runtime_layout(root)
    os.environ[RUNTIME_ENV_VAR] = str(layout.root)
    os.environ["TEMP"] = str(layout.temp)
    os.environ["TMP"] = str(layout.temp)
    os.environ["TMPDIR"] = str(layout.temp)
    os.environ["XDG_CACHE_HOME"] = str(layout.cache)
    os.environ.setdefault("PYTHONPYCACHEPREFIX", str(layout.cache / "pycache"))
    os.environ.setdefault("UV_CACHE_DIR", str(layout.cache / "uv"))
    return layout
