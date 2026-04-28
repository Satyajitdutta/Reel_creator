# 🐾 PetReel Studio

**End-to-end AI pet reel creator** — script, edit, voice, YouTube upload — all automated.

## Repo layout

```
Reel_creator/
├── backend/          ← Railway deploys THIS folder
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt   ← no audioop-lts (Railway uses Python 3.11)
│   ├── nixpacks.toml      ← Python 3.11 + FFmpeg
│   ├── railway.toml
│   └── pipeline/
│       ├── audioop_shim.py
│       ├── vision.py
│       ├── planner.py
│       ├── designer.py
│       ├── tts_engine.py
│       ├── video_engine.py
│       └── uploader.py
└── frontend/         ← run locally: npm run dev
    ├── src/
    │   ├── App.tsx
    │   └── api.ts
    └── package.json
```

## Railway setup

1. Push this repo to GitHub  
2. Railway → New Project → Deploy from GitHub → `Reel_creator`  
3. **IMPORTANT: Set Root Directory = `backend`** in Railway service settings  
4. Add Volume at `/data`  
5. Set env vars: `GEMINI_API_KEY`, `GEMINI_MODEL=gemini-2.5-flash`, `STORAGE_ROOT=/data`  
6. Deploy ✅

## Local frontend

```bash
cd frontend
cp .env.example .env
# set VITE_BACKEND_URL=https://your-app.railway.app
npm install && npm run dev
```
