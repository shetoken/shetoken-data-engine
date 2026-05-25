# SHEtoken API Reference
## WEI Data API — Technical Documentation

> The SHEtoken WEI API provides programmatic access to Women's Empowerment Index scores, token supply data, and program milestone submissions. Read endpoints are public and keyless at a basic rate limit; free and paid tokens unlock higher daily quotas (see Authentication & Tiers).

---

## Base URL

```
https://api.shetoken.org/v1
```

---

## Authentication & Tiers

The API is **public and keyless at a basic rate limit** — you can call read
endpoints with no token at all. Tokens unlock higher daily quotas.

| Tier | Token? | Limit | How to get it |
|---|---|---|---|
| **Public** | none | 60 requests/min per IP | Just call the API |
| **Free** | yes | 5,000 requests/day | Email contact@shetoken.org |
| **Paid** | yes | 100,000 requests/day | Email contact@shetoken.org |
| **Admin** | yes | Unlimited | Internal only |

**Using a token:**
```
Authorization: Bearer YOUR_TOKEN
```
(or, for quick browser testing, append `?token=YOUR_TOKEN`)

**Rate-limit headers** are returned on every response:
```
X-RateLimit-Tier:       public | free | paid | admin
X-RateLimit-Limit:      <your limit>
X-RateLimit-Remaining:  <calls left>
```

**When you exceed your limit** you receive HTTP `429` with a JSON body
explaining the limit and how to upgrade. Public callers get a per-minute
window; token holders get a daily quota.

Write endpoints (government and NGO data submission) always require a token.

---

## Endpoints

### WEI Scores

#### GET /wei/global

Returns the current global WEI score and year-over-year change.

```bash
curl https://api.shetoken.org/v1/wei/global
```

**Response:**
```json
{
  "score": 54.2,
  "previous_score": 52.8,
  "change": 1.4,
  "year": 2025,
  "last_updated": "2025-05-01",
  "status": "final"
}
```

---

#### GET /wei/countries

Returns WEI scores for all countries.

```bash
curl https://api.shetoken.org/v1/wei/countries
```

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `tier` | integer | Filter by tier (1, 2, 3, or 4) |
| `sort` | string | Sort by `score`, `change`, or `name` |
| `order` | string | `asc` or `desc` |
| `limit` | integer | Number of results (default 50, max 200) |

**Response:**
```json
{
  "count": 195,
  "data": [
    {
      "country": "Iceland",
      "iso_code": "ISL",
      "ticker": "SHE-ISL",
      "score": 84.3,
      "previous_score": 83.1,
      "change": 1.2,
      "tier": 1,
      "year": 2025
    },
    ...
  ]
}
```

---

#### GET /wei/countries/:iso_code

Returns detailed WEI score for a specific country including pillar breakdown.

```bash
curl https://api.shetoken.org/v1/wei/countries/IND
```

**Response:**
```json
{
  "country": "India",
  "iso_code": "IND",
  "ticker": "SHE-IND",
  "score": 48.6,
  "previous_score": 47.2,
  "change": 1.4,
  "tier": 2,
  "year": 2025,
  "pillars": {
    "empowerment": {
      "score": 52.1,
      "weight": 0.25,
      "contribution": 13.0
    },
    "education": {
      "score": 61.4,
      "weight": 0.20,
      "contribution": 12.3
    },
    "economic": {
      "score": 44.8,
      "weight": 0.20,
      "contribution": 8.96
    },
    "health": {
      "score": 58.2,
      "weight": 0.15,
      "contribution": 8.73
    },
    "crime_penalty": {
      "score": 38.6,
      "weight": 0.20,
      "deduction": 7.72
    }
  },
  "data_sources": ["NCRB", "UNESCO", "World Bank", "ILO", "WHO"]
}
```

---

#### GET /wei/states

Returns WEI scores for all registered Indian states.

```bash
curl https://api.shetoken.org/v1/wei/states
```

**Response:**
```json
{
  "count": 6,
  "data": [
    {
      "state": "Kerala",
      "code": "KL",
      "ticker": "SHE-KL",
      "score": 74.2,
      "previous_score": 72.1,
      "change": 2.1,
      "verified": true,
      "update_frequency": "quarterly"
    },
    {
      "state": "West Bengal",
      "code": "WB",
      "ticker": "SHE-WB",
      "score": 68.9,
      "previous_score": 65.5,
      "change": 3.4,
      "verified": true,
      "update_frequency": "quarterly",
      "hot": true
    },
    ...
  ]
}
```

---

#### GET /wei/states/:state_code

Returns detailed WEI score for a specific Indian state.

```bash
curl https://api.shetoken.org/v1/wei/states/WB
```

---

#### GET /wei/leaderboard

Returns the top 10 fastest-improving countries or states.

```bash
curl https://api.shetoken.org/v1/wei/leaderboard?type=states&limit=10
```

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `type` | string | `countries` or `states` |
| `metric` | string | `change` (default) or `score` |
| `limit` | integer | Number of results (default 10) |

---

### Sister Indexes

All sister-index endpoints follow the same shape: a list endpoint returns all
scored countries, and `/{iso_code}` returns one. All are 0–100.

| Endpoint | Index | Direction |
|---|---|---|
| `GET /gpi` · `/gpi/:iso` | Gender Poverty Index (9 dimensions) | higher = better |
| `GET /svi` · `/svi/:iso` | Sexual Violence Index (WHO prevalence) | higher = better |
| `GET /wevi` · `/wevi/:iso` | Widow & Elderly Vulnerability Index | higher = more vulnerable |
| `GET /wadi` · `/wadi/:iso` | Women's AI Displacement Index | higher = more exposed |
| `GET /whi` · `/whi/:iso` | Women's Health Index (mental, anaemia, menstrual, contraception) | higher = better |
| `GET /wvi` · `/wvi/:iso` | Women's Voice Index (online GBV, media, tech, civil society) | higher = better |
| `GET /compliance/countries` · `/{iso}` | Corporate Compliance Score (WRBCS) | higher = safer to source |

```bash
curl https://api.shetoken.org/v1/whi
curl https://api.shetoken.org/v1/wvi/IND
```

> WHI and WVI currently return transparent modeled estimates — each record
> includes a `data_source` field indicating modeled vs verified.

---

### Token Supply
#### GET /token/supply

Returns current token supply statistics.

```bash
curl https://api.shetoken.org/v1/token/supply
```

**Response:**
```json
{
  "total_supply": 1000000000,
  "circulating_supply": 412500000,
  "impact_fund_balance": 256000000,
  "reserve_balance": 98000000,
  "total_minted": 15000000,
  "total_burned": 2500000,
  "last_mint_event": {
    "date": "2025-05-01",
    "amount": 14000000,
    "reason": "Global WEI +1.4 points"
  },
  "last_burn_event": null
}
```

---

#### GET /token/events

Returns history of all minting and burning events.

```bash
curl https://api.shetoken.org/v1/token/events
```

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `type` | string | `mint`, `burn`, or `all` |
| `from_date` | string | ISO date (YYYY-MM-DD) |
| `to_date` | string | ISO date (YYYY-MM-DD) |

**Response:**
```json
{
  "events": [
    {
      "date": "2025-05-01",
      "type": "mint",
      "amount": 14000000,
      "wei_change": 1.4,
      "destination": "impact_fund",
      "tx_hash": "0x..."
    },
    ...
  ]
}
```

---

### Programs & NGOs

#### GET /programs

Returns all registered NGO programs.

```bash
curl https://api.shetoken.org/v1/programs
```

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `pillar` | string | Filter by WEI pillar |
| `country` | string | ISO country code |
| `state` | string | India state code |
| `verified` | boolean | Filter by verification status |

---

#### GET /programs/:program_id

Returns details and milestone status for a specific program.

```bash
curl https://api.shetoken.org/v1/programs/JEEViKA-BR-001
```

**Response:**
```json
{
  "id": "JEEViKA-BR-001",
  "name": "JEEViKA",
  "state": "Bihar",
  "pillar": "economic",
  "verified": true,
  "beneficiaries": 5200000,
  "milestones": [
    {
      "id": "M1",
      "description": "100,000 new SHG members",
      "target": 100000,
      "achieved": 100000,
      "status": "completed",
      "tokens_released": 500000,
      "verified_date": "2025-03-15"
    },
    {
      "id": "M2",
      "description": "₹1,000 crore in bank credit",
      "target": 100000000000,
      "achieved": 72000000000,
      "status": "in_progress",
      "tokens_released": 0
    }
  ]
}
```

---

### Government Data Submission

#### POST /submit/government

Submit verified program data as a registered government body.

**Requires API key.**

```bash
curl -X POST https://api.shetoken.org/v1/submit/government \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "state_code": "WB",
    "quarter": "Q1-2026",
    "programs": [
      {
        "name": "Lakshmi Bhandar",
        "pillar": "economic",
        "beneficiaries": 24500000,
        "data_source": "State Government Portal",
        "verification_body": "NABARD",
        "notes": "Beneficiary count as of March 2026"
      }
    ]
  }'
```

**Response:**
```json
{
  "submission_id": "GOV-WB-Q1-2026-001",
  "status": "received",
  "review_period_ends": "2026-04-15",
  "message": "Your data has been received and will be reviewed within 15 days."
}
```

---

### NGO Milestone Submission

#### POST /submit/milestone

Submit milestone completion data as a registered NGO.

**Requires API key.**

```bash
curl -X POST https://api.shetoken.org/v1/submit/milestone \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "program_id": "JEEViKA-BR-001",
    "milestone_id": "M2",
    "achieved_value": 100000000000,
    "evidence_url": "https://jeevika.bih.nic.in/annual-report-2026.pdf",
    "verification_source": "NABARD audit report"
  }'
```

---

## Error Codes

| Code | Meaning |
|---|---|
| `200` | Success |
| `400` | Bad request — check your parameters |
| `401` | Unauthorised — invalid or missing API key |
| `404` | Resource not found |
| `422` | Validation error — data format issue |
| `429` | Rate limit exceeded |
| `500` | Server error — contact support |

---

## Rate Limits

| Endpoint Type | Limit |
|---|---|
| Public read endpoints | 100 requests / minute |
| Authenticated write endpoints | 10 requests / minute |
| Bulk data downloads | 5 requests / hour |

---

## Data Formats

- All dates: ISO 8601 (`YYYY-MM-DD`)
- All scores: Float, rounded to 1 decimal place
- All token amounts: Integer (no decimals)
- All monetary values: Integer in smallest currency unit

---

## Changelog

| Version | Date | Changes |
|---|---|---|
| v1.0 | May 2026 | Initial API launch |

---

**Questions or issues?**
📧 contact@shetoken.org
💻 [github.com/shetoken/issues](https://github.com/shetoken/issues)
