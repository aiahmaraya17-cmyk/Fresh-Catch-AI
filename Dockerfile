# ─────────────────────────────────────────────────────────────────────────────
# FreshCatch AI — Backend + Python AI (single container)
# Runs the Express API which spawns Python (cv2 + scikit-learn) for inference.
# Build context MUST be the repository root so both /backend and /ai are copied.
# ─────────────────────────────────────────────────────────────────────────────
FROM node:20-bookworm-slim

# System packages:
#  - python3 / pip / venv  → the AI inference engine
#  - build-essential + python3-dev → compile better-sqlite3 (native) & any wheels
#  - libglib2.0-0 → runtime dep some opencv builds still touch (kept minimal;
#    we use opencv-python-headless so libGL is NOT required)
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 \
      python3-pip \
      python3-venv \
      build-essential \
      python3-dev \
      libglib2.0-0 \
      ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Python dependencies (cached layer) ──────────────────────────────────────
# Use an isolated virtualenv so we do not fight Debian's "externally managed"
# Python. PYTHON_PATH points the Node bridge at this interpreter.
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHON_PATH="$VIRTUAL_ENV/bin/python"

COPY ai/requirements-server.txt ./ai/requirements-server.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r ai/requirements-server.txt

# ── Node dependencies (cached layer) ────────────────────────────────────────
COPY backend/package.json backend/package-lock.json ./backend/
RUN cd backend && npm ci --omit=dev

# ── Application code ─────────────────────────────────────────────────────────
COPY backend ./backend
COPY ai ./ai

# ── Runtime configuration ────────────────────────────────────────────────────
# PORT is provided by the host (Render sets it). Persistent data (SQLite DB and
# uploaded images) should live on a mounted disk at /data — set DATABASE_PATH
# and UPLOAD_DIR to point there via the host's environment settings.
ENV NODE_ENV=production
ENV PORT=5000
EXPOSE 5000

WORKDIR /app/backend
CMD ["node", "src/server.js"]
