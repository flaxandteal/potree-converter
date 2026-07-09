#!/usr/bin/env python3
"""Build a double-clickable Potree Converter binary with PyInstaller.

PyInstaller does NOT cross-compile: run this ON the OS you want to ship for.
    Windows  ->  dist/PotreeConverter.exe
    Linux    ->  dist/PotreeConverter
    macOS    ->  dist/PotreeConverter

    pip install pyinstaller
    python build.py

The Dockerfile + convert.sh are bundled into the binary so the app can build
the converter image on a user's machine on first run. Docker Desktop / Docker
Engine still has to be installed on that machine — it is not (and cannot be)
bundled.
"""
import os
import PyInstaller.__main__

sep = ";" if os.name == "nt" else ":"  # --add-data uses ; on Windows, : elsewhere
PyInstaller.__main__.run([
    "converter_gui.py",
    "--onefile",
    "--windowed",        # no console window; Docker output shows inside the app
    "--name", "PotreeConverter",
    f"--add-data=Dockerfile{sep}.",
    f"--add-data=convert.sh{sep}.",
    "--clean",
    "--noconfirm",
])
