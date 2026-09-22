<div align="center">

# πŸ"° AI News Aggregator

**A self-hosted pipeline that scrapes AI news, summarises it with LLMs, ranks it to your taste, and delivers a curated digest to your inbox — every single day.**

<br/>

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![uv](https://img.shields.io/badge/uv-package%20manager-DE5FE9?style=flat-square&logo=astral&logoColor=white)](https://docs.astral.sh/uv/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-database-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM%20API-FF6B35?style=flat-square)](https://openrouter.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)

</div>

---

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [AI Agents](#ai-agents)
- [Scheduling](#scheduling)
- [Extending the Project](#extending-the-project)
- [Dependencies](#dependencies)

---

## Overview

AI News Aggregator is a fully automated daily pipeline that:

1. **Scrapes** fresh content from Anthropic, OpenAI, and YouTube
2. **Extracts** full article text and video transcripts
3. **Summarises** each piece into a compact digest using an LLM
4. **Ranks** every digest against your personal interest profile
5. **Emails** a beautifully formatted HTML digest with the top articles

All intermediate data is persisted in PostgreSQL, so re-runs never duplicate work.

---

## How It Works

```
                        ┌──────────────────────────┐
                        │     Sources (RSS/API)     │
                        │  Anthropic · OpenAI · YT  │
                        └────────────┬─────────────┘
                                     │  scrape
                                     ▼
                        ┌──────────────────────────┐
                        │    Content Processors    │
                        │  Docling · Transcripts   │
                        └────────────┬─────────────┘
                                     │  extract text
                                     ▼
                        ┌──────────────────────────┐
                        │      DigestAgent         │
                        │  Summarise → title +     │
                        │  2-3 sentence summary    │
                        └────────────┬─────────────┘
                                     │  LLM ranking
                                     ▼
                        ┌──────────────────────────┐
                        │      CuratorAgent        │
                        │  Score 0–10 per article  │
                        │  based on your profile   │
                        └────────────┬─────────────┘
                                     │  compose
                                     ▼
                        ┌──────────────────────────┐
                        │   EmailAgent + Gmail     │
                        │  Personalised HTML email │
                        │  delivered to your inbox │
                        └──────────────────────────┘
```

All agents run via the [OpenRouter](https://openrouter.ai/) API (free tier supported).

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.12+ |
| [uv](https://docs.astral.sh/uv/) | latest |
| PostgreSQL | any recent |
| OpenRouter API key | [sign up free](https://openrouter.ai/) |
| Gmail App Password | [how to create](https://support.google.com/accounts/answer/185833) |

---

## Quick Start

### 1 — Clone & install

```bash
git clone https://github.com/your-username/ai-news-aggregator.git
cd ai-news-aggregator
uv sync
```

### 2 — Set up environment variables

```bash
cp app/example.env .env
```

Open `.env` and fill in your values:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/ai_news
OPENROUTER_API_KEY=your_openrouter_api_key

MY_EMAIL=you@gmail.com
APP_PASSWORD=your_gmail_app_password

# Optional — YouTube proxy to avoid rate limits
PROXY_USERNAME=
PROXY_PASSWORD=
```

### 3 — Initialise the database

```bash
uv run python -c "from app.database.create_tables import create_tables; create_tables()"
```

### 4 — Personalise your profile

Edit `app/profiles/user_profile.py`:

```python
USER_PROFILE = {
    "name": "Your Name",
    "background": "Brief description of your background",
    "interests": [
        "Large Language Models (LLMs)",
        "AI agent architectures",
        "RAG systems",
        # add or remove topics freely
    ],
    "preferences": {
        "prefer_practical": True,
        "prefer_technical_depth": True,
        "avoid_marketing_hype": True,
    },
    "expertise_level": "Advanced",
}
```

### 5 — Add YouTube channels

Edit `app/config.py`:

```python
YOUTUBE_CHANNELS = [
    "UCawZsQWqfGSbCI5yjkdVkTA",  # Matthew Berman
    # "UCn8ujwUInbJkBhffxqAPBVQ",  # Dave Ebbelaar
]
```

### 6 — Run

```bash
# Default: last 24 hours, top 10 articles
uv run python main.py

# Custom: last 48 hours, top 5 articles
uv run python main.py 48 5
```

---

## Configuration

| Variable | File | Description |
|---|---|---|
| `DATABASE_URL` | `.env` | PostgreSQL connection string |
| `OPENROUTER_API_KEY` | `.env` | OpenRouter API key |
| `MY_EMAIL` | `.env` | Gmail address to send from and receive at |
| `APP_PASSWORD` | `.env` | Gmail App Password |
| `PROXY_USERNAME` | `.env` | Webshare proxy username *(optional)* |
| `PROXY_PASSWORD` | `.env` | Webshare proxy password *(optional)* |
| `OPENROUTER_MODEL` | `app/config.py` | LLM model for all agents |
| `YOUTUBE_CHANNELS` | `app/config.py` | List of YouTube channel IDs to monitor |

The default model is `nvidia/nemotron-3.5-lightning:free` — any [OpenRouter-supported model](https://openrouter.ai/models) can be used as a drop-in replacement.

---

## Project Structure

```
ai-news-aggregator/
β"œβ"€β"€ main.py                        # CLI entry point
β"œβ"€β"€ pyproject.toml
β"œβ"€β"€ app/
β"‚   β"œβ"€β"€ config.py                  # Model config & YouTube channel IDs
β"‚   β"œβ"€β"€ daily_runner.py            # Orchestrates the full 5-step pipeline
β"‚   β"œβ"€β"€ runner.py                  # Runs all scrapers and persists to DB
β"‚   β"œβ"€β"€ example.env
β"‚   β"‚
β"‚   β"œβ"€β"€ agent/
β"‚   β"‚   β"œβ"€β"€ curator_agent.py       # Ranks digests by relevance to user profile
β"‚   β"‚   β"œβ"€β"€ digest_agent.py        # Summarises articles into title + summary
β"‚   β"‚   └── email_agent.py         # Generates personalised email introduction
β"‚   β"‚
β"‚   β"œβ"€β"€ scrapers/
β"‚   β"‚   β"œβ"€β"€ anthropic.py           # Anthropic RSS + Docling page extractor
β"‚   β"‚   β"œβ"€β"€ openai.py              # OpenAI RSS scraper
β"‚   β"‚   └── youtube.py             # YouTube RSS + transcript fetcher
β"‚   β"‚
β"‚   β"œβ"€β"€ services/
β"‚   β"‚   β"œβ"€β"€ email.py               # Gmail SMTP + HTML email rendering
β"‚   β"‚   β"œβ"€β"€ process_anthropic.py   # Converts Anthropic pages to Markdown
β"‚   β"‚   β"œβ"€β"€ process_curator.py     # Runs CuratorAgent over all digests
β"‚   β"‚   β"œβ"€β"€ process_digest.py      # Runs DigestAgent over raw content
β"‚   β"‚   β"œβ"€β"€ process_email.py       # Builds and sends the email digest
β"‚   β"‚   └── process_youtube.py     # Fetches and stores transcripts
β"‚   β"‚
β"‚   β"œβ"€β"€ database/
β"‚   β"‚   β"œβ"€β"€ models.py              # SQLAlchemy ORM models
β"‚   β"‚   β"œβ"€β"€ connection.py          # DB engine & session factory
β"‚   β"‚   β"œβ"€β"€ repository.py          # CRUD operations
β"‚   β"‚   └── create_tables.py       # Schema initialisation
β"‚   β"‚
β"‚   └── profiles/
β"‚       └── user_profile.py        # Your personalisation config
```

---

## Database Schema

| Table | Primary Key | Description |
|---|---|---|
| `youtube_videos` | `video_id` | Scraped videos with full transcripts |
| `openai_articles` | `guid` | OpenAI blog posts from RSS |
| `anthropic_articles` | `guid` | Anthropic articles with extracted Markdown |
| `digests` | `id` (`type:article_id`) | LLM-generated title + summary for each item |

---

## AI Agents

### `DigestAgent`

Consumes raw article text or video transcripts and produces a concise **title** (5–10 words) plus a **2–3 sentence summary** focused on substance and practical value — no marketing language.

### `CuratorAgent`

Scores each digest from **0.0–10.0** and assigns a unique rank based on the user profile's interests, expertise level, and stated preferences. Returns structured JSON with per-article reasoning, making the ranking fully auditable.

```
9.0 – 10.0  Highly relevant, directly aligns with user interests
7.0 –  8.9  Very relevant, strong alignment
5.0 –  6.9  Moderately relevant
3.0 –  4.9  Somewhat relevant
0.0 –  2.9  Low relevance
```

### `EmailAgent`

Writes a warm, personalised greeting and a 2–3 sentence preview of the top-ranked articles, then hands off to the email service which renders the full digest as styled HTML.

---

## Scheduling

Add a cron job to run the pipeline automatically every morning:

```bash
# Every day at 7:00 AM
0 7 * * * cd /path/to/ai-news-aggregator && uv run python main.py >> logs/pipeline.log 2>&1
```

Or use any scheduler you prefer — **systemd timers**, **GitHub Actions**, **AWS EventBridge**, **GCP Cloud Scheduler**, etc.

---

## Extending the Project

**Add a new source** — create a scraper in `app/scrapers/`, add a corresponding service in `app/services/`, then wire it into `app/runner.py` and `app/daily_runner.py`.

**Swap the LLM** — change `OPENROUTER_MODEL` in `app/config.py` to any model from [openrouter.ai/models](https://openrouter.ai/models).

**Send to multiple recipients** — update `send_digest_email()` in `app/services/process_email.py` to pass a list of addresses to `send_email()`.

---

## Dependencies

| Package | Purpose |
|---|---|
| `openai` | OpenRouter-compatible LLM API client |
| `feedparser` | RSS feed parsing |
| `docling` | Web page → clean Markdown conversion |
| `youtube-transcript-api` | YouTube transcript extraction |
| `sqlalchemy` | ORM and database abstraction |
| `psycopg2-binary` | PostgreSQL driver |
| `markdown` | Markdown → HTML for email rendering |
| `beautifulsoup4` | HTML parsing |
| `python-dotenv` | `.env` file loading |

---

## License

MIT © 2026 — see [LICENSE](LICENSE) for details.