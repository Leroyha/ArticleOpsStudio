from __future__ import annotations

from pathlib import Path
from typing import Any

from .runtime import ensure_runtime_layout, get_application_base_dir, get_resource_base_dir


DOC_EXTENSIONS = {".md", ".txt"}


def _candidate_roots() -> list[Path]:
    roots = [get_resource_base_dir(), get_application_base_dir(), ensure_runtime_layout().docs, Path.cwd()]
    unique_roots: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        resolved = root.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique_roots.append(resolved)
    return unique_roots


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _safe_slug(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def list_documents() -> list[dict[str, Any]]:
    seen: set[str] = set()
    docs: list[dict[str, Any]] = []
    for root in _candidate_roots():
        candidates = []
        readme = root / "README.md"
        if readme.exists():
            candidates.append(readme)
        docs_dir = root / "docs"
        if docs_dir.exists():
            candidates.extend(
                path
                for path in sorted(docs_dir.iterdir())
                if path.is_file() and path.suffix.lower() in DOC_EXTENSIONS
            )
        for path in candidates:
            slug = _safe_slug(path, root)
            if slug in seen:
                continue
            seen.add(slug)
            docs.append({"slug": slug, "title": path.stem, "path": str(path)})
    return docs


def read_document(slug: str) -> dict[str, Any]:
    normalized = slug.replace("\\", "/").lstrip("/")
    if ".." in Path(normalized).parts:
        raise ValueError("文档路径不合法。")
    for root in _candidate_roots():
        path = root / normalized
        if path.exists() and path.is_file() and path.suffix.lower() in DOC_EXTENSIONS:
            return {
                "slug": normalized,
                "title": path.stem,
                "content": _read_text(path),
                "path": str(path),
            }
    raise ValueError("未找到文档。")
