@echo off
cd /d "%~dp0"
echo TranslateText: building TranslateText.exe (no console window)
python -m pip install -r requirements.txt
python -m pip install "pyinstaller>=6,<7"
python -m PyInstaller --noconfirm --clean TranslateText.spec
if errorlevel 1 (
  echo Build failed.
  pause
  exit /b 1
)
if not exist "..\artifacts" mkdir "..\artifacts"
copy /Y "dist\TranslateText.exe" "..\artifacts\TranslateText.exe"
echo.
echo Ready: artifacts\TranslateText.exe
echo Double-click in Explorer. Ollama must be running for translation.
pause
