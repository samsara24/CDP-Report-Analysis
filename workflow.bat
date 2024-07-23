@echo off
REM Ensure to activate the Python environment if needed
REM call path\to\your\venv\Scripts\activate.bat

echo Running extract_qa_pairs.py...
python extract_qa_pairs.py
if %errorlevel% neq 0 (
    echo extract_qa_pairs.py failed!
    pause
    exit /b %errorlevel%
)

echo Running score_process.py...
python score_process.py
if %errorlevel% neq 0 (
    echo score_process.py failed!
    pause
    exit /b %errorlevel%
)

echo Running json_to_excel.py...
python json_to_excel.py
if %errorlevel% neq 0 (
    echo json_to_excel.py failed!
    pause
    exit /b %errorlevel%
)

echo All scripts ran successfully!
pause
