# -*- mode: python ; coding: utf-8 -*-

# Import necessary modules from PyInstaller
from PyInstaller.utils.hooks import collect_data_files

# Analysis: Define what is included in the package
a = Analysis(
    ['run_app.py'],  # Main script to be executed
    pathex=[],  # Paths to search for imports
    binaries=[],  # Additional binary files
    datas=[
        ('templates', 'templates'),  # Include the 'templates' directory
        ('static', 'static'),  # Include the 'static' directory if needed
    ],
    hiddenimports=[],  # Hidden imports that PyInstaller might miss
    hookspath=[],  # Custom hooks
    hooksconfig={},
    runtime_hooks=[],  # Scripts to be run before the main script
    excludes=[],  # Modules to exclude
    noarchive=False,
    optimize=0,
)

# PYZ: Create a compressed archive of all the Python modules
pyz = PYZ(a.pure)

# EXE: Generate the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='run_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# COLLECT: Collect all necessary files into a single directory
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='run_app',
)
