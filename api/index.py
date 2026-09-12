import sys
import os

# Add root directory and backend directory to sys.path for Vercel Serverless Function environment
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

UTILS_DIR = os.path.join(BACKEND_DIR, "utils")
if UTILS_DIR not in sys.path:
    sys.path.insert(0, UTILS_DIR)

from backend.main import app
