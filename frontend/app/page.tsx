import CommandCenter from "@/components/CommandCenter";
import {
  fetchCategoryDistribution,
  fetchCityAlerts,
  fetchCityOverview,
  fetchDistrictRisk,
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
  ] = await Promise.all([
    fetchCityAlerts({ limit: 200 }),
    fetchCityOverview(),
    fetchSourceDistribution(),
    fetchCategoryDistribution(),
    fetchTopRiskAlerts(5),
    fetchDistrictRisk(),
    fetchRiskSummary(),
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
    />
  );
}