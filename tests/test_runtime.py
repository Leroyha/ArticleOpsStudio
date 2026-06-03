import os
import sys

from articleops_studio.database import get_database_path
from articleops_studio.runtime import (
    configure_runtime_environment,
    ensure_runtime_layout,
    get_application_base_dir,
    get_resource_base_dir,
)


def test_runtime_layout_uses_env_directory(tmp_path, monkeypatch) -> None:
    runtime_root = tmp_path / "runtime-home"
    monkeypatch.setenv("ARTICLEOPS_RUNTIME_DIR", str(runtime_root))

    layout = ensure_runtime_layout()

    assert layout.root == runtime_root
    assert get_database_path() == runtime_root / "data" / "articleops.sqlite"
    assert layout.data.is_dir()
    assert layout.logs.is_dir()
    assert layout.cache.is_dir()
    assert layout.temp.is_dir()
    assert layout.exports.is_dir()
    assert layout.evidence.is_dir()
    assert layout.backups.is_dir()
    assert layout.docs.is_dir()


def test_runtime_environment_redirects_temp_and_cache(tmp_path, monkeypatch) -> None:
    runtime_root = tmp_path / "packaged-runtime"
    monkeypatch.delenv("ARTICLEOPS_RUNTIME_DIR", raising=False)
    monkeypatch.delenv("UV_CACHE_DIR", raising=False)
    monkeypatch.delenv("PYTHONPYCACHEPREFIX", raising=False)

    layout = configure_runtime_environment(runtime_root)

    assert layout.root == runtime_root
    assert get_database_path() == runtime_root / "data" / "articleops.sqlite"
    assert os.environ["TEMP"] == str(layout.temp)
    assert os.environ["TMP"] == str(layout.temp)
    assert os.environ["TMPDIR"] == str(layout.temp)
    assert os.environ["XDG_CACHE_HOME"] == str(layout.cache)
    assert os.environ["UV_CACHE_DIR"] == str(layout.cache / "uv")
    assert os.environ["PYTHONPYCACHEPREFIX"] == str(layout.cache / "pycache")
    assert layout.cache.is_dir()


def test_packaged_resource_dir_uses_pyinstaller_meipass(tmp_path, monkeypatch) -> None:
    executable_dir = tmp_path / "ArticleOpsStudio"
    resource_dir = executable_dir / "_internal"
    executable = executable_dir / "ArticleOpsStudio.exe"
    resource_dir.mkdir(parents=True)
    executable.touch()

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(resource_dir), raising=False)
    monkeypatch.setattr(sys, "executable", str(executable))

    assert get_application_base_dir() == executable_dir
    assert get_resource_base_dir() == resource_dir
