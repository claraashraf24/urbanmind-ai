"use client";

import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { CityAlert } from "@/lib/api";

const alertIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

type Props = {
  alerts: CityAlert[];
};

export default function CityMap({ alerts }: Props) {
  return (
    <div className="h-full w-full overflow-hidden rounded-2xl border border-cyan-500/20 shadow-2xl">
      <MapContainer
        center={[43.6532, -79.3832]}
        zoom={12}
        scrollWheelZoom={true}
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {alerts.map((alert) => (
          <Marker
            key={alert.id}
            position={[alert.latitude, alert.longitude]}
            icon={alertIcon}
          >
            <Popup>
              <strong>{alert.title}</strong>
              <br />
              {alert.category} | {alert.severity}
              <br />
              {alert.description}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}