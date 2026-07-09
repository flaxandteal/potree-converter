@echo off
REM ============================================================
REM  Potree Converter - drag & drop launcher (Windows)
REM
REM  Drag one or more point-cloud files (.e57 .las .laz .ply
REM  .xyz ...) onto this file. Each is converted to a Potree
REM  octree folder named <file>_potree, placed next to the input.
REM
REM  Requires Docker Desktop installed and running.
REM ============================================================
setlocal enabledelayedexpansion

set "IMAGE=potree-converter"
set "SCRIPTDIR=%~dp0"

REM --- Docker available? ---
where docker >nul 2>&1
if errorlevel 1 (
  echo.
  echo ERROR: Docker was not found.
  echo Install Docker Desktop from https://www.docker.com/products/docker-desktop/
  echo make sure it is running, then try again.
  echo.
  pause
  exit /b 1
)

REM --- Anything dropped? ---
if "%~1"=="" (
  echo.
  echo Drag one or more point-cloud files onto this .bat to convert them.
  echo Supported: .e57 .las .laz .ply .xyz .pcd .pts
  echo.
  pause
  exit /b 0
)

REM --- Build the image on first use ---
docker image inspect %IMAGE% >nul 2>&1
if errorlevel 1 (
  echo.
  echo First run: building the converter image. This downloads a few
  echo hundred MB and may take several minutes. It only happens once.
  echo.
  docker build -t %IMAGE% "%SCRIPTDIR%."
  if errorlevel 1 (
    echo.
    echo ERROR: image build failed. See the messages above.
    pause
    exit /b 1
  )
)

REM --- Convert each dropped file ---
:loop
if "%~1"=="" goto done
set "INDIR=%~dp1"
if "!INDIR:~-1!"=="\" set "INDIR=!INDIR:~0,-1!"
set "FNAME=%~nx1"
set "BASE=%~n1"
echo.
echo === Converting !FNAME! ===
docker run --rm -v "!INDIR!:/data" %IMAGE% "/data/!FNAME!" -o "/data/!BASE!_potree"
if errorlevel 1 (
  echo *** Conversion FAILED for !FNAME!
) else (
  echo Done: !INDIR!\!BASE!_potree
)
shift
goto loop

:done
echo.
echo All conversions finished.
pause
