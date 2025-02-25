@echo off
pyinstaller --noconsole --onefile --icon=resource\app.ico --add-data "resource\app.ico;." clipAssistant.py
pause