# Use lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements then install for better caching
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the repository content
COPY . .

# Create logs dir to avoid write errors
RUN mkdir -p backend/logs

# Expose port (container)
EXPOSE 8000

# Start command (use PORT env if set by platform)
CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker backend.main:app --bind 0.0.0.0:${PORT:-8000}"]