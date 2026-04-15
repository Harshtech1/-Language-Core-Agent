# 语言核心 // Language Core Agent
> **730-Day Autonomous HSK 1-4 Tutor** — powered by Claude Sonnet (lessons) + Gemini Flash Lite (evaluations)

---

## Architecture

```
monorepo/
├── api/                    # FastAPI backend (Render Free Tier)
│   ├── core/
│   │   ├── db.py           # Motor async MongoDB client
│   │   ├── openrouter.py   # Dual-model LLM calls
│   │   ├── srs.py          # SM-2 spaced repetition engine
│   │   └── telegram.py     # Message formatters + send_message()
│   ├── models/
│   │   └── user_state.py   # Pydantic schemas
│   └── routes/
│       ├── cron.py         # /cron/daily-word, /cron/evening-quiz, /webhook/telegram
│       ├── vocab.py        # /vocab, /vocab/{hanzi}
│       └── stats.py        # /stats/overview
├── workers/
│   ├── seed_hsk.py         # One-time database seeder (HSK 1-4)
│   └── telegram_bot.py     # Standalone webhook proxy (port 8001)
└── web/                    # Next.js 14 dashboard (Vercel)
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx         # Dashboard: Word of the Day + Stats
    │   └── globals.css      # OKLCH design tokens
    └── components/
        ├── ThreeBackground.tsx  # Drifting Hanzi starfield + mouse parallax
        ├── WordCard.tsx         # Today's word with etymology
        ├── StatsRing.tsx        # Streak / mastery telemetry
        └── MasteryTree.tsx      # Vocabulary node visualization
```

---

## Quick Start

### 1. Prerequisites

```bash
# Python 3.11+
pip install -r api/requirements.txt

# Node 18+
cd web && npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your secrets:

```bash
cp .env.example .env
```

| Variable | Where to get it |
|---|---|
| `MONGODB_URI` | MongoDB Atlas → Connect → Drivers → copy connection string |
| `OPENROUTER_API_KEY` | openrouter.ai → Keys |
| `TELEGRAM_BOT_TOKEN` | @BotFather on Telegram → `/newbot` |
| `TELEGRAM_ALLOWED_CHAT_IDS` | Comma-separated IDs (e.g. `123,456`) from @userinfobot |
| `CRON_SECRET` | Any random string, e.g. `openssl rand -hex 16` |

### 3. Seed the Database (run once)

```bash
python -m workers.seed_hsk
```

Expected output:
```
[seed] Connecting to MongoDB: mongodb+srv://...
[seed] Connection OK.
[seed] Using embedded list: 68 words (add workers/data/hsk_wordlist.json for full 1,200-word list)
[seed] Done! Inserted 68 vocab entries, 68 SRS states.
[seed] Indexes created on vocabulary and word_states.
```

### 4. Start the API

```bash
# From repo root
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Verify:
```bash
curl http://localhost:8000/health
# → {"status":"operational","agent":"语言核心","version":"0.1.0"}
```

### 5. Start the Dashboard

```bash
cd web && npm run dev
# → http://localhost:3000
```

### 6. Register Telegram Webhook (production)

```bash
# Replace with your actual Render URL
python -m workers.telegram_bot --webhook-url https://hsk-agent.onrender.com/telegram/update
```

---

## Manual Trigger Commands (for testing)

Use these `curl` commands to fire each cron event without waiting for the scheduler.

> Replace `YOUR_CRON_SECRET` with the value in your `.env`.
> For local testing, host is `http://localhost:8000`.

---

### ☀️ Morning Lesson Push (08:00 IST)

Generates the daily lesson via Claude Sonnet and delivers it to your Telegram:

```bash
curl -X POST http://localhost:8000/cron/daily-word \
  -H "x-cron-secret: YOUR_CRON_SECRET" \
  -H "Content-Type: application/json"
```

**Expected response:**
```json
{"status": "success", "word": "爱", "model": "anthropic/claude-3.5-sonnet"}
```

---

### 🌙 Evening Quiz Push (20:00 IST)

Sends the quiz prompt for today's word to Telegram:

```bash
curl -X POST http://localhost:8000/cron/evening-quiz \
  -H "x-cron-secret: YOUR_CRON_SECRET" \
  -H "Content-Type: application/json"
```

**Expected response:**
```json
{"status": "success", "word": "爱"}
```

---

### 📊 Check Stats (Dashboard API)

```bash
curl http://localhost:8000/stats/overview | python -m json.tool
```

---

### 📚 Browse Vocabulary

```bash
# All words, page 1
curl "http://localhost:8000/vocab?page=1&per_page=10"

# Filter by HSK level
curl "http://localhost:8000/vocab?hsk_level=1"

# Single word detail
curl "http://localhost:8000/vocab/爱"
```

---

### 🧪 Simulate a Telegram User Reply (test evaluation)

This mimics what Telegram sends when you reply to the evening quiz:

```bash
curl -X POST http://localhost:8000/webhook/telegram \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "text": "我很爱我的家人。",
      "chat": {"id": "YOUR_CHAT_ID"},
      "from": {"first_name": "Harsh"}
    }
  }'
```

---

## Render Deployment

1. Push to GitHub
2. On Render: **New Web Service** → connect repo
   - **Runtime:** Python
   - **Build command:** `pip install -r api/requirements.txt`
   - **Start command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
3. Add all `.env` variables in Render → Environment tab
4. Set up two Cron Jobs (Render → New Cron Job):
   - `0 2 * * *` IST = `0 2 30 * * *` UTC → `curl -X POST $API_URL/cron/daily-word -H "x-cron-secret: $CRON_SECRET"`
   - `0 14 * * *` IST = `0 14 30 * * *` UTC → `curl -X POST $API_URL/cron/evening-quiz -H "x-cron-secret: $CRON_SECRET"`

> **Note:** Render Free Tier has a 30-second cold start. This is acceptable for scheduled cron jobs that run at fixed times.

---

## Vercel Dashboard Deployment

```bash
cd web
npx vercel --prod
```

Set `API_URL` environment variable in Vercel project settings to your Render API URL.

---

## SRS Algorithm

The agent uses a modified **SuperMemo-2** algorithm:

| Quality (0–5) | Description | Result |
|---|---|---|
| 5 | Perfect | Interval × EF, EF increases |
| 4 | Hesitation | Interval × EF, EF slightly increases |
| 3 | Difficult correct | Interval × EF, EF unchanged |
| 2 | Incorrect but familiar | Reset to interval=1, EF drops |
| 1 | Incorrect | Reset to interval=1, EF drops more |
| 0 | Blackout | Reset to interval=1, EF drops to floor |

- **EF floor:** 1.3 (cards never become impossible)
- **Interval cap:** 365 days (even mastered words get yearly review)
- **Overdue handling:** Cards past their `next_review` date are surfaced first; the SM-2 calculation still uses current state, so missing a day doesn't reset progress — it just delays the next review.

---

## Cost Estimate (daily)

| Operation | Model | Est. tokens | Est. cost |
|---|---|---|---|
| Morning lesson (1/day) | claude-3.5-sonnet | ~800 in / ~600 out | ~$0.014 |
| Evening evaluation (1/day) | gemini-3.1-flash-lite | ~400 in / ~200 out | ~$0.0004 |
| **Total** | | | **~$0.015/day = ~$0.45/month** |

---

## Manual Database Overrides (Safety Valve)

If the LLM incorrectly grades a valid sentence or you want to manually reset/fast-forward a word's SRS state, you can use the MongoDB shell (or Atlas UI):

### 1. Override a Specific Word's Mastery
```javascript
// Set a word to "Mastered" (long interval)
db.word_states.updateOne(
  { hanzi: "你好" },
  { $set: { 
      interval: 100, 
      repetitions: 5, 
      ease_factor: 2.8,
      status: "evaluated",
      next_review: "2026-12-31" 
  }}
)
```

### 2. Reset a Streak
```javascript
db.word_states.updateOne(
  { hanzi: "把握" },
  { $set: { streak: 0, interval: 1, repetitions: 0 }}
)
```

---

## Production Security

The system includes a **Global Safety Valve** in `api/main.py`. 
All routes starting with `/cron/` require a valid `x-cron-secret` header.

To verify your production security:
```bash
# This should FAIL with 401 Unauthorized
curl -X POST https://your-app.onrender.com/cron/daily-word

# This should SUCCEED
curl -X POST https://your-app.onrender.com/cron/daily-word -H "x-cron-secret: YOUR_SECRET"
```

---

加油! 💪
