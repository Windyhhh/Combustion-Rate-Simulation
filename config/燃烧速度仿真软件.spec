# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['../src/gui/Gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../assets/images/logo1.png', '.'),
        ('../assets/images/logo2.jpg', '.'),
        ('../assets/resources', 'resources'),
        ('../assets/libs', 'libs'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'PIL',
        'PIL._tkinter_finder',
        'cantera',
        'numpy',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'tksheet',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='燃烧速度仿真软件',
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

