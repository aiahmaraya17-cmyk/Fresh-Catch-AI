# FreshCatch AI deployment

## Services

| Component | Host | Notes |
| --- | --- | --- |
| Vue + Vite frontend | Vercel | Set the project root to `frontend`; the Vercel rewrite is in `frontend/vercel.json`. |
| Express API + Python ML inference | Render | Deploy the root Dockerfile using `render.yaml`. The ML model and API run in one service. |
| Authentication + user profiles | Firebase | Firebase Authentication handles email/password; Firestore stores user profiles and roles. |

Predictions, stalls, datasets, and other relational operational records remain in SQLite on Render's persistent disk. User profile/auth data lives in Firebase. The backend mirrors Firebase users into SQLite because existing app records reference integer user IDs.

## Firebase setup

In Firebase project `freshcatch-ai`:

1. Enable **Authentication → Sign-in method → Email/Password**.
2. Create a Firestore database.
3. Publish the root `firestore.rules` rules. They allow a signed-in user to manage only their own profile and prevent client-side role changes.
4. Add the Vercel production domain under **Authentication → Settings → Authorized domains**.
5. Create a service account under **Project settings → Service accounts** for the Render backend. Keep its private key secret.

Self-registered users get the `consumer` role. To provision the first admin, create and sign in to that account, then use the Firebase Console to set `users/{uid}.role` to `admin`; subsequent promotions can use the admin user-management page/API. Firestore rules prevent users from changing their own role.

## Deploy backend and ML to Render

Create a Render Blueprint from the repository and use `render.yaml`. The blueprint builds the root Dockerfile, mounts `/data`, and configures the `/api/health` health check. Set these service environment variables:

| Variable | Value |
| --- | --- |
| `NODE_ENV` | `production` |
| `FIREBASE_PROJECT_ID` | `freshcatch-ai` |
| `FIREBASE_CLIENT_EMAIL` | Service account `client_email` |
| `FIREBASE_PRIVATE_KEY` | Service account `private_key`; paste full value (escaped `\\n` newlines are supported) |
| `PYTHON_PATH` | `/opt/venv/bin/python` |
| `DATABASE_PATH` | `/data/freshcatch.db` |
| `UPLOAD_DIR` | `/data/uploads` |
| `CORS_ORIGINS` | Vercel production URL, no trailing slash; add preview/custom domains separated by commas if needed |

The `FIREBASE_CLIENT_EMAIL` and `FIREBASE_PRIVATE_KEY` values are server secrets. Do not add them to Vercel or any `VITE_*` variable. Wait for the first successful deploy and copy the Render origin, for example `https://freshcatch-api.onrender.com`.

## Deploy frontend to Vercel

Import the repository into Vercel and set **Root Directory** to `frontend`. Build command is `npm run build`; output directory is `dist`. Add these environment variables for Production (and Preview if you use preview deployments), then redeploy after changing them:

| Variable | Value |
| --- | --- |
| `VITE_API_BASE_URL` | Render origin, e.g. `https://freshcatch-api.onrender.com` (no `/api`, no trailing slash) |
| `VITE_FIREBASE_API_KEY` | `AIzaSyCRakMImm2C_h8DWzIdsymz9p7s8Gw6qFU` |
| `VITE_FIREBASE_AUTH_DOMAIN` | `freshcatch-ai.firebaseapp.com` |
| `VITE_FIREBASE_PROJECT_ID` | `freshcatch-ai` |
| `VITE_FIREBASE_STORAGE_BUCKET` | `freshcatch-ai.firebasestorage.app` |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | `700006049129` |
| `VITE_FIREBASE_APP_ID` | `1:700006049129:web:7a4aae56c6be2d434c49f8` |

These Firebase web app values are public browser configuration; Firebase security rules and API key restrictions provide protection. The backend service account key is private and belongs only in Render.

Once Vercel has deployed, add its URL to Render `CORS_ORIGINS`, save/redeploy the backend, then confirm `/api/health`, account registration/login, and a fish scan.

## Local environment

Copy `frontend/.env.example` to `frontend/.env.local`; it contains the Firebase web app values and leave `VITE_API_BASE_URL` blank when using the Vite proxy. Copy `backend/.env.example` to `backend/.env` and fill the Firebase Admin credentials. Never commit `.env` files or service account JSON/private keys.

## Environment reference

### Vercel

`VITE_API_BASE_URL` and all six `VITE_FIREBASE_*` values listed above. Vite embeds these into the browser build, so they must not contain secrets.

### Render

`PORT` is supplied by Render. Set `NODE_ENV`, `FIREBASE_PROJECT_ID`, `FIREBASE_CLIENT_EMAIL`, `FIREBASE_PRIVATE_KEY`, `PYTHON_PATH`, `DATABASE_PATH`, `UPLOAD_DIR`, and `CORS_ORIGINS`. A persistent disk is required for SQLite and uploaded files. Free Render services can sleep when idle, so their first request may take longer.
