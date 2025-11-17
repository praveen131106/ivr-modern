# Deployment & Hosting Guide

## Local Docker
1. docker compose -f milestone4/deployment/docker-compose.yml up --build
2. Backend: http://localhost:8000, Frontend: http://localhost:8080
3. Stop with docker compose ... down

## Render
- Create new Web Service
- Build command: pip install -r requirements.txt
- Start command: uvicorn backend.main:app --host 0.0.0.0 --port 
- Add environment variables from .env.example

## Railway
- railway up
- Provide repo with Dockerfile path milestone4/deployment/Dockerfile
- Map port 8000, add health check /health

## Azure App Service
- Publish Docker image to Azure Container Registry
- Configure startup command python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
- Add environment variables under Configuration  Application settings

## AWS (Elastic Beanstalk)
- Use Dockerrun v2 referencing the same Dockerfile
- Set health check URL to /health
- Attach CloudWatch alarms for CPU > 70%

## Verification Checklist
- [ ] GET /health returns status 200 in production
- [ ] CORS origins updated to deployed frontend URL
- [ ] HTTPS enabled via hosting provider

