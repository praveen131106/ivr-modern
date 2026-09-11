# 🚀 Deployment Guide

## Quick Start

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Backend:**
   ```bash
   # Windows
   start_backend.bat
   
   # Linux/Mac
   ./start_backend.sh
   ```

3. **Open Frontend:**
   - Open `frontend/index.html` in browser
   - Or use: `python -m http.server 8080` in frontend folder

## Production Deployment

### Backend Deployment

**Option 1: Using Uvicorn**
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**Option 2: Using Gunicorn**
```bash
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Deployment

**Option 1: Static Hosting**
- Upload `frontend/` folder to any static hosting (GitHub Pages, Netlify, Vercel)
- Update `API_BASE_URL` in `script.js` to production backend URL

**Option 2: Serve with Backend**
- Add static file serving in FastAPI
- Serve from same domain

## Environment Variables

Create `.env` file:
```
API_PORT=8000
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:8080,https://yourdomain.com
```

## Security Considerations

- Enable HTTPS for production
- Add authentication if needed
- Implement rate limiting
- Validate all inputs
- Sanitize user data

