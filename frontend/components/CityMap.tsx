"use client";

import "leaflet/dist/leaflet.css";

import L from "leaflet";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import type { CityAlert } from "@/lib/api";

type Props = {
  alerts: CityAlert[];
};

function getSeverityColor(severity: string) {
  if (severity === "critical") return "#ef4444";
  if (severity === "high") return "#f97316";
  if (severity === "medium") return "#22d3ee";
  return "#94a3b8";
}

function getMarkerSize(riskScore: number) {
  if (riskScore >= 90) return 34;
  if (riskScore >= 75) return 28;
  if (riskScore >= 60) return 22;
  return 18;
}

function formatSource(source: string) {
  if (source === "open-meteo") return "Weather";
  if (source === "ttc-gtfs-realtime") return "TTC";
  if (source === "toronto-road-restrictions") return "Roads";
  if (source === "websocket-test") return "WebSocket Test";
  return source.replaceAll("-", " ");
}

function createRiskIcon(alert: CityAlert) {
  const color = getSeverityColor(alert.severity);
  const size = getMarkerSize(alert.risk_score);

  return L.divIcon({
    className: "",
    html: `
      <div
        style="
          width: ${size}px;
          height: ${size}px;
          border-radius: 9999px;
          background: ${color};
          border: 2px solid white;
          box-shadow: 0 0 18px ${color};
          opacity: 0.92;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 10px;
          font-weight: 800;
        "
      >
        ${Math.round(alert.risk_score)}
      </div>
    `,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2],
  });
}

export default function CityMap({ alerts }: Props) {
  const torontoCenter: [number, number] = [43.6532, -79.3832];

  return (
    <div className="relative h-full w-full overflow-hidden rounded-2xl border border-cyan-500/20">
      <MapContainer
        center={torontoCenter}
        zoom={11}
        scrollWheelZoom
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {alerts.map((alert) => (
          <Marker
            key={`${alert.id}-${alert.source}`}
            position={[alert.latitude, alert.longitude]}
            icon={createRiskIcon(alert)}
          >
            <Popup>
              <div style={{ maxWidth: "260px" }}>
                <strong>{alert.title}</strong>

                <p style={{ margin: "8px 0 4px" }}>
                  {alert.description}
                </p>

                <p style={{ margin: "4px 0" }}>
                  <strong>Source:</strong> {formatSource(alert.source)}
                </p>

                <p style={{ margin: "4px 0" }}>
                  <strong>Severity:</strong> {alert.severity}
                </p>

                <p style={{ margin: "4px 0" }}>
                  <strong>Risk:</strong> {Math.round(alert.risk_score)}/100
                </p>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      <div className="absolute bottom-4 left-4 z-[1000] rounded-xl border border-slate-700 bg-slate-950/90 p-3 text-xs text-slate-200 shadow-xl backdrop-blur">
        <p className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-slate-400">
          Risk Legend
        </p>

        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-red-500" />
            <span>Critical</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-orange-500" />
            <span>High</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-cyan-300" />
            <span>Medium</span>
          </div>
        </div>

        <p className="mt-2 text-[10px] text-slate-500">
          Marker size follows risk score
        </p>
      </div>
    </div>
  );
}