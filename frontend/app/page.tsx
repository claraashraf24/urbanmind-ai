import { fetchCityAlerts, fetchCityOverview } from "@/lib/api";
import CommandCenter from "@/components/CommandCenter";

export default async function Home() {
  const alerts = await fetchCityAlerts();
  const overview = await fetchCityOverview();

  return <CommandCenter alerts={alerts} overview={overview} />;
}