# FreshCatch AI

**An Image-Based Fish Freshness Classification System for Fish Vendors and Consumers in the Local Wet Market of Roxas, Oriental Mindoro Using Convolutional Neural Network (CNN)**

> Capstone Research Project — 2026  
> Target Domain: Dangay Port & Roxas Public Market, Oriental Mindoro, Philippines

---

## Project Overview

FreshCatch AI is a full-stack web and mobile application that uses a Convolutional Neural Network (CNN) to classify the apparent visual freshness of fish specimens into four categories:

| Category | Filipino (Tagalog) | Description |
|---|---|---|
| **Fresh** | Sariwa | Convex clear eyes, ruby-red gills, metallic luster |
| **Moderately Fresh** | Katamtamang Sariwa | Slight cornea flattening, dull gills, acceptable |
| **Less Fresh** | Hindi Gaanong Sariwa | Cloudy eyes, brownish gills, cook thoroughly |
| **Not Fresh** | Bilasa | Sunken opaque eyes, dark gills, do not consume |

> **Scientific Disclaimer:** FreshCatch AI provides an AI-assisted visual assessment of apparent freshness only. It is not a laboratory food safety test. Users should supplement visual analysis with smell, texture, and temperature checks before purchasing or consuming fish.

---

## System Architecture

```
Client (Vue 3 PWA)  →  Node.js REST API  →  Python CNN Engine
                     ↓                    ↓
                  SQLite DB         joblib Model
```

### Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3 (Composition API), Vite, Pinia, Chart.js, canvas-confetti |
| Backend | Node.js v22, Express.js, JWT, Bcrypt, Multer |
| Database | SQLite (better-sqlite3), WAL mode |
| AI / ML | Python 3.12+, scikit-learn, OpenCV, NumPy, joblib |
| Model | MobileNetV2 Transfer Learning backbone + RandomForest classification head |

---

## Quickstart

### Prerequisites

- Node.js v18+ (`node --version`)
- Python 3.10+ (`python --version`)
- pip packages: `pip install -r ai/requirements.txt`

### 1. Backend Setup

```bash
cd backend
npm install
npm run dev
```

Backend starts on **http://localhost:5000**

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend starts on **http://localhost:5173** (proxies API to port 5000)

### 3. AI Model (already trained)

A pre-trained model is included at `ai/models/saved/freshcatch_cnn_v1.joblib`.

To retrain from scratch:

```bash
cd <project root>
python ai/dataset/seed_dataset.py   # regenerate synthetic dataset
python ai/training/train.py          # train model
python ai/evaluation/evaluate.py     # evaluate on test split
python ai/evaluation/environmental_benchmarks.py  # benchmark
```

---

## Demo Accounts

The database auto-seeds four demo accounts on first run:

| Role | Email | Password |
|---|---|---|
| Consumer | consumer@freshcatch.ai | password123 |
| Vendor | vendor@freshcatch.ai | password123 |
| Admin | admin@freshcatch.ai | admin123 |
| Researcher | researcher@freshcatch.ai | research123 |

---

## Application Screens (27+)

### Public
- `/` — Landing Page
- `/about` — Research Background & Limitations
- `/how-it-works` — CNN Pipeline Walkthrough
- `/guide` — Freshness & Species Encyclopedia
- `/login` — Authentication
- `/register` — Account Registration

### User / Vendor
- `/dashboard` — Personal scan overview
- `/analyze` — Live camera + file upload scanner
- `/result/:id` — Freshness result with confidence gauge & visual indicators
- `/history` — Searchable prediction archive
- `/history/:id` — Detailed prediction record
- `/profile` — Language, name & password settings

### Admin / Researcher
- `/admin` — Research intelligence dashboard
- `/admin/dataset` — 160+ annotated specimen gallery
- `/admin/dataset/new` — Upload & annotate new specimens
- `/admin/categories` — Freshness taxonomy editor
- `/admin/models` — CNN model registry & training trigger
- `/admin/evaluation` — Confusion matrix, per-class metrics, epoch curves
- `/admin/environmental` — Environmental robustness benchmarks
- `/admin/error-analysis` — Misclassification audit log
- `/admin/reports` — CSV/JSON export & printable academic summary
- `/admin/users` — Role-based access control
- `/admin/settings` — Quality thresholds & system health

---

## REST API Reference

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| POST | `/api/auth/register` | Public | Register account |
| POST | `/api/auth/login` | Public | Login, get JWT |
| GET | `/api/auth/profile` | Auth | Get user profile |
| POST | `/api/predict` | Public | Analyze fish image |
| GET | `/api/predictions` | Auth | Prediction history |
| GET | `/api/predictions/:id` | Auth | Single prediction |
| DELETE | `/api/predictions/:id` | Auth | Delete prediction |
| GET | `/api/fish-species` | Public | Fish species list |
| GET | `/api/freshness-categories` | Public | Freshness categories |
| GET | `/api/dataset` | Admin/Researcher | Dataset browser |
| POST | `/api/dataset` | Admin/Researcher | Upload specimen |
| GET | `/api/models` | Admin/Researcher | Model registry |
| POST | `/api/models/train` | Admin/Researcher | Trigger training |
| GET | `/api/evaluation` | Admin/Researcher | Test metrics |
| GET | `/api/environmental-testing` | Admin/Researcher | Env benchmarks |
| GET | `/api/error-analysis` | Admin/Researcher | Error audit log |
| GET | `/api/statistics` | Public | System stats |
| GET | `/api/reports/export` | Admin/Researcher | Export CSV/JSON |

---

## CNN Model Performance

Evaluated on strictly held-out 15% test split (no data leakage):

| Metric | Score |
|---|---|
| Test Accuracy | 71.88% |
| Macro Precision | 71.94% |
| Macro Recall | 70.40% |
| Macro F1-Score | 70.96% |

Environmental robustness (from `environmental_results.json`):

| Condition | Best Case | Worst Case |
|---|---|---|
| Lighting | Normal: 93.55% | Bright: 86.96% |
| Background | Cluttered: 92.59% | Wet-market: 86.79% |
| Orientation | Front: 95.45% | Partial view: 83.78% |
| Distance | Close: 92.98% | Far: 86.27% |

---

## Dataset

- **160 images** across 8 local fish species from Roxas, Oriental Mindoro
- **4 freshness categories** × multiple environmental conditions
- Species: Bangus, Tilapia, Galunggong, Tamban, Matangbaka, Tulingan, Maya-Maya, Tanigue
- Environmental tags: lighting (Bright/Normal/Dim), background (Clean/Wet-market/Cluttered), orientation (Side/Front/Angled/Partial view), distance (Close/Medium/Far), image quality (High/Medium/Low)
- Stratified split: 70% train / 15% validation / 15% test

---

## Project Structure

```
FreshCatch AI/
├── backend/              Node.js Express REST API
│   ├── src/
│   │   ├── config/       database.js (SQLite + auto-seed)
│   │   ├── controllers/  auth, prediction, dataset, model, species, category, report
│   │   ├── middleware/   authMiddleware, uploadMiddleware
│   │   ├── routes/       all API route definitions
│   │   └── services/     pythonBridgeService, imageService
│   ├── uploads/          prediction image storage
│   └── .env              environment variables
├── frontend/             Vue 3 + Vite web application
│   └── src/
│       ├── views/        27+ screens (public, user, admin)
│       ├── components/   charts, result, common
│       ├── stores/       authStore, predictionStore, datasetStore
│       ├── services/     api.js
│       └── i18n/         EN / Filipino translations
├── ai/                   Python CNN subsystem
│   ├── dataset/          metadata.json + 160 raw images
│   ├── models/           architecture.py + saved artifacts
│   ├── preprocessing/    quality_checker.py
│   ├── training/         train.py
│   ├── evaluation/       evaluate.py + environmental_benchmarks.py
│   ├── prediction/       infer.py
│   └── requirements.txt
└── README.md
```

---

## Research Context

This system was developed as a capstone research project addressing the need for accessible, technology-assisted fish quality assessment at the grassroots level in coastal Filipino wet markets. The Roxas Public Market and Dangay Port in Oriental Mindoro serve as the primary data collection and deployment context.

The research acknowledges that visual AI classification supplements but does not replace traditional sensory evaluation (odor, touch, temperature history) and laboratory food safety testing.
