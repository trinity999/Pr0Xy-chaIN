@echo off
cd /d "%~dp0"
python proxy_status.py status %*
