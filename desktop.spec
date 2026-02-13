# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for VoiceFlow Desktop Application
Build with: pyinstaller desktop.spec
"""

import os

block_cipher = None

extra_datas = []
if os.path.exists('bundled_models'):
    extra_datas.append(('bundled_models', 'bundled_models'))

# Collect all data files
a = Analysis(
    ['desktop_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
    ] + extra_datas,
    hiddenimports=[
        'flask',
        'whisper',
        'transformers',
        'torch',
        'scipy',
        'scipy.io.wavfile',
        'pygame',
        'pyttsx3',
        'huggingface_hub',
        'PyQt5.QtWebEngineWidgets',
        'sklearn',
        'tiktoken',
        'regex',
        'ftfy',
        'more_itertools',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pandas',
        'numpy.distutils',
        'setuptools',
        'pip',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VoiceFlow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True for debugging, False for release
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VoiceFlow',
)
