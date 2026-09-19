# EXHIBIT A — JMail Explorer

Scraper, indexer, and investigative web UI for the [jmail.world](https://jmail.world) Epstein email archive.

Scrapes all 7,545 threads (15,188 messages) with full email bodies, indexes them into SQLite with FTS5 full-text search, entity extraction, and communication graph analysis, then serves a React frontend designed as a "leaked classified archive viewer."

## Quick Start

```bash
# 1. Install Python deps
pip install aiohttp fastapi uvicorn

# 2. Scrape (~60s, writes ~/Downloads/jmail_threads.jsonl, 106MB)
python scraper.py

# 3. Ingest into SQLite (~3s, writes jmail.db, 137MB)
python ingest.py

# 4. Build frontend
cd frontend && npm install && npm run build && cd ..

# 5. Serve
uvicorn server:app --host 0.0.0.0 --port 8000
# Open http://localhost:8000
```

The scraper supports resume — re-run after a crash and it picks up where it left off.

## Frontend

### Design Concept: "EXHIBIT A"

The interface is designed to feel like you've gained unauthorized access to a government evidence database. Every surface communicates: *this data was never meant to be seen.*

**Visual language:**
- Redacted government documents (black bars, stamp marks, heavy censorship aesthetic)
- Evidence room filing systems (manila folders, evidence tags, case numbers)
- Surveillance camera feeds (timestamps, film grain, scanlines, vignette)
- Court exhibit labels (stamped text, monospace, bureaucratic typography)

**Color palette:** Blood red (`#8b0000`) + evidence yellow (`#c4a000`) + bone white (`#c8b89a`) on near-black (`#050505`)

**Typography:** Special Elite (typewriter headers), IBM Plex Mono (data/metadata), Crimson Pro (email body text)

**Atmospheric effects (CSS-only):** Film grain (SVG turbulence), CRT scanlines, corner vignette, surveillance clock flicker, glitch-on-hover

### Views

| View | Sidebar Label | Description |
|------|---------------|-------------|
| **Search** | QUERY DATABASE | FTS5 full-text search across 15K messages with highlighted snippets, evidence tags, pagination |
| **Thread Reader** | *(overlay)* | Full-screen evidence overlay — case file header, individual message cards, Epstein flags, HTML email rendering |
| **Network Graph** | NETWORK ANALYSIS | D3 force-directed graph of communication patterns. Surveillance grid background, filterable by edge weight/node count |
| **Entities** | SUBJECT FILES | Government database table of 1,134 known entities with dossier drill-down, connections, recent messages |
| **Timeline** | TEMPORAL ANALYSIS | D3 bar chart of message volume by month (2002–2019). Click a bar to search that month |
| **Stats** | CLASSIFIED BRIEFING | Dashboard with aggregate counts, top senders, top domains. "CONFIDENTIAL" watermark |

### Keyboard Shortcuts

- `Cmd+K` or `/` — Focus search, switch to search view
- `Escape` — Close thread overlay

### Tech Stack

- **Vite 6** + **React 19** + **TypeScript**
- **D3.js v7** (force graph, timeline chart)
- **Plain CSS** — no Tailwind, no UI library (the custom aesthetic demands it)
- **Google Fonts** — Special Elite, IBM Plex Mono, Crimson Pro

### Development

```bash
# Terminal 1: Backend
uvicorn server:app --host 0.0.0.0 --port 8000

# Terminal 2: Vite dev server (HMR, proxies /api to :8000)
cd frontend && npm run dev
# Open http://localhost:5173
```

### Production Build

```bash
cd frontend && npm run build   # outputs frontend/dist/
# server.py auto-detects and serves frontend/dist when present
```

## Architecture

```
scraper.py          aiohttp async scraper, 40 concurrent requests
                      |
                      v
              jmail_threads.jsonl     one JSON object per thread per line (106MB)
                      |
                      v
ingest.py           reads JSONL -> SQLite (FTS5 + entity graph + timeline)
                      |
                      v
                  jmail.db            137MB, 6 tables + 1 FTS virtual table
                      |
                      v
server.py           FastAPI, 9 endpoints
                      |
                      v
frontend/           React + TypeScript + D3.js
  src/
    App.tsx         View routing, keyboard shortcuts, thread state
    api.ts          Typed fetch wrappers for all API endpoints
    types.ts        TypeScript interfaces matching API responses
    utils.ts        Avatar colors, date formatting, exhibit IDs
    styles/         global.css, effects.css, typography.css
    components/
      Layout/       Shell (grain/scanlines/vignette), Sidebar, SurveillanceClock
      Search/       SearchView, ResultCard
      Thread/       ThreadOverlay, ThreadHeader, MessageCard
      Network/      NetworkView, useForceGraph (D3 hook)
      Entities/     EntitiesView, EntityDetail
      Timeline/     TimelineView, useTimeline (D3 hook)
      Stats/        StatsView
      ui/           EvidenceTag, ClassifiedBadge, Spinner, Pagination, EmptyState
    hooks/          useDebounce, useApi
```

## Database Schema

```sql
threads    (doc_id PK, subject, message_count, latest_date, preview, is_sent,
            star_count, has_redactions, attachment_count)

messages   (id PK, doc_id FK, message_index, sender, sender_name, sender_email,
            subject, sent_at, content_markdown, content_html, attachment_count,
            is_from_epstein, preview, account_email)

recipients (message_id FK, address, name, type)        -- type: to/cc/bcc

entities   (id PK, email UNIQUE, name, message_count, is_epstein)

edges      (source_email, target_email, weight)         -- PK: source+target

timeline   (month PK, message_count)                    -- month: YYYY-MM

messages_fts  FTS5 virtual table on (doc_id, message_id, sender_name,
              sender_email, subject, content, sent_at)
              tokenizer: porter unicode61
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/search?q=&page=&limit=` | FTS5 search with snippet highlighting |
| GET | `/api/threads/{doc_id}` | Full thread with messages and recipients |
| GET | `/api/entities?page=&limit=&sort=&order=&search=` | Paginated entity list |
| GET | `/api/entities/{email}` | Entity detail + connections + recent messages |
| GET | `/api/graph?min_weight=&limit=` | Network graph nodes + links |
| GET | `/api/graph/ego/{email}?depth=` | Ego network for one entity |
| GET | `/api/timeline` | Message count per month |
| GET | `/api/stats` | Totals, top senders, top domains |

## How the Scraper Works

See [SCRAPING.md](SCRAPING.md) for the full technical writeup.

**Short version:** jmail.world is a Next.js app. Thread listings come from React Server Components (requires `Accept: text/x-component` + `RSC: 1` headers). Doc IDs are extracted with regex from the RSC stream. Full thread JSON comes from `/api/threads/{doc_id}`. The scraper runs 40 concurrent requests and completes in ~60 seconds.

## Numbers

| Metric | Value |
|--------|-------|
| Threads | 7,545 |
| Messages | 15,188 |
| Entities | 1,134 |
| Communication edges | 2,232 |
| Date range | 2002-12 to 2019-08 |
| Scrape time | ~60s |
| Ingest time | ~3s |
| JSONL size | 106 MB |
| DB size | 137 MB |
| Frontend bundle | ~313 KB JS + ~6 KB CSS |

## Project Files

| File | Purpose |
|------|---------|
| `scraper.py` | Async jmail.world scraper (aiohttp, 40 concurrent) |
| `ingest.py` | JSONL → SQLite ingestion with entity/graph/timeline extraction |
| `server.py` | FastAPI backend, serves API + React frontend |
| `frontend/` | React + TypeScript + Vite frontend |
| `static/index.html` | Original vanilla JS SPA (kept as fallback) |
| `SCRAPING.md` | Technical documentation of scraping methodology |
| `REDESIGN_PLAN.md` | Detailed frontend redesign specification |
