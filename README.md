# 🐾 PetReel Studio
### Canva Enterprise + InVideo AI — Complete Pet Video Automation

End-to-end pipeline: **Upload media → Describe topic → AI scripts, designs & edits → Auto-uploads to YouTube**

---

## Architecture

```
Your Laptop (browser)                    Railway (cloud backend)
┌──────────────────────┐                ┌─────────────────────────────────────┐
│  React Studio UI     │  REST API  →   │  FastAPI + FFmpeg + AI Pipeline     │
│  localhost:3000       │ ←────────────  │                                     │
│  npm run dev         │                │  ① Vision AI  (Gemini analyses media)│
└──────────────────────┘                │  ② Script Gen (InVideo formulas)    │
                                        │  ③ Design Gen (Canva title cards)   │
                                        │  ④ TTS Voice  (gTTS / ElevenLabs)  │
                                        │  ⑤ Video Edit (Ken Burns + FX)      │
                                        │  ⑥ YouTube    (auto-upload)         │
                                        └─────────────────────────────────────┘
```

---

## 🚀 Setup: Railway Backend

### 1. Create Railway project
1. Go to [railway.app](https://railway.app) → **New Project → Deploy from GitHub**
2. Fork this repo or push the `backend/` folder
3. Railway auto-detects Python via `nixpacks.toml`

### 2. Add Railway Volume (for file storage)
Dashboard → Your service → **Volumes** → Add `/data` mount

### 3. Set Environment Variables
In Railway service settings → Variables:
```
GEMINI_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-2.5-flash
STORAGE_ROOT=/data
ELEVENLABS_API_KEY=optional_for_premium_tts
```

### 4. Note your Railway URL
e.g. `https://petreel-studio-production.up.railway.app`

---

## 🖥️ Setup: Local Frontend (Your Laptop)

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env → set VITE_BACKEND_URL=https://your-app.railway.app
npm run dev
```
Open http://localhost:3000 — that's your studio!

---

## YouTube Auto-Upload Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create project → Enable **YouTube Data API v3**
3. Create **OAuth 2.0 Client ID** (Desktop app type)
4. Download JSON → rename to `client_secrets.json`
5. Upload to Railway volume at `/data/client_secrets.json`
6. First run: backend will print an auth URL in logs — open it, authorize, done.
   Token auto-refreshes after that.

---

## Canva Enterprise Features Included

| Feature | Implementation |
|---|---|
| Magic Design | Gemini generates complete visual brief → Pillow renders branded frames |
| Brand Kit | Channel name, colors, logo → applied to every title card + thumbnail |
| Style Presets | 6 presets: Cinematic, Energetic, Warm, Minimal, Dramatic, Playful |
| Title Cards | Pillow-generated gradient cards with brand colors and logo |
| Outro Cards | Subscribe CTA with paw print branding |
| YouTube Thumbnails | Auto-generated with bold title text + brand overlay |
| Smart Resize | Export 9:16 (Shorts), 1:1 (Instagram) from one video |
| Color Grading | 6 FFmpeg grade presets (teal-orange, warm, high-contrast, etc.) |
| Text Overlays | Per-segment on-screen captions with brand styling |
| Background Removal | `rembg` library (add to requirements if needed) |

---

## InVideo AI Features Included

| Feature | Implementation |
|---|---|
| Text-to-Video | Just type a topic → AI generates everything |
| Vision Analysis | Gemini Vision describes every uploaded photo/video before scripting |
| Scene Matching | AI assigns best media to each script segment automatically |
| AI Scene Generation | Gemini Imagen generates missing visuals from text prompts |
| Script Formulas | 5 viral formulas: Hook-Loop-Payoff, PAS, Story Arc, Reaction, Day in Life |
| Hook Options | 3 A/B-testable opening hooks generated per video |
| Voice Presets | 5 accent/style options via gTTS; ElevenLabs for premium |
| Style Presets | One click changes entire video aesthetic |
| Refinement | Tell AI what to change → regenerate instantly |

---

## Daily Workflow

1. Add new pet photos/videos to Media Library (drag & drop)
2. Click **Vision AI** to analyze media
3. Set topic in Studio panel
4. Pick style preset + script formula
5. Click **Generate Reel** — everything happens automatically
6. Download or auto-publish to YouTube

---

## Troubleshooting

**Railway build fails**: Check `nixpacks.toml` — FFmpeg must install correctly.

**"No media found"**: Make sure Railway Volume is mounted at `/data`.

**Gemini 404 error**: Model name changed. Update `GEMINI_MODEL` env var to `gemini-2.5-flash`.

**YouTube auth**: Run locally once with `no_upload=false` to complete OAuth browser flow. Token saves to `/data/yt_token.pickle`.

**ElevenLabs voice**: Leave API key blank to use free gTTS. Find voice IDs at elevenlabs.io/voice-library.

---

## File Structure

```
petreel-studio/
├── backend/                  ← Deploy to Railway
│   ├── main.py               ← FastAPI server
│   ├── config.py             ← All settings + presets
│   ├── requirements.txt
│   ├── Procfile
│   ├── nixpacks.toml         ← FFmpeg installation
│   ├── railway.toml
│   ├── media_manager.py
│   └── pipeline/
│       ├── vision.py         ← Gemini Vision analysis
│       ├── planner.py        ← AI script with viral formulas
│       ├── designer.py       ← Canva replica: title cards, thumbnails
│       ├── tts_engine.py     ← gTTS + ElevenLabs voiceover
│       ├── video_engine.py   ← Ken Burns + transitions + assembly
│       └── uploader.py       ← YouTube Data API
│
└── frontend/                 ← Run locally (npm run dev)
    ├── src/
    │   ├── App.tsx           ← Studio dashboard
    │   └── api.ts            ← Railway API client
    ├── package.json
    └── .env.example
```
