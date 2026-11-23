@echo off
setlocal
cd /d "%~dp0"
echo =====================================================
echo    CIVITAS - Python Smart City Simulator - CL1010
echo =====================================================
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON=py"
) else (
    set "PYTHON=python"
)
%PYTHON% --version
if errorlevel 1 (
    echo.
    echo Python was not found. Install Python 3.10+ from python.org.
    echo During setup select "Add Python to PATH".
    pause
    exit /b 1
)
echo.
echo Checking the three Python libraries...
%PYTHON% -c "import streamlit, plotly, reportlab" >nul 2>&1
if errorlevel 1 (
    echo Installing missing libraries. An internet connection is needed the first time.
    %PYTHON% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Could not install dependencies. Check your internet connection.
        pause
        exit /b 1
    )
)
echo Starting CIVITAS in your browser...
%PYTHON% -m streamlit run app.py
pause
