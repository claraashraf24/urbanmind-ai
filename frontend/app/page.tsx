import CommandCenter from "@/components/CommandCenter";
import { fetchCityAlerts, fetchCityOverview } from "@/lib/api";

export default async function Home() {
  const alerts = await fetchCityAlerts({ limit: 150 });
  const overview = await fetchCityOverview();

  return <CommandCenter alerts={alerts} overview={overview} />;
}