Potree Converter - easy point-cloud conversion
===============================================

This turns point-cloud files (.e57, .las, .laz, .ply, .xyz, .pcd, .pts)
into a Potree octree folder you can load in the Potree web viewer.

----------------------------------------------------------------
ONE-TIME SETUP
----------------------------------------------------------------
1. Install Docker Desktop:
   https://www.docker.com/products/docker-desktop/
2. Start Docker Desktop and wait until it says it is running.

----------------------------------------------------------------
EASIEST WAY - the app  (Windows)
----------------------------------------------------------------
- Download  PotreeConverter.exe  (from the project's Releases page,
  or ask whoever gave you this).
- Double-click it. No install, no Python needed.
- Click "Choose..." to pick your point-cloud file, pick where to
  save the result, then click Convert.
- The FIRST conversion builds the converter and downloads a few
  hundred MB - this can take several minutes. It only happens once.
- The result is a  <yourfile>_potree  folder in the location you
  chose. Docker Desktop must be installed and running (see setup
  above); the app will tell you if it isn't.

The app also runs on macOS / Linux if you have Python 3 installed:
  python converter_gui.py
(On Linux you may first need:  sudo apt install python3-tk)

----------------------------------------------------------------
HOW TO CONVERT  (Windows, drag & drop)
----------------------------------------------------------------
- Drag your point-cloud file onto  Convert.bat
- The FIRST run builds the converter and downloads a few hundred
  MB - this can take several minutes. It only happens once.
- When it finishes you'll have a new folder next to your file,
  named  <yourfile>_potree  - that's the result.
- You can drag several files at once to convert them in a batch.

HOW TO CONVERT  (macOS / Linux)
----------------------------------------------------------------
- Open a terminal
- Navigate to the potree-converter directory
- Run `./convert.command /user/path-to-file`
  This wil then run the conversion process

----------------------------------------------------------------
USING THE RESULT
----------------------------------------------------------------
The <yourfile>_potree folder contains metadata.json, hierarchy.bin
and octree.bin. Point a Potree viewer at the metadata.json to view
the cloud in 3D.

----------------------------------------------------------------
NOTES
----------------------------------------------------------------
- Trimble RealWorks projects (.rwp / .rwi / .rwcx) are NOT supported.
  Export them to .e57 or .las/.laz from RealWorks first.
- If a conversion fails, the messages in the window explain why
  (most often: Docker isn't running, or an unsupported file).

----------------------------------------------------------------
BUILDING THE APP  (for maintainers)
----------------------------------------------------------------
The GUI is a single Python file, converter_gui.py. To turn it into
a double-click PotreeConverter.exe:

  pip install pyinstaller
  python build.py

PyInstaller does NOT cross-compile - run it ON Windows to get the
.exe (or on Linux/macOS for a native binary). The result is in
dist/.

A GitHub Action (.github/workflows/build-windows.yml) builds the
Windows .exe automatically: run it from the Actions tab, or push a
git tag like v1.0 to also attach the .exe to a Release.
