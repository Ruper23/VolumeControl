@echo off
REM Build script for Volume Control utility

cd /d "D:\D disk\IT\AI Agent\Hermes\VolumeControl"

echo ============================================
echo  Volume Control - Build Script
echo ============================================
echo.

echo [1/5] Cleaning old builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist VolumeControl.spec del /q VolumeControl.spec
echo Done.
echo.

echo [2/5] Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller pystray pywin32 pillow
echo.
echo Verifying pystray is installed...
python -c "import pystray; print('pystray OK')" || (
    echo ERROR: pystray not found! Installing...
    pip install pystray
)
echo.

echo [3/5] Generating icon...
python -c "exec(open('volume_control.py').read().split('def create_default_icon')[0]); exec('''import os; from PIL import Image, ImageDraw; APP_NAME=\"VolumeControl\"; CONFIG_DIR=os.path.join(os.getenv(\"APPDATA\"), APP_NAME); ICON_PATH=os.path.join(CONFIG_DIR, \"icon.ico\"); os.makedirs(CONFIG_DIR, exist_ok=True); size=256; img=Image.new(\"RGBA\", (size,size), (0,0,0,0)); draw=ImageDraw.Draw(img); cx,cy=size//2,size//2; [draw.ellipse((cx-r,cy-r,cx+r,cy+r), fill=(int(30+15*(1-r/cx)),int(30+15*(1-r/cx)),int(30+15*(1-r/cx))+40,255)) for r in range(cx,0,-1)]; draw.polygon([(int(cx-size*0.12),int(cy-size*0.18)),(int(cx+size*0.02),int(cy-size*0.14)),(int(cx+size*0.02),int(cy+size*0.14)),(int(cx-size*0.12),int(cy+size*0.18))], fill=(80,80,90,255), outline=(120,120,130,255)); draw.polygon([(int(cx+size*0.02),int(cy-size*0.10)),(int(cx+size*0.18),int(cy-size*0.22)),(int(cx+size*0.18),int(cy+size*0.22)),(int(cx+size*0.02),int(cy+size*0.10))], fill=(60,60,70,255), outline=(100,100,110,255)); [(draw.arc((cx+int(size*0.10)-int(size*r),cy-int(size*r),cx+int(size*0.10)+int(size*r),cy+int(size*r)), start=-50, end=50, fill=(0,200,255,255-i*40), width=w)) for i,(r,w) in enumerate([(0.28,4),(0.36,3),(0.44,2)])]; img.save(ICON_PATH, format=\"ICO\", sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)]); print(\"Icon generated\")''')"
echo.

echo [4/5] Building executable with icon...
pyinstaller --onefile --noconsole --name "VolumeControl" --icon="%APPDATA%\VolumeControl\icon.ico" ^
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

echo [5/5] Installing to Program Files and creating shortcut...
set "INSTALL_DIR=C:\Program Files\VolumeControl"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
copy /Y "dist\VolumeControl.exe" "%INSTALL_DIR%\VolumeControl.exe"
copy /Y "%APPDATA%\VolumeControl\icon.ico" "%INSTALL_DIR%\icon.ico"

REM Create desktop shortcut via PowerShell
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Volume Control.lnk'); $s.TargetPath = '%INSTALL_DIR%\VolumeControl.exe'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.IconLocation = '%INSTALL_DIR%\icon.ico'; $s.Description = 'Volume Control - scroll taskbar to adjust volume'; $s.Save()"

echo.
echo ============================================
echo  Build and install complete!
echo  Installed to: %INSTALL_DIR%
echo  Desktop shortcut: Volume Control.lnk
echo  Icon: %INSTALL_DIR%\icon.ico
echo ============================================
pause