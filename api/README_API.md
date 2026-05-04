# SHEtoken WEI API

REST API serving live WEI scores, state data, and weekly signals.
Built with FastAPI — auto-generates interactive docs at `/docs`.

---

## Run Locally (in 30 seconds)

```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Open: http://localhost:8000/docs

---

## Key Endpoints

| Endpoint | Returns |
|---|---|
| `GET /v1/summary` | Dashboard stats — global WEI, counts, latest signals |
| `GET /v1/wei/countries` | All 105 country WEI scores |
| `GET /v1/wei/countries/{iso}` | Single country detail (e.g. `/IND`) |
| `GET /v1/wei/states/{country}` | State scores (india/usa/brazil/nigeria/mexico/pakistan) |
| `GET /v1/wei/states/{country}/{code}` | Single state (e.g. `/india/WB`) |
| `GET /v1/wei/leaderboard` | Top performers or fastest movers |
| `GET /v1/signals/latest` | This week's classified news signals |
| `GET /v1/signals/pillar-summary` | Signal strength by pillar |
| `GET /v1/signals/top-movers` | Most active regions this week |
| `GET /v1/token` | SHE token info and mechanics |

---

## Connect Lovable to This API

### Step 1 — Deploy the API (free options)

**Option A — Railway (easiest, free tier)**
1. Go to railway.app → New Project → Deploy from GitHub
2. Select your `shetoken_repo` repo
3. Set Root Directory to `api`
4. Railway auto-detects the Dockerfile and deploys
5. Your API URL: `https://shetoken-api-production.up.railway.app`

**Option B — Render (also free)**
1. Go to render.com → New Web Service
2. Connect GitHub repo
3. Root directory: `api`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Option C — Google Cloud Run**
```bash
cd api && ./deploy_api.sh
```

### Step 2 — Tell Lovable your API URL

In Lovable, open the chat and paste this prompt:

```
Connect to the SHEtoken WEI API at:
  https://YOUR-API-URL

Use these endpoints to populate the site:

Homepage hero:
  GET /v1/summary
  → global_wei_score, countries_scored, latest_signals_count

Global leaderboard table:
  GET /v1/wei/countries?limit=20
  → data array with country, wei_score, tier, ticker

India states section:
  GET /v1/wei/states/india
  → data array with state, wei_score, change, hot, key_programs

Weekly signals feed:
  GET /v1/signals/latest?limit=10
  → data array with pillar, direction, summary_en, country

Token info:
  GET /v1/token
  → name, ticker, mechanics

Refresh all data every 5 minutes using setInterval.
Show a loading skeleton while fetching.
Add error handling if API is unreachable.
```

### Step 3 — Lovable code example

Lovable generates React. Here's the fetch pattern it will use:

```javascript
// In your Lovable component
const [countries, setCountries] = useState([])
const API = "https://your-api-url"

useEffect(() => {
  fetch(`${API}/v1/wei/countries?limit=20`)
    .then(r => r.json())
    .then(({ data }) => setCountries(data))
}, [])
```

---

## CORS

The API is open (`allow_origins=["*"]`) — any website including Lovable
can call it directly from the browser. No API key needed for public endpoints.

---

## Deploy to Multiple Environments

```
Local dev:    http://localhost:8000
Railway:      https://shetoken-api-production.up.railway.app
Cloud Run:    https://shetoken-api-xxxxxx-uc.a.run.app
Custom domain: https://api.shetoken.org
```

Set `VITE_API_URL` in your Lovable `.env` to switch environments.

---

*© 2026 SHE Foundation. MIT License.*
