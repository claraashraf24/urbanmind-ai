export type CityAlert = {
  id: number;
  title: string;
  category: string;
  severity: string;
  latitude: number;
  longitude: number;
  description?: string;
  source: string;
  created_at: string;
  risk_score: number;
};

export async function fetchCityAlerts(): Promise<CityAlert[]> {
  const res = await fetch("http://127.0.0.1:8000/api/alerts/", {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch city alerts");
  }

  return res.json();
}

export type CityOverview = {
  total_alerts: number;
  critical_alerts: number;
  average_risk_score: number;
  dominant_category: string;
  city_status: string;
};

export async function fetchCityOverview(): Promise<CityOverview> {
  const response = await fetch("http://127.0.0.1:8000/analytics/overview", {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch city overview");
  }

  return response.json();
}