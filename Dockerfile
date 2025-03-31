# ───────────── Base ─────────────
FROM python:3.11-slim

# ───────────── Environment ─────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ───────────── System Dependencies ─────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    unzip \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libxss1 \
    libasound2 \
    libxshmfence1 \
    libx11-xcb1 \
    libgbm1 \
    libxcomposite1 \
    libxdamage1 \
    libxi6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ───────────── App Setup ─────────────
WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && playwright install --with-deps

# ───────────── App Code ─────────────
COPY . /app

# ───────────── Entrypoint ─────────────
CMD ["python", "main.py"]
