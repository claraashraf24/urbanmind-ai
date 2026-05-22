from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket, WebSocketDisconnect
from app.websocket.connection_manager import manager
import asyncio
from app.database import SessionLocal
from app.models.city_alert import CityAlert
from app.services.city_event_simulator import generate_city_event
from app.websocket.connection_manager import manager

from app.routers import city_alerts
from app.routers import analytics

app = FastAPI(title="UrbanMind AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(city_alerts.router)
app.include_router(analytics.router)


@app.on_event("startup")
async def start_city_event_stream():
    asyncio.create_task(city_event_stream())

@app.get("/")
def health_check():
    return {"status": "UrbanMind AI backend running"}


@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def city_event_stream():
    while True:
        await asyncio.sleep(8)

        db = SessionLocal()

        try:
            event_data = generate_city_event()
            new_alert = CityAlert(**event_data)

            db.add(new_alert)
            db.commit()
            db.refresh(new_alert)

            await manager.broadcast({
                "id": new_alert.id,
                "title": new_alert.title,
                "category": new_alert.category,
                "severity": new_alert.severity,
                "latitude": new_alert.latitude,
                "longitude": new_alert.longitude,
                "description": new_alert.description,
                "source": new_alert.source,
                "risk_score": new_alert.risk_score,
                "created_at": str(new_alert.created_at),
            })

        finally:
            db.close()