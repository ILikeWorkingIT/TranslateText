@echo off
cd /d "%~dp0"
echo TranslateText — окно приложения (не браузер). Заголовок: TranslateText
python -m pip install -r requirements.txt
python app.py
if errorlevel 1 echo Если окно не открылось: нужен Python с tcl/tk.
pause
