# SHEtoken Data Engine — Maintenance Guide

> How to keep the data engine running, and how to do the one thing you'll
> actually do going forward: **enrich the data sources.** Pair this with
> `DATA_ENGINE_HANDOFF.md` (architecture) — this doc is the *operating manual*.

---

## 1. The rhythm — what runs without you

The engine is automated. In normal weeks you do **nothing**.

| When | What happens | Your job |
|---|---|---|
| Every Sunday | Weekly news agent runs (scans → classifies → moves WEI/SVI/WVI → loads Supabase → newsletter/social) | Glance at the Monday email + crisis alerts |
| 1st of month | Monthly pipeline regenerates all CSVs → commits → loads Supabase | Confirm the Action went green |
| On any commit | Railway redeploys the API (~2 min) | Nothing |
| Annually | Refresh baselines when WHO/UNESCO/UNODC publish new data | The big enrichment (see §3) |

**The only routine check:** once a month, open the Actions tab and confirm the
monthly + weekly workflows show green. If both are green, the engine is healthy.

---

## 2. The golden rules (these prevent every bug we've hit)

1. **CSVs are the source of truth.** Generators write them; Supabase and the API
   read them. Never edit a score directly in Supabase as a permanent fix — edit
   the generator, regenerate, reload.
2. **Two CSV folders must stay in sync.** Data lives in BOTH `data/output/` and
   `api/data/output/`. The monthly pipeline copies between them. Any **hand-added**
   file must be placed in BOTH, or the API won't see it. *(This caused a real bug.)*
3. **No exotic characters in CSVs.** Use plain ASCII `#` for comment lines (or no
   comments). A wrong hash character makes the loader silently parse 0 rows.
   *(This caused a real bug.)* Prefer generating CSVs over hand-typing them.
4. **Commit → Railway redeploys automatically.** To make code/data live, commit
   to GitHub and wait ~2 min. Check the Railway Deployments tab if unsure.
5. **Every new table needs its schema SQL run in Supabase** before the loader can
   write to it (`PGRST205 table not found` = schema not run).
6. **Label unverified data.** If a number is an estimate, mark it (`data_source`
   or `is_verified=false`). Never let an estimate masquerade as sourced.

---

## 3. Enriching data sources — your main task going forward

There are **two** kinds of data source. Know which one you're enriching.

### 3A. News sources (the weekly agent's eyes)

These feed the Sunday agent — more/better feeds = better weekly signals.

**Where:** `agent/config.py` → the `NEWS_SOURCES` list.

**Format:** each source is one tuple:
```python
("Display Name", "https://site.com/feed/rss.xml", "en", "India", "regional"),
#  name          RSS/Atom URL                      lang  country  scope
```
- `lang` — `en`, `hi`, `bn`, `ur`, `ar`, `pt`, `es`, etc. (the classifier handles these)
- `country` — country name or `global`
- `scope` — `global` or `regional`

**To add a source:**
1. Find the site's RSS/Atom feed URL (usually `site.com/feed/` or `/rss.xml`).
2. Add one tuple line to `NEWS_SOURCES`, in the right region block.
3. Commit. The next Sunday run picks it up automatically — no other change.

**To test a feed before trusting it:** `agent/test_sources.py` exists for this —
run it to check a feed returns articles.

**Good sources to prioritise:** women's-rights NGOs, gender desks of major
outlets, regional-language press (the more non-English, the better the global
coverage), UN/HRW/Equality Now-type bodies. Avoid low-quality aggregators.

### 3B. Indicator data (the numbers behind the indexes)

This is the "replace modeled estimates with verified data" path — the higher-value
enrichment. Each index is a generator with an embedded data table.

**Where:** `pipeline/data/generate_<index>.py` → a data table like:
```python
SV_DATA = [
#   country      iso   region    ...indicator values...   "source / note"
    ("Iceland",  "ISL","Europe", 14.0, 152, 60, ...,       "High reporting reflects strong legal framework"),
    ...
]
```

**To update/verify a country's numbers:**
1. Open the generator for that index.
2. Edit the values in that country's row. Update the note to cite the real source.
3. If it's an index with a `data_source`/verified flag (WHI, WVI, sex-ratio),
   flip the flag to "verified" for that row.
4. Run the generator (or the monthly pipeline) → it rewrites the CSV.
5. The monthly pipeline copies to `api/data/output/` and loads Supabase.

**To add a new country:** add a new tuple row with all indicator columns filled.
Keep the column order identical to the others.

**To add a new indicator (column):** this is bigger — you edit the generator's
`compute_*()` function (the weighting), the data tuples (add the value), and the
CSV header. Then update the matching Supabase schema (`db/*.sql`) to add the
column, and the loader's `select_cols` map. Tell your future self: adding a
column touches generator + schema + loader together.

### The priority enrichment backlog (unverified → verified)

| Data | Status | Fix |
|---|---|---|
| Sex ratio at birth | **Unverified estimates** | Replace with World Bank `SP.POP.BRTH.MF`; flip `is_verified` |
| WHI (health) | Modeled estimates | Verified WHO / DHS pulls per indicator |
| WVI (voice) | Modeled estimates | Verified V-Dem / GMMP / ILO pulls |

> **Turn hand-authored files into generators.** The sex-ratio file was typed by
> hand and caused two bugs (bad character, two-folder desync). The moment you have
> verified numbers, make it a `generate_sex_ratio.py` like the others — then it
> flows through the clean pipeline and can't have those problems again.

---

## 4. Common maintenance tasks (cookbook)

| I want to… | Do this |
|---|---|
| Add a news feed | Add a tuple to `NEWS_SOURCES` in `agent/config.py`, commit |
| Verify/update a country's score | Edit the generator's data table + note, run pipeline |
| Add a new country to an index | Add a tuple row to the generator, run pipeline |
| Add a whole new index | New `generate_*.py` + `db/schema_*.sql` + loader fn + API endpoint (the full pattern — see handoff §4) |
| Force a data refresh now | Actions → "Monthly Data Refresh" → Run workflow |
| Re-run just the Supabase load | Actions → "Load Data to Supabase" → Run workflow |
| Re-run the weekly agent | Actions → "Weekly News Agent" → Run workflow |
| Make an API change live | Commit to GitHub → Railway auto-redeploys (~2 min) |

---

## 5. Health checks (run these if something feels off)

**Are the workflows healthy?** Actions tab → both monthly + weekly green.

**Is the data in Supabase?**
```sql
select 'wei' t, count(*) from she_wei_countries
union all select 'svi', count(*) from she_svi_countries
union all select 'whi', count(*) from she_whi_countries
union all select 'wvi', count(*) from she_wvi_countries
union all select 'vital', count(*) from she_vital_stats
union all select 'srb', count(*) from she_sex_ratio_birth;
```
All non-zero.

**Is the API serving?** Open `https://api.shetoken.org/v1/summary` and `/docs`.

**Is a new CSV reaching the API?** Remember the two-folder rule — check the file
is in `api/data/output/`, not just `data/output/`.

---

## 6. Troubleshooting (symptom → cause → fix)

| Symptom | Cause | Fix |
|---|---|---|
| Loader: `PGRST205 table not found` | Schema SQL not run | Run the table's `db/*.sql` in Supabase |
| Loader: `[8x] … 0 rows` | CSV parse failed (bad comment char) or wrong folder | Use a clean ASCII/no-comment CSV; confirm path |
| API endpoint 404 | Route not deployed | Commit the route; check `/docs` after redeploy |
| New CSV not reflected in API | Only in `data/output/`, not `api/data/output/` | Copy to both folders |
| Supabase table empty after load | Loader not called in `main()`, or 0-rows parse | Confirm the call + the CSV parses |
| Stage/data missing but code is right | API reading CSV (not Supabase), or wrong folder | Set Railway `SUPABASE_URL`/`ANON_KEY`; sync folders |
| Weekly agent `[5b]` skipped | sister_updater error (non-fatal) | Check agent log; baseline CSV present? |
| Node 20 deprecation warning | GitHub runner update | Bump `checkout@v4→v5`, `setup-python@v5→v6`, `cache@v4→v5` |

---

## 7. The newsletter (optional enhancement)

The weekly newsletter (`agent/reporter/email_sender.py`) reports global WEI,
weekly signals, crisis alerts, and pillar movers — across three audience tiers
(founder / NGO / public). It does **not** yet surface the new SVI/WVI weekly
movements. It's not broken; it just doesn't show the newest data. If you want
the sister-index movers added to the email, that's a small edit to the report
builder — a worthwhile enhancement when convenient, not a maintenance need.

---

## 8. When to call for help vs DIY

**DIY (safe, routine):** adding news feeds, updating numbers in a generator,
re-running workflows, syncing CSVs.

**Get a hand (touches multiple files):** adding a whole new index, adding an
indicator column (generator + schema + loader together), changing the WEI
formula or weights, migrating more endpoints to Supabase.

The single most valuable enrichment you can do: **verify the three estimate
datasets (sex-ratio, WHI, WVI) against their real sources, one indicator at a
time, flipping the verified flag as you go.** That steadily turns the platform
from "modeled" to "sourced" — which is the whole credibility thesis.

---

*© 2026 SHE Foundation. Operating manual for the SHEtoken data engine.*
