# SHEtoken Anonymous Grievance & Support App
## Technical Specification + Privacy Architecture

---

## Purpose

Two distinct functions in one interface:

```
1. REPORT   → contribute to WEI community signal data
2. GET HELP → be routed to the right support resource immediately
```

The second function is more important than the first.
**A woman landing on this page may be in immediate danger.**
Help resources come first, always.

---

## User Flow

```
OPEN APP / shetoken.org/signal
         ↓
┌─────────────────────────────────┐
│  ARE YOU SAFE RIGHT NOW?        │
│                                 │
│  [ YES, I want to report ]      │
│  [ I NEED HELP NOW ]            │
└─────────────────────────────────┘
         ↓                    ↓
   REPORT FLOW           HELP FLOW
```

---

## HELP FLOW — Immediate Support Routing

If a woman selects "I NEED HELP NOW":

```
SELECT YOUR COUNTRY
         ↓
SELECT SITUATION
  □ Domestic violence / unsafe at home
  □ Forced marriage / child marriage
  □ Sexual assault
  □ Honour-based threat
  □ Trafficking
  □ Acid attack
  □ Other
         ↓
IMMEDIATE RESOURCES shown:
  - National emergency number
  - DV helpline (free, confidential)
  - Nearest shelter (if available)
  - Legal aid number
  - Online chat support

All resources verified and updated monthly.
```

### India Crisis Resources
| Situation | Resource | Number |
|---|---|---|
| Any emergency | Police | 100 |
| Women in distress | Women Helpline | 1091 |
| Domestic violence | NCW Helpline | 7827170170 |
| Child marriage | Childline | 1098 |
| Trafficking | Anti-trafficking | 1800-419-8588 |
| Acid attack | Chhanv Foundation | +91-9582-908080 |

---

## REPORT FLOW — Anonymous Signal Collection

### What the user sees

```
Step 1: SELECT ISSUE TYPE (dropdown, no free text)
  □ Domestic violence
  □ Sexual assault / harassment
  □ Period poverty / school
  □ Forced marriage / child marriage
  □ Online harassment
  □ Dowry pressure
  □ Honour-based threat
  □ Denied education
  □ Denied employment
  □ Property / inheritance dispute
  □ Widowhood property stripping
  □ Trafficking / forced labour
  □ FGM / harmful practice
  □ Other

Step 2: LOCATION (country + state only, NOT address)
  Select country → Select state/province

Step 3: TIMEFRAME
  □ This week
  □ This month
  □ Past 3 months

Step 4: STATUS
  □ Reported to police
  □ Wanted to report but afraid to
  □ Did not report — reason:
       □ Fear of retaliation
       □ Police won't help
       □ Family pressure
       □ Don't know how
       □ Stigma / shame
  □ Already safe
  □ Ongoing

Step 5: SUBMIT (one button, no account required)
```

### What we DO NOT collect
- ❌ IP address (checked for rate limiting, then immediately discarded)
- ❌ Device ID or fingerprint
- ❌ Name, age, or any personal information
- ❌ Address or specific location (country + state only)
- ❌ Free text (protects against accidental PII)
- ❌ Photos or files
- ❌ Time of day (only week/month)

### What IS recorded (aggregate only)
```json
{
  "issue_type": "domestic_violence",
  "country":    "IND",
  "state":      "WB",
  "week":       "2026-W19",
  "reported_to_police": false,
  "reason_not_reported": "fear_of_retaliation",
  "status":     "ongoing"
}
```

---

## Privacy Architecture

### No individual record ever exists

```
User submits → Immediate aggregation → Raw record deleted
                    ↓
           Weekly count stored:
           {country: IND, state: WB,
            issue: DV, week: 2026-W19,
            count: 47, reported_to_police: 12}
```

### Rate limiting without tracking
```python
# Check rate limit using short-lived hash
# Hash is not stored after check
import hashlib, time

def check_rate_limit(request_ip):
    # Hash IP with rotating daily salt — cannot be reversed
    daily_salt = str(int(time.time() / 86400))
    ip_hash    = hashlib.sha256(f"{request_ip}{daily_salt}".encode()).hexdigest()[:12]
    # Check in-memory rate limit store (Redis with 24hr TTL)
    # If over limit: reject
    # IP never stored anywhere — only the hash with 24hr expiry
    ...
```

### Proof of human (no account needed)
- Invisible reCAPTCHA v3 (scores 0-1, threshold 0.5)
- Honeypot field (bots fill it, humans don't see it)
- Time-on-page check (too fast = bot)

---

## How It Feeds Into WEI

```
Community signals (10% weight in Violence Penalty pillar)
         ↓
Aggregated weekly by country/state/issue
         ↓
Three-source triangulation:
  Official data (NCRB, UNODC): 70%
  NGO verified data:           20%
  Community signals:           10%
         ↓
Sustained signals (3+ weeks) → quarterly WEI adjustment
Crisis spike (300%+) → DAO governance vote
```

The **reporting gap indicator** is the most powerful output:
```
Reporting Gap = (Community signal rate - Official rate) / Community signal rate

High gap = women experiencing violence but not reporting to police
High gap = fear, stigma, institutional failure
High gap = increases the Violence Penalty score
```

---

## The "Reasons for Not Reporting" Data

This is data no government collects and no index tracks.
It tells you *why* women don't report — which determines *which* policy to fund:

| Reason | Policy intervention |
|---|---|
| Fear of retaliation | Safe house / shelter expansion |
| Police won't help | Police gender training + female officers |
| Family pressure | Community awareness + legal protection |
| Stigma / shame | Education + community norms programs |
| Don't know how | Legal aid awareness campaigns |

---

## Period Poverty Module

Special section within the app for girls/women to report period poverty:

```
SELECT (checkboxes — multiple allowed):
  □ Cannot afford sanitary products
  □ School has no female toilet
  □ School has no changing area
  □ Missed school this month due to period
  □ Used unsafe alternative (cloth/other)
  □ Restricted from activities during period (cultural)
  □ Experienced stigma related to menstruation

SELECT: Country + State + Week
SUBMIT (anonymous)
```

This data feeds directly into:
- Bodily Autonomy pillar (period poverty sub-indicator)
- Education pillar (school attendance)
- School Dropout Causes tracker

---

## Tech Stack

```
Frontend:  React (Lovable-built) or simple HTML form
Backend:   FastAPI endpoint: POST /v1/signal/submit
Database:  Supabase (aggregated counts only, no individual rows)
Rate limit: Redis (IP hashes with 24hr TTL, then deleted)
CAPTCHA:   Google reCAPTCHA v3 (invisible)
```

### API endpoint
```
POST /v1/signal/submit
{
  "issue_type":           "domestic_violence",
  "country":              "IND",
  "state":                "WB",
  "timeframe":            "this_week",
  "reported_to_police":   false,
  "reason_not_reported":  "fear_of_retaliation",
  "status":               "ongoing",
  "captcha_token":        "03AGdBq25..."   // verified server-side
}

Response:
{
  "status": "received",
  "message": "Thank you. Your report has been recorded anonymously.",
  "resources": [
    {"name": "Women Helpline India", "number": "1091", "free": true},
    {"name": "NCW DV Helpline",      "number": "7827170170", "free": true}
  ]
}
```

---

## One Non-Negotiable Design Rule

**Every page in the app, at every step, shows:**

```
┌─────────────────────────────────────────────┐
│ Need help right now?                        │
│ Women's Helpline: 1091 (India)              │
│ International: findahelpline.com            │
└─────────────────────────────────────────────┘
```

This cannot be removed, minimised, or scrolled past.
A woman filling out this form may be doing it while in danger.

---

*© 2026 SHE Foundation*
*Privacy architecture reviewed by [Digital Safety Org to be confirmed]*
