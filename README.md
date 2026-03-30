# Distributed URL Shortener

A production-grade URL shortening service built from scratch with Redis caching, rate limiting, and click analytics. Inspired by how bit.ly works at its core.

---

## Demo

```
POST /shorten  →  { "original_url": "https://google.com" }
               ←  { "short_url": "http://localhost:8000/1" }

GET /1         →  302 Redirect to https://google.com
GET /stats/1   →  { "clicks": 42, "created_at": "..." }
```

---

## Features

- **Base62 encoding** — converts auto-increment DB ids into short codes (56 billion combinations with 6 chars)
- **Redis cache-aside** — redirects served from RAM in microseconds, zero DB queries for hot URLs
- **Click analytics** — atomic Redis counters track every visit per short code
- **Rate limiting** — 10 requests/minute per IP using Redis TTL counters, returns HTTP 429
- **Duplicate detection** — same URL always returns the same short code
- **Docker setup** — PostgreSQL + Redis run in containers, one command to start
- **Auto Swagger docs** — full interactive API docs at `/docs`

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, Python 3.11 |
| Database | PostgreSQL 15 (via SQLAlchemy ORM) |
| Cache + Rate Limiting | Redis 7 |
| Containerization | Docker + Docker Compose |
| Validation | Pydantic v2 |

---

## Architecture

```
Client
  │
  │  POST /shorten
  ▼
FastAPI Backend
  ├── Validate URL (Pydantic)
  ├── Check rate limit (Redis counter per IP)
  ├── Check duplicate (PostgreSQL query)
  ├── Insert row → get auto-increment ID
  ├── encode(id) → Base62 short code
  ├── Cache in Redis (TTL 1 hour)
  └── Return short URL

  │  GET /{short_code}
  ▼
FastAPI Backend
  ├── Check Redis cache → HIT → redirect instantly
  │                    → MISS → query PostgreSQL
  │                           → cache in Redis
  │                           → redirect
  └── increment_clicks (atomic Redis INCR)

  │  GET /stats/{short_code}
  ▼
FastAPI Backend
  ├── Query PostgreSQL → original_url, created_at
  ├── Query Redis      → click count
  └── Return combined stats
```

---

## How Base62 Works

Every URL gets an auto-incrementing ID from PostgreSQL (1, 2, 3...). We convert that ID to Base62:

```
Characters: 0-9 + a-z + A-Z = 62 total

encode(1)   = "1"
encode(62)  = "10"
encode(125) = "21"
encode(238328) = "zzz"  (6 chars = 62^6 = 56 billion combinations)
```

This guarantees uniqueness because every DB id is unique, and the encoding is deterministic.

---

## Getting Started

### Prerequisites
- Python 3.11+
- Docker Desktop

### 1. Clone the repo

```bash
git clone https://github.com/SISODIA2303/url-shortener
cd url-shortener
```

### 2. Create `.env` file in root folder

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/urlshortener
REDIS_URL=redis://localhost:6379
BASE_URL=http://localhost:8000
```

### 3. Start PostgreSQL + Redis

```bash
docker-compose up -d
```

### 4. Install dependencies and run

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 5. Open Swagger UI

```
http://localhost:8000/docs
```

---

## API Reference

### `POST /shorten`
Shortens a URL.

**Request:**
```json
{
  "original_url": "https://www.google.com"
}
```

**Response:**
```json
{
  "short_code": "1",
  "original_url": "https://www.google.com",
  "short_url": "http://localhost:8000/1",
  "clicks": 0,
  "created_at": "2026-03-29T10:00:00"
}
```

**Rate limit:** 10 requests/minute per IP → returns `429` if exceeded

---

### `GET /{short_code}`
Redirects to the original URL.

- Checks Redis first (cache hit → instant redirect)
- Falls back to PostgreSQL on cache miss
- Increments click counter atomically

**Response:** `302 Redirect`

---

### `GET /stats/{short_code}`
Returns analytics for a short URL.

**Response:**
```json
{
  "short_code": "1",
  "original_url": "https://www.google.com",
  "short_url": "http://localhost:8000/1",
  "clicks": 42,
  "created_at": "2026-03-29T10:00:00"
}
```

---

## Project Structure

```
url-shortener/
├── backend/
│   ├── main.py            # FastAPI app + startup
│   ├── database.py        # PostgreSQL connection + session
│   ├── models.py          # URLs table schema (SQLAlchemy)
│   ├── schemas.py         # Request/response validation (Pydantic)
│   ├── shortener.py       # Base62 encode/decode
│   ├── cache.py           # Redis get/set/increment/rate-limit
│   ├── requirements.txt
│   └── routers/
│       ├── urls.py        # POST /shorten + GET /{code}
│       └── analytics.py   # GET /stats/{code}
├── docker-compose.yml     # PostgreSQL + Redis containers
└── .env.example
```

---

## Key Engineering Decisions

**Why Base62 over UUID?**
UUIDs are 36 characters and random. Base62 encodes the DB id so codes are short, URL-safe, and guaranteed unique without any collision checking.

**Why Redis for caching?**
Redis operates in microseconds vs PostgreSQL's milliseconds. A popular short URL getting millions of hits would destroy a DB without caching. Cache-aside means only the first visit hits PostgreSQL.

**Why Redis for rate limiting?**
Redis `INCR` is atomic — even with 1000 concurrent requests, every increment is counted correctly. TTL handles the time window automatically without any scheduled cleanup jobs.

**Why Docker?**
Reproducible environment. Anyone can clone and run with two commands regardless of their OS.

---

## Resume Bullet Points

- Built distributed URL shortener with Base62 encoding, serving redirects via Redis cache-aside pattern with sub-millisecond latency
- Implemented IP-based rate limiting (10 req/min) using atomic Redis TTL counters, returning HTTP 429 on threshold breach
- Designed click analytics system combining PostgreSQL (metadata) and Redis (atomic counters) for real-time stats
- Containerized PostgreSQL and Redis with Docker Compose for reproducible local development

---

## License

MIT
