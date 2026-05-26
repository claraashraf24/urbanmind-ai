import CommandCenter from "@/components/CommandCenter";
import {
  fetchCategoryDistribution,
  fetchCityAlerts,
  fetchCityBriefing,
  fetchCityOverview,
  fetchDistrictRisk,
  fetchRiskHotspots,
  fetchRiskSummary,
  fetchSourceDistribution,
  fetchTopRiskAlerts,
} from "@/lib/api";

export default async function Home() {
  const [
  alerts,
  overview,
  sourceDistribution,
  categoryDistribution,
  topRiskAlerts,
  districtRisk,
  riskSummary,
  riskHotspots,
  cityBriefing,
] = await Promise.all([
  fetchCityAlerts({ limit: 200, status: "active" }),
  fetchCityOverview(),
  fetchSourceDistribution(),
  fetchCategoryDistribution(),
  fetchTopRiskAlerts(5),
  fetchDistrictRisk(),
  fetchRiskSummary(),
  fetchRiskHotspots(1, 5),
  fetchCityBriefing(),
]);

  return (
    <CommandCenter
      alerts={alerts}
      overview={overview}
      sourceDistribution={sourceDistribution}
      categoryDistribution={categoryDistribution}
      topRiskAlerts={topRiskAlerts}
      districtRisk={districtRisk}
      riskSummary={riskSummary}
      riskHotspots={riskHotspots}
      cityBriefing={cityBriefing}
    />
  );
}