#!/bin/bash
echo "Starting Train IVR Backend Server..."
echo ""
cd backend
python3 -m uvicorn main:app --reload

