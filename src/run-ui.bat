@echo off
cd /d "%~dp0"
echo TranslateText: app window, not a browser. Title: TranslateText
python -m pip install -r requirements.txt
python app.py
if errorlevel 1 echo If the window did not open: need Python with tcl/tk.
pause
