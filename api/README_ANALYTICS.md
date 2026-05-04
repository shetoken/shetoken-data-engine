# SHEtoken API — Analytics Setup

## What Gets Tracked

Every API call is recorded with:
- Which endpoint was called
- How many times
- Response time (ms)
- Status code (200, 404, 500 etc.)
- Date and week

## Check Your Stats Right Now

Once deployed, visit:
```
https://api.shetoken.org/v1/admin/stats
```

Returns:
```json
{
  "total_calls": 1842,
  "uptime_hours": 24.3,
  "calls_per_hour": 75.8,
  "unique_endpoints": 12,
  "top_endpoints": [
    {
      "endpoint": "/v1/wei/countries",
      "total_calls": 432,
      "avg_response_ms": 48.2,
      "error_rate_pct": 0.0,
      "last_called": "2026-05-04T..."
    },
    ...
  ]
}
```

## Three Backend Options

### Option A — Memory (default, zero setup)
```
ANALYTICS_BACKEND=memory
```
- Works immediately, no setup
- Resets when API redeploys
- Good for: checking today's traffic

### Option B — Supabase (recommended, free)
Permanent storage. See all calls ever made. Query by date, endpoint, week.

**Setup (5 minutes):**

1. Go to supabase.com → New Project (free tier)

2. Open SQL Editor and run:
```sql
create table api_calls (
  id            bigserial primary key,
  endpoint      text not null,
  status_code   integer,
  duration_ms   float,
  called_at     timestamptz default now(),
  week          text,
  date          text
);

-- Index for fast queries
create index on api_calls (endpoint);
create index on api_calls (date);
create index on api_calls (week);
```

3. Go to Settings → API → copy URL and anon key

4. Add to your `.env`:
```
ANALYTICS_BACKEND=supabase
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
```

5. In Supabase Table Editor you can now see every API call in a table.
   Filter by date, sort by endpoint, export to CSV.

**Useful Supabase queries:**
```sql
-- Calls per endpoint this week
select endpoint, count(*) as calls
from api_calls
where date >= current_date - 7
group by endpoint
order by calls desc;

-- Calls per day (last 30 days)
select date, count(*) as calls
from api_calls
where called_at > now() - interval '30 days'
group by date
order by date;

-- Slowest endpoints
select endpoint, avg(duration_ms) as avg_ms, count(*) as calls
from api_calls
group by endpoint
order by avg_ms desc;

-- Error rate
select endpoint,
  count(*) as total,
  sum(case when status_code >= 400 then 1 else 0 end) as errors
from api_calls
group by endpoint;
```

### Option C — File (simplest)
```
ANALYTICS_BACKEND=file
```
Writes to `analytics_log.jsonl` in the api/ folder.
Each line is one API call as JSON.
Good for: local development, small traffic.

## Railway Built-in Metrics (no code needed)

Railway also shows:
- Request volume chart
- Response time p50/p95/p99
- Error rate

At: railway.app → your project → Metrics

## Weekly Check (2 minutes)

Every Monday, open:
```
https://api.shetoken.org/v1/admin/stats
```

Or if using Supabase, open the table and filter by this week.

What to look for:
- Is total_calls growing? (good sign — people using it)
- Any endpoints with error_rate > 5%? (something broken)
- Any endpoint with avg_response_ms > 500? (too slow, needs caching)
- Which endpoints are called most? (tells you what Lovable uses most)
