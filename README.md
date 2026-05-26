# UrbanMind AI — Smart City Intelligence Platform

UrbanMind AI is a real-time smart city intelligence platform for Toronto. It ingests live public city data, scores operational risk, detects dense risk hotspots, explains alert severity, manages alert lifecycle, and generates AI-style incident briefings for city operations teams.

The goal of this project is to go beyond a normal dashboard. UrbanMind AI turns raw city feeds into explainable operational intelligence.

---

## Demo Screenshots

### Command Center Overview



![UrbanMind AI Command Center](docs/screenshots/dashboard-overview.png)

### AI Incident Briefing and Hotspot Map



![AI Incident Briefing and Hotspot Map](docs/screenshots/ai-incident-briefing.png)

---

## Why This Project Is Different

Most dashboards only display data. UrbanMind AI adds intelligence on top of live city data.

It includes:

- Real-time ingestion from public city and weather sources
- Explainable risk scoring for each alert
- Risk hotspot detection
- AI-style incident briefing with key drivers and recommended actions
- Alert lifecycle management: active, resolved, expired
- Interactive map with risk-aware markers and hotspot zones
- WebSocket support for live updates
- Full-stack command center UI

---

## Current Features

### Real Data Ingestion

UrbanMind AI currently ingests real data from:

- Open-Meteo Weather API
- TTC GTFS-Realtime Alerts
- City of Toronto Road Restrictions Feed

Each source is normalized into a shared alert format.

---

### Risk Scoring Engine

Each alert receives a risk score from `0` to `100`.

The score is calculated using factors such as:

- Alert severity
- Data source
- Road class
- Current impact
- Maximum impact
- Planned vs. unplanned disruption
- TTC disruption type
- Weather intensity
- Keywords such as collision, closure, detour, and no subway service

---

### Explainable Risk

Each alert has a “Why this risk?” explanation.

Example:

```text
Base severity is critical.
Road class is Major Arterial Road.
Current impact is High.
Maximum impact is High.
```

The backend stores the raw source payload so the platform can explain why each risk score was assigned.

---

### Risk Hotspot Detection

UrbanMind AI detects dense clusters of high-risk alerts and generates hotspot zones.

Each hotspot includes:

- Center latitude and longitude
- Alert count
- Critical alert count
- Average risk score
- Dominant category
- Dominant source
- Top alert in the zone

The map displays hotspot zones as transparent circles.

---

### AI Incident Briefing

The platform generates an operations-style city briefing.

The briefing includes:

- City status headline
- Risk summary
- Key risk drivers
- Recommended operational actions
- Current risk level

Example:

```text
Toronto is operating under high urban strain.

UrbanMind AI is monitoring active alerts. The dominant category is traffic, mainly driven by road restrictions.

Recommended actions:
- Prioritize monitoring affected road corridors.
- Review high-risk road restrictions for multi-day disruptions.
- Monitor TTC disruptions and detours.
- Use hotspot zones to focus operational attention.
```

---

### Alert Lifecycle Management

Alerts can have different statuses:

- `active`
- `resolved`
- `expired`

Resolved and expired alerts remain stored for history, but active analytics only use active alerts.

Operators can mark alerts as resolved directly from the dashboard.

---

## Tech Stack

### Backend

- FastAPI
- Python
- SQLAlchemy
- PostgreSQL / PostGIS Docker image
- Redis Docker service
- WebSockets
- GTFS-Realtime bindings
- Rule-based risk engine
- Rule-based briefing engine

### Frontend

- Next.js
- TypeScript
- Tailwind CSS
- React Leaflet
- OpenStreetMap tiles
- Dynamic client-side map rendering

### Data Sources

- Open-Meteo API
- TTC GTFS-Realtime
- City of Toronto Open Data — Road Restrictions

---

## System Architecture

```text
Open-Meteo API
TTC GTFS-Realtime
Toronto Road Restrictions
        |
        v
Backend Ingestion Workers
        |
        v
Normalization + Risk Scoring + Deduplication
        |
        v
PostgreSQL
        |
        v
FastAPI REST APIs + WebSocket Broadcast
        |
        v
Next.js Smart City Command Dashboard
```

---

## Backend API Endpoints

### Alerts

```text
GET    /api/alerts/
GET    /api/alerts/{id}/risk-explanation
PATCH  /api/alerts/{id}/resolve
```

### Analytics

```text
GET    /api/analytics/overview
GET    /api/analytics/source-distribution
GET    /api/analytics/category-distribution
GET    /api/analytics/top-risk-alerts
GET    /api/analytics/district-risk
GET    /api/analytics/risk-hotspots
GET    /api/analytics/risk-summary
GET    /api/analytics/briefing
```

### Ingestion

```text
POST   /api/ingestion/run
```

### WebSocket

```text
WS     /ws/alerts
```

---

## Project Structure

```text
urbanmind-ai/
│
├── backend/
│   ├── app/
│   │   ├── ingestion/
│   │   │   ├── weather_ingestor.py
│   │   │   ├── ttc_ingestor.py
│   │   │   ├── road_ingestor.py
│   │   │   ├── run_ingestion.py
│   │   │   ├── save_ingested_alerts.py
│   │   │   ├── delete_all_alerts.py
│   │   │   ├── cleanup_old_alerts.py
│   │   │   └── expire_stale_alerts.py
│   │   │
│   │   ├── models/
│   │   │   └── city_alert.py
│   │   │
│   │   ├── routers/
│   │   │   ├── city_alerts.py
│   │   │   └── analytics.py
│   │   │
│   │   ├── schemas/
│   │   │   └── city_alert.py
│   │   │
│   │   ├── services/
│   │   │   ├── risk_engine.py
│   │   │   └── briefing_engine.py
│   │   │
│   │   ├── websocket/
│   │   │   └── connection_manager.py
│   │   │
│   │   ├── database.py
│   │   ├── config.py
│   │   └── main.py
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   └── page.tsx
│   │
│   ├── components/
│   │   ├── CommandCenter.tsx
│   │   └── CityMap.tsx
│   │
│   └── lib/
│       └── api.ts
│
├── docs/
│   ├── architecture.md
│   ├── data-sources.md
│   ├── demo-script.md
│   └── screenshots/
│
├── docker-compose.yml
└── README.md
```

---

## How to Run Locally

### 1. Start Docker Services

From the project root:

```bash
docker compose up -d
```

This starts:

- PostgreSQL / PostGIS
- Redis

---

### 2. Run the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

Backend runs on:

```text
http://127.0.0.1:8000
```

---

### 3. Run the Frontend

```bash
cd frontend
npm run dev
```

Frontend runs on:

```text
http://localhost:3000
```

---

## Environment Variables

Create a backend environment file:

```bash
backend/.env
```

Example:

```env
DATABASE_URL=postgresql://urbanmind:urbanmind@localhost:5432/urbanmind_db
```

Create a frontend environment file:

```bash
frontend/.env.local
```

Example:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

---

## Useful Development Commands

### Run all ingestors without saving

```bash
cd backend
python -m app.ingestion.run_ingestion
```

### Save real ingested alerts to database

```bash
python -m app.ingestion.save_ingested_alerts
```

### Run manual ingestion through API

```bash
curl -X POST http://127.0.0.1:8000/api/ingestion/run | python -m json.tool
```

### Check active alerts

```bash
curl "http://127.0.0.1:8000/api/alerts/?limit=3" | python -m json.tool
```

### Check all alerts

```bash
curl "http://127.0.0.1:8000/api/alerts/?status=all&limit=3" | python -m json.tool
```

### Check risk explanation

```bash
curl "http://127.0.0.1:8000/api/alerts/ALERT_ID/risk-explanation" | python -m json.tool
```

### Resolve an alert

```bash
curl -X PATCH http://127.0.0.1:8000/api/alerts/ALERT_ID/resolve | python -m json.tool
```

### Check risk hotspots

```bash
curl "http://127.0.0.1:8000/api/analytics/risk-hotspots?radius_km=1&limit=5" | python -m json.tool
```

### Check AI incident briefing

```bash
curl "http://127.0.0.1:8000/api/analytics/briefing" | python -m json.tool
```

---

## Implemented Milestones

- Initialized FastAPI backend
- Built Next.js command center dashboard
- Integrated PostgreSQL with SQLAlchemy
- Added real-time WebSocket support
- Added Open-Meteo weather ingestion
- Added TTC GTFS-Realtime ingestion
- Added Toronto Road Restrictions ingestion
- Added risk scoring engine
- Added raw payload storage
- Added explainable risk endpoint
- Added city analytics endpoints
- Added risk hotspot detection
- Added hotspot zones on the map
- Added hotspot focus interaction
- Added alert lifecycle management
- Added AI incident briefing generator
- Added professional dashboard filters

---

## Planned Improvements

- Add APScheduler for production-style scheduled ingestion
- Add map marker clustering for better performance
- Add historical risk trend analysis
- Add incident report export
- Add authentication for operators
- Add deployment setup with Dockerized frontend and backend
- Add optional OpenAI-powered briefing generation
- Add automated tests for ingestion and risk scoring
- Add CI/CD pipeline

---

## Portfolio Summary

UrbanMind AI demonstrates full-stack AI and data engineering skills through a realistic smart city command center.

It combines:

- Real-time public data ingestion
- Backend risk intelligence
- Explainable risk scoring
- Geospatial visualization
- Hotspot detection
- Alert lifecycle management
- AI-style operational briefings
- A polished frontend dashboard

This project is designed to show practical AI engineering beyond simple model demos by focusing on production-style data flow, decision support, and operational intelligence.
