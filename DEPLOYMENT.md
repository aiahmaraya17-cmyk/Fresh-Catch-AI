# FreshCatch AI — Deployment Guide

This app has two deployable parts:

| Part | Where it goes | Why |
|------|---------------|-----|
| **Frontend** (Vue + Vite) | **Vercel** | Static site, perfect fit for Vercel |
| **Backend API + Python AI** (Express + OpenCV/scikit-learn) | **Render** (Docker) | Needs a long-running server, a writable disk, and Python — which Vercel serverless cannot provide |

The frontend talks to the backend over HTTPS. You will deploy the **backend first**, get its URL, then deploy the **frontend** pointing at that URL, and finally tell the backend to trust the frontend's domain (CORS).

---

## 0. One-time prerequisites

- A **GitHub** repository containing this project.
- A **Vercel** account (free) — https://vercel.com
- A **Render** account (free) — https://render.com

### Commit the AI model files
Render builds from GitHub, so the model weights must be committed. The trained
classifier (`freshcatch_cnn_v1.joblib`) is already tracked, but the ONNX fish-gate
model may be untracked. From the project root:

```bash
git add ai/models/saved/mobilenetv2_imagenet.onnx ai/models/saved/freshcatch_cnn_v1.joblib
git add Dockerfile .dockerignore render.yaml ai/requirements-server.txt
git add backend/ frontend/
git commit -m "Prepare for deployment (Vercel + Render)"
git push
```

> Note: `ai/dataset/raw/` (training/demo images) is intentionally **not** deployed —
> it is large and not needed for inference. The admin "Dataset" gallery will be
> empty in production unless you seed it later.

---

## 1. Deploy the backend to Render (Docker)

You can use the included blueprint (easiest) or configure manually.

### Option A — Blueprint (recommended)
1. In Render click **New +** → **Blueprint**.
2. Select your GitHub repo. Render reads **`render.yaml`** and proposes a
   web service named `freshcatch-api` with a 1 GB disk mounted at `/data`.
3. When prompted, set **`CORS_ORIGINS`** to a temporary value (you can leave it
   blank for now and fill it in after step 2 — blank means "allow all", fine
   for first test).
4. Click **Apply**. Render builds the Docker image (installs Node + Python +
   OpenCV + scikit-learn). First build takes several minutes.
5. When live, note the URL, e.g. `https://freshcatch-api.onrender.com`.

### Option B — Manual
1. **New +** → **Web Service** → connect the repo.
2. Runtime: **Docker**. Dockerfile path: `./Dockerfile`. Context: `.` (root).
3. Add a **Disk**: mount path `/data`, size 1 GB.
4. Add environment variables:
   | Key | Value |
   |-----|-------|
   | `NODE_ENV` | `production` |
   | `JWT_SECRET` | a long random string |
   | `PYTHON_PATH` | `/opt/venv/bin/python` |
   | `DATABASE_PATH` | `/data/freshcatch.db` |
   | `UPLOAD_DIR` | `/data/uploads` |
   | `CORS_ORIGINS` | (fill after step 2) |
5. Health check path: `/api/health`. Create the service.

### Verify the backend
Open `https://<your-render-url>/api/health` — you should see JSON with
`"status": "healthy"`.

---

## 2. Deploy the frontend to Vercel

1. In Vercel click **Add New…** → **Project** → import your GitHub repo.
2. Set **Root Directory** to **`frontend`** (important — the app is in a subfolder).
3. Framework preset: **Vite** (auto-detected). Build command `npm run build`,
   output directory `dist` (already set in `frontend/vercel.json`).
4. Add an **Environment Variable**:
   | Key | Value |
   |-----|-------|
   | `VITE_API_BASE_URL` | your Render URL, e.g. `https://freshcatch-api.onrender.com` (no trailing slash, no `/api`) |
5. Click **Deploy**. Note the resulting URL, e.g.
   `https://freshcatch-ai.vercel.app`.

---

## 3. Connect the two (CORS)

Back in **Render** → your service → **Environment**:

1. Set **`CORS_ORIGINS`** to your Vercel URL (no trailing slash). For multiple
   domains, separate with commas:
   ```
   CORS_ORIGINS=https://freshcatch-ai.vercel.app
   ```
2. Save — Render redeploys automatically.

Now open your Vercel URL, register/login, and run a fish scan. Images and
predictions should work end-to-end.

---

## 4. Notes, limits, and gotchas

- **Free tier sleeps.** Render's free web service spins down after inactivity;
  the first request afterwards may take ~30–60s (and Python cold-start adds a
  little more). Upgrade to a paid plan for always-on.
- **Persistent disk.** The SQLite DB and uploaded images live on `/data`. Do not
  store them on the ephemeral container filesystem, or they vanish on redeploy.
- **Database seeding.** On first boot the app creates tables and seeds demo
  accounts automatically (see `backend/src/config/database.js`). If you want the
  demo dataset gallery populated, run the seed script or upload images via the
  admin UI.
- **Changing the backend URL later** means updating `VITE_API_BASE_URL` in Vercel
  (triggers a frontend rebuild) and `CORS_ORIGINS` in Render.
- **Local development is unchanged.** With the env vars unset, the backend uses
  local paths and permissive CORS, and the frontend uses the Vite dev proxy
  (`npm run dev` in `frontend`, `npm run dev` in `backend`).

---

## Environment variable reference

### Backend (Render)
| Variable | Purpose | Example |
|----------|---------|---------|
| `PORT` | Listen port (Render sets it) | `5000` |
| `JWT_SECRET` | Signs auth tokens | long random string |
| `NODE_ENV` | Mode | `production` |
| `PYTHON_PATH` | Python interpreter for inference | `/opt/venv/bin/python` |
| `CORS_ORIGINS` | Allowed frontend origins (CSV) | `https://freshcatch-ai.vercel.app` |
| `DATABASE_PATH` | SQLite file on the disk | `/data/freshcatch.db` |
| `UPLOAD_DIR` | Uploaded images on the disk | `/data/uploads` |
| `DATASET_DIR` | (optional) dataset images | `/data/dataset` |

### Frontend (Vercel)
| Variable | Purpose | Example |
|----------|---------|---------|
| `VITE_API_BASE_URL` | Backend origin | `https://freshcatch-api.onrender.com` |
