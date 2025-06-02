# ─────────────────────────────────────────────────────────────────────────────
# 1) Start from a slim Python base
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.9-slim

# ─────────────────────────────────────────────────────────────────────────────
# 2) Install minimal system packages needed to compile 'blis' (and other wheels)
# ─────────────────────────────────────────────────────────────────────────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      gcc \
      libpq-dev \
      libffi-dev \
      libssl-dev \
      libxml2-dev \
      libxslt1-dev \
      curl \
    && rm -rf /var/lib/apt/lists/*

# ─────────────────────────────────────────────────────────────────────────────
# 3) Create and switch into the working directory `/app`
# ─────────────────────────────────────────────────────────────────────────────
WORKDIR /app

# ─────────────────────────────────────────────────────────────────────────────
# 4) Copy only requirements.txt and install Python dependencies
#    (so Docker can cache this layer if requirements.txt hasn’t changed)
# ─────────────────────────────────────────────────────────────────────────────
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download en_core_web_sm

# ─────────────────────────────────────────────────────────────────────────────
# 5) Now copy your actual application code
# ─────────────────────────────────────────────────────────────────────────────
COPY app/ ./app

# ─────────────────────────────────────────────────────────────────────────────
# 6) Expose port 8000 and set the default command to launch Uvicorn
# ─────────────────────────────────────────────────────────────────────────────
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
