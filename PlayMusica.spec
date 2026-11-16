# -*- mode: python ; coding: utf-8 -*-

import importlib.util

if importlib.util.find_spec('PySide6') is None:
    raise RuntimeError(
        'PySide6 is not installed in the Python environment used by PyInstaller. '
        'Run "python -m pip install -r requirements.txt" with the same Python '
        'used to build the executable.'
    )

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
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
    a.binaries,
    a.datas,
    [],
    name='PlayMusica',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
