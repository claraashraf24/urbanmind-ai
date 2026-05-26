export type CityAlert = {
  id: number;
  external_id?: string | null;
  title: string;
  category: string;
  severity: "low" | "medium" | "high" | "critical";
  latitude: number;
  longitude: number;
  description: string | null;
  source: string;
  risk_score: number;
  created_at: string;
  raw_payload?: Record<string, unknown> | null;
};

export type CityOverview = {
  urban_risk_index: number;
  critical_alerts: number;
  dominant_category: string;
  city_status: string;
};

export type SourceDistributionItem = {
  source: string;
  count: number;
};

export type CategoryDistributionItem = {
  category: string;
  count: number;
};

export type TopRiskAlert = {
  id: number;
  title: string;
  category: string;
  severity: string;
  source: string;
  risk_score: number;
  latitude: number;
  longitude: number;
  created_at: string;
};

export type DistrictRiskItem = {
  district: string;
  count: number;
  critical_alerts: number;
  average_risk_score: number;
};

export type RiskSummary = {
  summary: string;
  total_alerts: number;
  critical_alerts: number;
  high_alerts: number;
  top_source: string | null;
  top_category: string | null;
  average_risk_score: number;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export async function fetchCityAlerts(params?: {
  source?: string;
  category?: string;
  severity?: string;
  limit?: number;
}): Promise<CityAlert[]> {
  const searchParams = new URLSearchParams();

  if (params?.source) searchParams.set("source", params.source);
  if (params?.category) searchParams.set("category", params.category);
  if (params?.severity) searchParams.set("severity", params.severity);
  if (params?.limit) searchParams.set("limit", String(params.limit));

  const query = searchParams.toString();

  const response = await fetch(
    `${API_BASE_URL}/api/alerts/${query ? `?${query}` : ""}`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch city alerts");
  }

  return response.json();
}

export async function fetchCityOverview(): Promise<CityOverview> {
  const response = await fetch(`${API_BASE_URL}/api/analytics/overview`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch city overview");
  }

  return response.json();
}

export type RiskExplanation = {
  alert_id: number;
  title: string;
  risk_score: number;
  source: string;
  category: string;
  severity: string;
  reasons: string[];
};

export async function fetchRiskExplanation(
  alertId: number
): Promise<RiskExplanation> {
  const response = await fetch(
    `${API_BASE_URL}/api/alerts/${alertId}/risk-explanation`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch risk explanation");
  }

  return response.json();
}

export async function fetchSourceDistribution(): Promise<
  SourceDistributionItem[]
> {
  const response = await fetch(
    `${API_BASE_URL}/api/analytics/source-distribution`,
    { cache: "no-store" }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch source distribution");
  }

  return response.json();
}

export async function fetchCategoryDistribution(): Promise<
  CategoryDistributionItem[]
> {
  const response = await fetch(
    `${API_BASE_URL}/api/analytics/category-distribution`,
    { cache: "no-store" }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch category distribution");
  }

  return response.json();
}

export async function fetchTopRiskAlerts(
  limit = 5
): Promise<TopRiskAlert[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/analytics/top-risk-alerts?limit=${limit}`,
    { cache: "no-store" }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch top risk alerts");
  }

  return response.json();
}

export async function fetchDistrictRisk(): Promise<DistrictRiskItem[]> {
  const response = await fetch(`${API_BASE_URL}/api/analytics/district-risk`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch district risk");
  }

  return response.json();
}

export async function fetchRiskSummary(): Promise<RiskSummary> {
  const response = await fetch(`${API_BASE_URL}/api/analytics/risk-summary`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch risk summary");
  }

  return response.json();
}

