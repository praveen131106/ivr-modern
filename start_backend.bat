@echo off
echo Starting Train IVR Backend Server...
echo.
cd backend
python -m uvicorn main:app --reload
pause

