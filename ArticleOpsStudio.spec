# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['packaging\\articleops_entry.py'],
    pathex=['src'],
    binaries=[],
    datas=[('frontend/dist', 'frontend/dist'), ('frontend/public', 'frontend/public'), ('README.md', '.'), ('docs', 'docs'), ('assets', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ArticleOpsStudio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='packaging\\windows_version_info.txt',
    icon=['assets\\logo\\articleops-logo.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ArticleOpsStudio',
)
