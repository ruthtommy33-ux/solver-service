FROM python:3.12-slim-bookworm

WORKDIR /app

# Install system dependencies for Chromium and virtual display
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    xvfb \
    chromium \
    python3-tk \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run with Xvfb virtual display so Chrome runs in "headed" mode (stealthier than headless)
CMD sh -c "xvfb-run --server-args=\"-screen 0 1024x768x24\" uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"
