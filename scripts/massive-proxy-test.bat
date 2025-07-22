@echo off
echo 🚀 MASSIVE PROXY TESTING - Process ALL 39,000+ Proxies
echo.
echo ⚠️  WARNING: This will process the ENTIRE proxy database!
echo 📊 Expected to find 50-200+ working proxies (vs current 5)
echo ⏱️  Time: 10-20 minutes for complete testing
echo 🔥 High CPU/bandwidth usage during testing
echo.
echo 🎯 This addresses your concern about only testing 200-500 proxies
echo    instead of the full 39,000+ available proxies
echo.
cd /d "%~dp0.."
python scripts/massive_proxy_tester.py
pause
