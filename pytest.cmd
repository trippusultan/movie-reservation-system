@echo off
set "PATH=%~dp0venv\Scripts;%PATH%"
pytest %*
