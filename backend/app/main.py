import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import analytics, city_alerts
from app.websocket.connection_manager import manager
from app.ingestion.save_ingested_alerts import ingest_and_save_events


Base.metadata.create_all(bind=engine)

app = FastAPI(title="UrbanMind AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(city_alerts.router)
app.include_router(analytics.router)


async def real_city_ingestion_stream():
    """
    Background loop:
    - Pulls real city data from Open-Meteo, TTC GTFS-RT, and Toronto Road Restrictions
    - Saves only new alerts
    - Broadcasts new high/critical alerts to the dashboard through WebSocket
    """
    while True:
        try:
            result = ingest_and_save_events()

            print(
                f"[Real Ingestion] Collected={result['collected']} "
                f"Saved={result['saved']} Skipped={result['skipped']}"
            )

            for alert in result["saved_alerts"]:
                if alert["severity"] in ["high", "critical"]:
                    await manager.broadcast(alert)

        except Exception as error:
            print("[Real Ingestion] Failed:", error)

        # Production interval: every 5 minutes
        await asyncio.sleep(300)


@app.on_event("startup")
async def start_real_city_ingestion():
    asyncio.create_task(real_city_ingestion_stream())


@app.get("/")
def health_check():
    return {"status": "UrbanMind AI backend running"}


@app.post("/api/ingestion/run")
async def run_ingestion_now():
    """
    Manual ingestion trigger.
    Useful for testing or refreshing real data from the frontend later.
    """
    result = ingest_and_save_events()

    for alert in result["saved_alerts"]:
        if alert["severity"] in ["high", "critical"]:
            await manager.broadcast(alert)

    return {
        "message": "Ingestion completed",
        "collected": result["collected"],
        "saved": result["saved"],
        "skipped": result["skipped"],
    }


@app.post("/api/dev/broadcast-test")
async def broadcast_test_alert():
    """
    Development-only endpoint to test WebSocket updates.
    Remove or disable before final production/demo polish if needed.
    """
    test_alert = {
        "id": 999999,
        "title": "WebSocket test alert",
        "category": "system",
        "severity": "high",
        "latitude": 43.6532,
        "longitude": -79.3832,
        "description": "This is a temporary test alert to confirm live updates are working.",
        "source": "websocket-test",
        "risk_score": 80,
        "created_at": "2026-05-24T00:00:00",
    }

    await manager.broadcast(test_alert)

    return {"message": "Test alert broadcasted"}


@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(websocket)