FROM python:3.12-slim-bookworm

WORKDIR /app

# Install system dependencies and Official Google Chrome (required for stealth/Turnstile)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    xvfb \
    python3-tk \
    python3-dev \
    python3-xlib \
    scrot \
    curl \
    unzip \
    fonts-liberation \
    fonts-noto \
    fonts-noto-color-emoji \
    fonts-indic \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Start FastAPI using uvicorn
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
