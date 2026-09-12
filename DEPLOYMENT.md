# 🚀 Deployment Guide (Vercel Full-Stack, Netlify & Docker)

## ⚡ Option 1: Vercel Full-Stack Deployment (Recommended)

Both the **FastAPI Python Backend** and **Interactive Web Frontend** are pre-configured to deploy together on Vercel under a single domain.

### 🔹 Deployment via Vercel CLI
```bash
npx vercel
```
Follow the interactive prompts to link and deploy your project instantly.

### 🔹 Deployment via GitHub Integration
1. Log in to [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New** → **Project** → Select `praveen131106/ivr-modern`.
3. Keep default settings (Vercel will detect `vercel.json` and `api/index.py`).
4. *(Optional)* Under **Environment Variables**, add:
   - `GEMINI_API_KEY`: `your_gemini_api_key`
5. Click **Deploy**. Both the API (`/api/*`, `/health`) and web UI (`/`) will be live on a single `*.vercel.app` URL!

---

## ⚡ Option 2: Local Development Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Backend Server:**
   ```bash
   # Windows
   start_backend.bat

   # Linux/Mac
   ./start_backend.sh
   ```

3. **Open Web Frontend:**
   - Double-click `open_frontend.bat` or open `frontend/index.html` in your browser.

---

## ⚡ Option 3: Docker Deployment (Backend API)

```bash
docker build -t ivr-backend .
docker run -p 8000:8000 -e GEMINI_API_KEY="your_api_key" ivr-backend
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env`:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
PORT=8000
LOG_LEVEL=INFO
```
