# PyInstaller spec for OnCUE.
# Build from the project root:
#   pip install pyinstaller
#   pyinstaller packaging/oncue.spec
# Output: dist/OnCUE.exe (windowed, single file).
#
# Notes:
# - The whisper model is NOT bundled; faster-whisper downloads it to the user
#   cache on first voice use.
# - Playwright's Chromium is NOT bundled; the `browse` tool tells users how to
#   install it. Everything else works without it.

import sys
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = [], [], []
for pkg in ("ctranslate2", "faster_whisper", "langgraph", "tiktoken"):
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception:
        pass

hiddenimports += [
    "langchain_groq",
    "langchain_openai",
    "langchain_anthropic",
    "langchain_google_genai",
    "langchain_tavily",
    "sounddevice",
    "mss",
    "pynput.keyboard._win32" if sys.platform == "win32" else "pynput.keyboard._darwin",
    "pynput.mouse._win32" if sys.platform == "win32" else "pynput.mouse._darwin",
]
if sys.platform == "win32":
    hiddenimports += ["AppOpener"]

a = Analysis(
    ["../oncue/__main__.py"],
    pathex=[".."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["torch", "tkinter", "matplotlib"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="OnCUE",
    console=False,
    upx=False,
)
