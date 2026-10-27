# -*- mode: python ; coding: utf-8 -*-
# Configuration PyInstaller : produit dist/AutoSaisieWord.exe (un seul fichier, sans console).
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("docx")  # modèles internes de python-docx

a = Analysis(
    ["app.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=["docx", "lxml.etree", "lxml._elementpath", "win32com", "win32com.client", "pythoncom", "pywintypes"],
    hookspath=[],
    runtime_hooks=[],
    excludes=["pytest", "unittest.mock"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="AutoSaisieWord",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)
