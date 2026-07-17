@echo off
REM Setup script for E-Commerce Backend Development (Windows)

echo 🚀 E-Commerce Backend - Development Setup (Windows)
echo =============================================

REM Check Python version
echo ✓ Checking Python version...
python --version

REM Create virtual environment
if not exist "venv" (
    echo ✓ Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
) else (
    echo ✓ Virtual environment already exists, activating...
    call venv\Scripts\activate.bat
)

REM Upgrade pip
echo ✓ Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

REM Install dependencies
echo ✓ Installing dependencies...
pip install -r requirements.txt

REM Setup environment file
if not exist ".env" (
    echo ✓ Creating .env file...
    copy .env.example .env
    echo Please edit .env with your configuration
) else (
    echo ✓ .env file already exists
)

REM Run migrations
echo ✓ Running database migrations...
python manage.py migrate

REM Create superuser
echo.
echo ✓ Create superuser for admin access
python manage.py createsuperuser

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Start the development server: python manage.py runserver
echo 2. Visit Swagger docs: http://localhost:8000/api/docs/
echo 3. Visit admin panel: http://localhost:8000/admin/
echo.
echo For production setup, see README.md
pause
