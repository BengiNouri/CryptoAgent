@echo off
echo.
echo ================================
echo   Crypto Insight Agent Startup
echo ================================
echo.

echo [1/4] Starting Docker services...
docker-compose up -d

echo.
echo [2/4] Waiting for services to be ready...
timeout /t 15 /nobreak > nul

echo.
echo [3/4] Initializing database...
docker-compose exec app python manage.py migrate

echo.
echo [4/4] Loading crypto data...
docker-compose exec app python manage.py load-data 30

echo.
echo ================================
echo   READY! 
echo ================================
echo.
echo Your app is running at: http://localhost:8501
echo.
echo Useful commands:
echo   docker-compose logs -f app      (view logs)
echo   docker-compose down             (stop services)
echo   docker-compose restart app      (restart after changes)
echo.
echo Opening browser...
start http://localhost:8501
echo.
pause