@echo off
echo ============================================================
echo CareBridge-AI Setup Script
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements-dev.txt
echo Dependencies installed.
echo.

REM Create logs directory
if not exist "logs" (
    echo Creating logs directory...
    mkdir logs
    echo Logs directory created.
    echo.
)

REM Setup database
echo Setting up database...
python scripts\setup_database.py
echo.

REM Make migrations
echo Creating migrations...
python manage.py makemigrations
echo.

REM Run migrations
echo Running migrations...
python manage.py migrate
echo.

echo ============================================================
echo Setup completed successfully!
echo ============================================================
echo.
echo Next steps:
echo 1. Create superuser: python manage.py createsuperuser
echo 2. Run server: python manage.py runserver
echo 3. Access admin: http://localhost:8000/admin/
echo 4. Access API docs: http://localhost:8000/api/docs/
echo ============================================================
pause
