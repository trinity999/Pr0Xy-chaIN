@echo off
echo 🔧 AUTOMATIC DEAD PROXY REMOVAL SYSTEM
echo.
echo This will optimize your proxy pool by:
echo   ✅ Removing non-working proxies automatically
echo   ✅ Reviving recovered proxies
echo   ✅ Improving load balancing from 50%% to 80%%+
echo   ✅ Real-time health monitoring
echo   ✅ Performance optimization
echo.
cd /d "%~dp0.."
python scripts/auto_dead_proxy_remover.py
pause
