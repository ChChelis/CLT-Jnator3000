# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\PROJETOS PYTHON\\clt_jnator_qt.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\PROJETOS PYTHON\\assets\\fa-solid-900.ttf', 'assets'), ('D:\\PROJETOS PYTHON\\assets\\Manrope-Variable.ttf', 'assets'), ('D:\\PROJETOS PYTHON\\assets\\app_icon_current.ico', 'assets')],
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
    name='CLT-Jnator 3000',
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
    icon=['D:\\PROJETOS PYTHON\\assets\\app_icon_current.ico'],
)
