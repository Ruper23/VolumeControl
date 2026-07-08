@echo off
REM Build script for Volume Control utility

cd /d "D:\D disk\IT\AI Agent\Hermes\VolumeControl"

echo ============================================
echo  Volume Control - Build Script
echo ============================================
echo.

echo [1/4] Cleaning old builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist VolumeControl.spec del /q VolumeControl.spec
echo Done.
echo.

echo [2/4] Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller pystray pywin32 pillow
echo.
echo Verifying pystray is installed...
python -c "import pystray; print('pystray OK')" || (
    echo ERROR: pystray not found! Installing...
    pip install pystray
)
echo.

echo [3/4] Building executable...
pyinstaller --onefile --noconsole --name "VolumeControl" --icon=NONE ^
  --collect-all pystray ^
  --collect-all PIL ^
  --hidden-import=pycaw ^
  --hidden-import=pycaw.pycaw ^
  --hidden-import=comtypes ^
  --hidden-import=comtypes.client ^
  --hidden-import=pynput ^
  --hidden-import=pynput.mouse ^
  --hidden-import=pynput.keyboard ^
  --hidden-import=pystray._win32 ^
  --hidden-import=pystray._util ^
  --hidden-import=win32gui ^
  --hidden-import=win32api ^
  --hidden-import=win32con ^
  --hidden-import=win32gui_struct ^
  --hidden-import=winreg ^
  --hidden-import=_tkinter ^
  volume_control.py
if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)
echo.

echo [4/4] Copying to final location...
copy "dist\VolumeControl.exe" "D:\D disk\IT\AI Agent\Hermes\VolumeControl.exe"
echo.
echo ============================================
echo  Build complete!
echo  Exe: dist\VolumeControl.exe
echo  Copy: D:\D disk\IT\AI Agent\Hermes\VolumeControl.exe
echo ============================================
pause