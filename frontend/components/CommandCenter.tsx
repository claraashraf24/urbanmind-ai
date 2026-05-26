"use client";

import dynamic from "next/dynamic";
import type {
  CategoryDistributionItem,
  CityAlert,
  CityOverview,
  DistrictRiskItem,
  RiskExplanation,
  RiskSummary,
  SourceDistributionItem,
  TopRiskAlert,
} from "@/lib/api";
import { fetchRiskExplanation } from "@/lib/api";
import { useEffect, useMemo, useState } from "react";

const CityMap = dynamic(() => import("@/components/CityMap"), {
  ssr: false,
});

type Props = {
  alerts: CityAlert[];
  overview: CityOverview;
  sourceDistribution: SourceDistributionItem[];
  categoryDistribution: CategoryDistributionItem[];
  topRiskAlerts: TopRiskAlert[];
  districtRisk: DistrictRiskItem[];
  riskSummary: RiskSummary;
};

function formatSource(source: string) {
  if (source === "open-meteo") return "Weather";
  if (source === "ttc-gtfs-realtime") return "TTC";
  if (source === "toronto-road-restrictions") return "Roads";
  if (source === "websocket-test") return "WebSocket Test";
  return source.replaceAll("-", " ");
}

function formatAlertDate(value: string) {
  const date = new Date(value);

  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");

  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");

  return `${year}-${month}-${day} ${hours}:${minutes}`;
}

function formatStatus(status: string) {
  return status.toUpperCase();
}

function formatAnalyticsLabel(value: string | null) {
  if (!value) return "Unknown";

  if (value === "open-meteo") return "Weather";
  if (value === "ttc-gtfs-realtime") return "TTC";
  if (value === "toronto-road-restrictions") return "Roads";

  return value
    .replaceAll("-", " ")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function getPercentage(value: number, max: number) {
  if (max <= 0) return 0;
  return Math.max(4, Math.round((value / max) * 100));
}

export default function CommandCenter({
  alerts,
  overview,
  sourceDistribution,
  categoryDistribution,
  topRiskAlerts,
  districtRisk,
  riskSummary,
}: Props) {
  const [liveAlerts, setLiveAlerts] = useState<CityAlert[]>(alerts);
  const [cityOverview, setCityOverview] = useState<CityOverview>(overview);

  const [sourceFilter, setSourceFilter] = useState("all");
  const [severityFilter, setSeverityFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");

  const [openExplanationId, setOpenExplanationId] = useState<number | null>(
    null
  );

  const [riskExplanations, setRiskExplanations] = useState<
    Record<number, RiskExplanation>
  >({});

  const [loadingExplanationId, setLoadingExplanationId] = useState<
    number | null
  >(null);

  useEffect(() => {
    const socket = new WebSocket("ws://127.0.0.1:8000/ws/alerts");

    socket.onopen = () => {
      socket.send("connected");
    };

    socket.onmessage = (event) => {
      const newAlert: CityAlert = JSON.parse(event.data);

      setLiveAlerts((prev) => {
        const updatedAlerts = [newAlert, ...prev];

        const criticalAlerts = updatedAlerts.filter(
          (alert) => alert.severity === "critical"
        ).length;

        const averageRisk =
          updatedAlerts.reduce((sum, alert) => sum + alert.risk_score, 0) /
          updatedAlerts.length;

        const categoryCounts = updatedAlerts.reduce<Record<string, number>>(
          (acc, alert) => {
            acc[alert.category] = (acc[alert.category] || 0) + 1;
            return acc;
          },
          {}
        );

        const dominantCategory =
          Object.entries(categoryCounts).sort((a, b) => b[1] - a[1])[0]?.[0] ||
          overview.dominant_category;

        const cityStatus =
          averageRisk >= 85
            ? "high strain"
            : averageRisk >= 70
            ? "elevated"
            : averageRisk >= 50
            ? "moderate"
            : "stable";

        setCityOverview({
          urban_risk_index: Math.round(averageRisk),
          critical_alerts: criticalAlerts,
          dominant_category: dominantCategory,
          city_status: cityStatus,
        });

        return updatedAlerts;
      });
    };

    socket.onerror = () => {
      console.warn(
        "WebSocket connection failed. Dashboard will use saved alerts."
      );
    };

    return () => {
      socket.close();
    };
  }, [overview.dominant_category]);

  const filteredAlerts = useMemo(() => {
    return liveAlerts.filter((alert) => {
      const matchesSource =
        sourceFilter === "all" || alert.source === sourceFilter;

      const matchesSeverity =
        severityFilter === "all" || alert.severity === severityFilter;

      const matchesCategory =
        categoryFilter === "all" || alert.category === categoryFilter;

      return matchesSource && matchesSeverity && matchesCategory;
    });
  }, [liveAlerts, sourceFilter, severityFilter, categoryFilter]);

  const severityOptions = ["all", "medium", "high", "critical"];

  const categoryOptions = [
    "all",
    "traffic",
    "transit",
    "weather",
    "emergency",
    "crowd",
    "system",
  ];

  const sourceOptions = [
    { label: "All Sources", value: "all" },
    { label: "Weather", value: "open-meteo" },
    { label: "TTC", value: "ttc-gtfs-realtime" },
    { label: "Roads", value: "toronto-road-restrictions" },
  ];

  const maxSourceCount = Math.max(
  ...sourceDistribution.map((item) => item.count),
  1
);

const maxCategoryCount = Math.max(
  ...categoryDistribution.map((item) => item.count),
  1
);

const topDistricts = districtRisk.slice(0, 5);

  async function handleToggleExplanation(alertId: number) {
    if (openExplanationId === alertId) {
      setOpenExplanationId(null);
      return;
    }

    setOpenExplanationId(alertId);

    if (riskExplanations[alertId]) {
      return;
    }

    try {
      setLoadingExplanationId(alertId);
      const explanation = await fetchRiskExplanation(alertId);

      setRiskExplanations((prev) => ({
        ...prev,
        [alertId]: explanation,
      }));
    } catch (error) {
      console.error("Failed to load risk explanation:", error);
    } finally {
      setLoadingExplanationId(null);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <div className="grid h-screen grid-cols-[1fr_380px] gap-4 p-4">
        <section className="relative">
          <div className="absolute left-[72px] top-6 z-[1000] w-[390px] rounded-2xl border border-cyan-400/30 bg-slate-950/95 p-5 shadow-2xl shadow-cyan-950/40 backdrop-blur">
            <p className="text-xs uppercase tracking-[0.4em] text-cyan-300">
              UrbanMind AI
            </p>

            <h1 className="mt-2 text-2xl font-bold text-white">
              Toronto Intelligence Command
            </h1>

            <div className="mt-5 grid grid-cols-2 gap-3">
              <div className="rounded-xl border border-cyan-400/30 bg-slate-900 p-4">
                <p className="text-[10px] uppercase tracking-wide text-slate-400">
                  Urban Risk Index
                </p>

                <p className="mt-1 text-2xl font-bold text-cyan-300">
                  {Math.round(cityOverview.urban_risk_index)}/100
                </p>
              </div>

              <div className="rounded-xl border border-red-400/30 bg-slate-900 p-4">
                <p className="text-[10px] uppercase tracking-wide text-slate-400">
                  Critical Alerts
                </p>

                <p className="mt-1 text-2xl font-bold text-red-300">
                  {cityOverview.critical_alerts}
                </p>
              </div>

              <div className="rounded-xl border border-purple-400/30 bg-slate-900 p-4">
                <p className="text-[10px] uppercase tracking-wide text-slate-400">
                  Dominant Category
                </p>

                <p className="mt-1 text-lg font-bold text-purple-300 uppercase">
                  {cityOverview.dominant_category}
                </p>
              </div>

              <div className="rounded-xl border border-emerald-400/30 bg-slate-900 p-4">
                <p className="text-[10px] uppercase tracking-wide text-slate-400">
                  City Status
                </p>

                <p className="mt-1 text-lg font-bold text-emerald-300">
                  {formatStatus(cityOverview.city_status)}
                </p>
              </div>
            </div>
          </div>

          <CityMap alerts={filteredAlerts} />
        </section>

        <aside className="h-full overflow-y-auto rounded-2xl border border-cyan-500/20 bg-slate-950 p-5 shadow-2xl">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-cyan-300">
                Live Alerts
              </p>

              <h2 className="mt-1 text-lg font-semibold text-white">
                City Activity Feed
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Showing {filteredAlerts.length} of {liveAlerts.length} alerts
              </p>
            </div>

            <div className="flex flex-col items-end gap-2">
  <span className="rounded-full border border-cyan-400/30 bg-cyan-400/10 px-3 py-1 text-[10px] uppercase text-cyan-300">
    AI Risk Engine
  </span>

  <button
    onClick={() => setSeverityFilter("critical")}
    className="rounded-full border border-red-400/30 bg-red-400/10 px-3 py-1 text-[10px] font-semibold uppercase text-red-300 transition hover:bg-red-400 hover:text-slate-950"
  >
    Critical Only
  </button>
</div>
          </div>

          <div className="mt-4 rounded-xl border border-slate-800 bg-slate-900 p-3">
            <p className="mb-2 text-[10px] uppercase tracking-widest text-slate-500">
              Source
            </p>

            <div className="grid grid-cols-2 gap-1.5">
              {sourceOptions.map((source) => (
                <button
                  key={source.value}
                  onClick={() => setSourceFilter(source.value)}
                  className={`rounded-lg px-2 py-1.5 text-[9px] font-semibold uppercase transition ${
                    sourceFilter === source.value
                      ? "bg-emerald-400 text-slate-950"
                      : "bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-slate-200"
                  }`}
                >
                  {source.label}
                </button>
              ))}
            </div>

            <p className="mb-2 mt-4 text-[10px] uppercase tracking-widest text-slate-500">
              Severity
            </p>

            <div className="grid grid-cols-4 gap-1.5">
              {severityOptions.map((severity) => (
                <button
                  key={severity}
                  onClick={() => setSeverityFilter(severity)}
                  className={`rounded-lg px-2 py-1.5 text-[9px] font-semibold uppercase transition ${
                    severityFilter === severity
                      ? "bg-cyan-400 text-slate-950"
                      : "bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-slate-200"
                  }`}
                >
                  {severity}
                </button>
              ))}
            </div>

            <p className="mb-2 mt-4 text-[10px] uppercase tracking-widest text-slate-500">
              Category
            </p>

            <div className="grid grid-cols-3 gap-1.5">
              {categoryOptions.map((category) => (
                <button
                  key={category}
                  onClick={() => setCategoryFilter(category)}
                  className={`rounded-lg px-2 py-1.5 text-[9px] font-semibold uppercase transition ${
                    categoryFilter === category
                      ? "bg-purple-400 text-slate-950"
                      : "bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-slate-200"
                  }`}
                >
                  {category}
                </button>
                
              ))}
              <button
  onClick={() => {
    setSourceFilter("all");
    setSeverityFilter("all");
    setCategoryFilter("all");
  }}
  className="mt-4 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-[10px] font-semibold uppercase tracking-wide text-slate-300 transition hover:border-cyan-400 hover:text-cyan-300"
>
  Reset Filters
</button>
            </div>
          </div>
          <div className="mt-4 rounded-xl border border-cyan-500/20 bg-slate-900 p-3">
  <div className="flex items-center justify-between gap-3">
    <div>
      <p className="text-[10px] uppercase tracking-widest text-cyan-300">
        City Intelligence
      </p>
      <h3 className="mt-1 text-sm font-semibold text-white">
        Risk Summary
      </h3>
    </div>

    <span className="rounded-full bg-cyan-400/10 px-2 py-1 text-[9px] font-semibold uppercase text-cyan-300">
      Live Analytics
    </span>
  </div>

  <p className="mt-3 text-[11px] leading-relaxed text-slate-400">
    {riskSummary.summary}
  </p>

  <div className="mt-3 grid grid-cols-3 gap-2">
    <div className="rounded-lg bg-slate-950 p-2">
      <p className="text-[9px] uppercase text-slate-500">Total</p>
      <p className="mt-1 text-sm font-bold text-white">
        {riskSummary.total_alerts}
      </p>
    </div>

    <div className="rounded-lg bg-slate-950 p-2">
      <p className="text-[9px] uppercase text-slate-500">High</p>
      <p className="mt-1 text-sm font-bold text-orange-300">
        {riskSummary.high_alerts}
      </p>
    </div>

    <div className="rounded-lg bg-slate-950 p-2">
      <p className="text-[9px] uppercase text-slate-500">Avg Risk</p>
      <p className="mt-1 text-sm font-bold text-cyan-300">
        {Math.round(riskSummary.average_risk_score)}
      </p>
    </div>
  </div>
</div>
<div className="mt-4 rounded-xl border border-slate-800 bg-slate-900 p-3">
  <p className="text-[10px] uppercase tracking-widest text-slate-500">
    Risk by Source
  </p>

  <div className="mt-3 space-y-2">
    {sourceDistribution.map((item) => (
      <div key={item.source}>
        <div className="mb-1 flex items-center justify-between text-[10px]">
          <span className="font-semibold uppercase text-slate-300">
            {formatAnalyticsLabel(item.source)}
          </span>
          <span className="text-slate-500">{item.count}</span>
        </div>

        <div className="h-2 overflow-hidden rounded-full bg-slate-800">
          <div
            className="h-full rounded-full bg-cyan-400"
            style={{
              width: `${getPercentage(item.count, maxSourceCount)}%`,
            }}
          />
        </div>
      </div>
    ))}
  </div>
</div>
<div className="mt-4 rounded-xl border border-slate-800 bg-slate-900 p-3">
  <p className="text-[10px] uppercase tracking-widest text-slate-500">
    Risk by Category
  </p>

  <div className="mt-3 space-y-2">
    {categoryDistribution.map((item) => (
      <div key={item.category}>
        <div className="mb-1 flex items-center justify-between text-[10px]">
          <span className="font-semibold uppercase text-slate-300">
            {formatAnalyticsLabel(item.category)}
          </span>
          <span className="text-slate-500">{item.count}</span>
        </div>

        <div className="h-2 overflow-hidden rounded-full bg-slate-800">
          <div
            className="h-full rounded-full bg-purple-400"
            style={{
              width: `${getPercentage(item.count, maxCategoryCount)}%`,
            }}
          />
        </div>
      </div>
    ))}
  </div>
</div>
<div className="mt-4 rounded-xl border border-red-500/20 bg-slate-900 p-3">
  <p className="text-[10px] uppercase tracking-widest text-red-300">
    Top Risk Alerts
  </p>

  <div className="mt-3 space-y-2">
    {topRiskAlerts.map((alert, index) => (
      <div
        key={alert.id}
        className="rounded-lg border border-slate-800 bg-slate-950 p-2"
      >
        <div className="flex items-center justify-between gap-2">
          <span className="rounded-full bg-red-400/10 px-2 py-0.5 text-[9px] font-bold text-red-300">
            #{index + 1}
          </span>

          <span className="text-[10px] font-bold text-red-300">
            {Math.round(alert.risk_score)}/100
          </span>
        </div>

        <p className="mt-2 line-clamp-2 text-[11px] font-semibold leading-snug text-slate-200">
          {alert.title}
        </p>

        <p className="mt-1 text-[9px] uppercase tracking-wide text-slate-500">
          {formatAnalyticsLabel(alert.source)} · {alert.category}
        </p>
      </div>
    ))}
  </div>
</div>
<div className="mt-4 rounded-xl border border-emerald-500/20 bg-slate-900 p-3">
  <p className="text-[10px] uppercase tracking-widest text-emerald-300">
    District Risk Ranking
  </p>

  <div className="mt-3 space-y-2">
    {topDistricts.map((district) => (
      <div
        key={district.district}
        className="rounded-lg border border-slate-800 bg-slate-950 p-2"
      >
        <div className="flex items-center justify-between gap-2">
          <p className="truncate text-[11px] font-semibold uppercase text-slate-200">
            {district.district}
          </p>

          <span className="text-[10px] font-bold text-emerald-300">
            {Math.round(district.average_risk_score)}
          </span>
        </div>

        <p className="mt-1 text-[9px] text-slate-500">
          {district.count} alerts · {district.critical_alerts} critical
        </p>
      </div>
    ))}
  </div>
</div>

          <div className="mt-4 space-y-2 pr-2">
            {filteredAlerts.slice(0, 30).map((alert) => (
              <div
                key={alert.id}
                className="rounded-xl border border-slate-800 bg-slate-900 p-3"
              >
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <span className="rounded-full border border-white/10 bg-white/10 px-2 py-1 text-[9px] font-semibold uppercase tracking-wide text-slate-200">
                    {formatSource(alert.source)}
                  </span>

                  <span
                    className={`rounded-full px-2 py-1 text-[9px] font-semibold uppercase ${
                      alert.severity === "critical"
                        ? "bg-red-500/15 text-red-300"
                        : alert.severity === "high"
                        ? "bg-orange-500/15 text-orange-300"
                        : alert.severity === "medium"
                        ? "bg-cyan-500/15 text-cyan-300"
                        : "bg-slate-500/15 text-slate-300"
                    }`}
                  >
                    {alert.severity}
                  </span>

                  <span className="rounded-full bg-slate-800 px-2 py-1 text-[9px] font-semibold uppercase text-slate-400">
                    Risk {Math.round(alert.risk_score)}/100
                  </span>
                </div>

                <h3 className="text-[12px] font-semibold leading-snug text-white">
                  {alert.title}
                </h3>

                <p className="mt-2 text-[11px] leading-relaxed text-slate-400">
                  {alert.description}
                </p>

                <p className="mt-2 truncate text-[10px] uppercase tracking-wider text-slate-500">
                  {alert.category} · {formatAlertDate(alert.created_at)}
                </p>

                <button
                  onClick={() => handleToggleExplanation(alert.id)}
                  className="mt-3 rounded-lg border border-cyan-400/20 bg-cyan-400/10 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wide text-cyan-300 transition hover:bg-cyan-400 hover:text-slate-950"
                >
                  {openExplanationId === alert.id
                    ? "Hide explanation"
                    : "Why this risk?"}
                </button>

                {openExplanationId === alert.id && (
                  <div className="mt-3 rounded-lg border border-slate-700 bg-slate-950/80 p-3">
                    {loadingExplanationId === alert.id ? (
                      <p className="text-[11px] text-slate-400">
                        Loading risk explanation...
                      </p>
                    ) : riskExplanations[alert.id] ? (
                      <div>
                        <p className="text-[10px] font-semibold uppercase tracking-widest text-cyan-300">
                          Risk Explanation
                        </p>

                        <ul className="mt-2 space-y-1.5">
                          {riskExplanations[alert.id].reasons.map(
                            (reason, index) => (
                              <li
                                key={`${alert.id}-${index}`}
                                className="flex gap-2 text-[11px] leading-relaxed text-slate-300"
                              >
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-cyan-300" />
                                <span>{reason}</span>
                              </li>
                            )
                          )}
                        </ul>
                      </div>
                    ) : (
                      <p className="text-[11px] text-red-300">
                        Could not load explanation.
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))}

            {filteredAlerts.length === 0 && (
              <div className="rounded-xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-400">
                No alerts match the selected filters.
              </div>
            )}
          </div>
        </aside>
      </div>
    </main>
  );
}