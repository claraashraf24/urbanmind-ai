"use client";

import dynamic from "next/dynamic";
import type { CityAlert, CityOverview } from "@/lib/api";
import { useEffect, useState } from "react";

const CityMap = dynamic(() => import("@/components/CityMap"), {
  ssr: false,
});

type Props = {
  alerts: CityAlert[];
  overview: CityOverview;
};

export default function CommandCenter({ alerts, overview }: Props) {
  const [liveAlerts, setLiveAlerts] = useState<CityAlert[]>(alerts);
  const [cityOverview, setCityOverview] = useState<CityOverview>(overview);

  const [severityFilter, setSeverityFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");

  useEffect(() => {
    const socket = new WebSocket("ws://127.0.0.1:8000/ws/alerts");

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
            ? "CRITICAL"
            : averageRisk >= 70
            ? "HIGH STRAIN"
            : averageRisk >= 50
            ? "ELEVATED"
            : "STABLE";

        setCityOverview({
          total_alerts: updatedAlerts.length,
          critical_alerts: criticalAlerts,
          average_risk_score: averageRisk,
          dominant_category: dominantCategory,
          city_status: cityStatus,
        });

        return updatedAlerts;
      });
    };

    return () => {
      socket.close();
    };
  }, [overview.dominant_category]);

  const filteredAlerts = liveAlerts.filter((alert) => {
    const matchesSeverity =
      severityFilter === "all" || alert.severity === severityFilter;

    const matchesCategory =
      categoryFilter === "all" || alert.category === categoryFilter;

    return matchesSeverity && matchesCategory;
  });

  const severityOptions = ["all", "medium", "high", "critical"];
  const categoryOptions = [
    "all",
    "traffic",
    "transit",
    "weather",
    "emergency",
    "crowd",
  ];

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <div className="grid h-screen grid-cols-[1fr_380px] gap-4 p-4">
        <section className="relative">
          {/* Left command panel: title + KPIs together so nothing overlaps */}
          <div className="absolute left-[72px] top-6 z-[1000] w-[390px] rounded-2xl border border-cyan-400/30 bg-slate-950 p-5 shadow-2xl shadow-cyan-950/40">
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
                  {Math.round(cityOverview.average_risk_score)}/100
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
                  {cityOverview.city_status}
                </p>
              </div>
            </div>
          </div>

          <CityMap alerts={liveAlerts} />
        </section>

        <aside className="h-full overflow-hidden rounded-2xl border border-cyan-500/20 bg-slate-950 p-5 shadow-2xl">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-cyan-300">
                Live Alerts
              </p>

              <h2 className="mt-1 text-lg font-semibold text-white">
                City Activity Feed
              </h2>
            </div>

            <span className="rounded-full border border-cyan-400/30 bg-cyan-400/10 px-3 py-1 text-[10px] uppercase text-cyan-300">
              Live
            </span>
          </div>

          {/* Clean filter chips instead of ugly dropdowns */}
          <div className="mt-4 rounded-xl border border-slate-800 bg-slate-900 p-3">
            <p className="mb-2 text-[10px] uppercase tracking-widest text-slate-500">
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
            </div>
          </div>

          <div className="mt-4 max-h-[calc(100vh-250px)] space-y-2 overflow-y-auto pr-2">
            {filteredAlerts.slice(0, 5).map((alert) => (
              <div
                key={alert.id}
                className="rounded-xl border border-slate-800 bg-slate-900 p-3"
              >
                <div className="flex items-start justify-between gap-3">
                  <h3 className="text-[12px] font-semibold leading-snug text-white">
                    {alert.title}
                  </h3>

                  <span
                    className={`shrink-0 rounded-full px-2 py-1 text-[9px] font-semibold uppercase ${
                      alert.severity === "critical"
                        ? "bg-red-500/15 text-red-300"
                        : alert.severity === "high"
                        ? "bg-orange-500/15 text-orange-300"
                        : "bg-cyan-500/15 text-cyan-300"
                    }`}
                  >
                    {alert.severity}
                  </span>
                </div>

                <p className="mt-2 text-[11px] leading-relaxed text-slate-400">
                  {alert.description}
                </p>

                <p className="mt-2 text-[11px] font-semibold text-cyan-300">
                  Risk Score: {Math.round(alert.risk_score)}/100
                </p>

                <p className="mt-2 truncate text-[10px] uppercase tracking-wider text-slate-500">
                  {alert.category} · {alert.source}
                </p>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </main>
  );
}