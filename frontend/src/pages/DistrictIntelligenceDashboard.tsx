import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

const API_BASE =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:9000";

export default function DistrictIntelligenceDashboard() {
  const { districtId } = useParams();

  const [summary, setSummary] = useState<any>(null);
  const [distribution, setDistribution] = useState<any>(null);
  const [overdue, setOverdue] = useState<any>(null);
  const [landlords, setLandlords] = useState<any[]>([]);
  const [collection, setCollection] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, [districtId]);

  async function loadDashboard() {
    if (!districtId) {
      setLoading(false);
      return;
    }

    try {
      const [
        summaryRes,
        distributionRes,
        overdueRes,
        landlordsRes,
        collectionRes,
      ] = await Promise.all([
        fetch(`${API_BASE}/district-risk/${districtId}/summary`),
        fetch(`${API_BASE}/district-risk/${districtId}/distribution`),
        fetch(`${API_BASE}/district-risk/${districtId}/overdue-exposure`),
        fetch(`${API_BASE}/district-risk/${districtId}/high-risk-landlords`),
        fetch(`${API_BASE}/district-risk/${districtId}/collection-health`),
      ]);

      setSummary(await summaryRes.json());
      setDistribution(await distributionRes.json());
      setOverdue(await overdueRes.json());
      setLandlords(await landlordsRes.json());
      setCollection(await collectionRes.json());
    } catch (error) {
      console.error("Failed to load district intelligence", error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        Loading District Intelligence...
      </div>
    );
  }

  if (!districtId) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        Missing district ID.
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white p-6">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-cyan-400">
          District Intelligence
        </h1>

        <p className="text-gray-400 mt-2">
          District rental governance, landlord risk, overdue exposure and
          collection performance intelligence.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-10">
        <Card
          title="District Collection Health"
          value={`${collection?.district_collection_health || 0}%`}
          color="text-green-400"
        />

        <Card
          title="Total Landlords"
          value={summary?.total_landlords || 0}
          color="text-cyan-400"
        />

        <Card
          title="Overdue Exposure"
          value={`M${overdue?.overdue_exposure || 0}`}
          color="text-red-400"
        />

        <Card
          title="Overdue Count"
          value={overdue?.overdue_count || 0}
          color="text-yellow-400"
        />
      </div>

      <div className="bg-gray-900 rounded-2xl p-6 mb-10 border border-gray-800">
        <h2 className="text-2xl font-semibold mb-6">
          District Risk Distribution
        </h2>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <RiskCard
            label="Stable"
            value={distribution?.stable || 0}
            color="bg-green-500"
          />

          <RiskCard
            label="Watchlist"
            value={distribution?.watchlist || 0}
            color="bg-yellow-500"
          />

          <RiskCard
            label="Risky"
            value={distribution?.risky || 0}
            color="bg-orange-500"
          />

          <RiskCard
            label="Critical"
            value={distribution?.critical || 0}
            color="bg-red-500"
          />
        </div>
      </div>

      <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
        <h2 className="text-2xl font-semibold mb-6">
          High Risk Landlords
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left border-b border-gray-700">
                <th className="pb-3">Business / Landlord</th>
                <th className="pb-3">Portfolio Risk</th>
                <th className="pb-3">Collection Health</th>
                <th className="pb-3">Stable</th>
                <th className="pb-3">Watchlist</th>
                <th className="pb-3">Risky</th>
                <th className="pb-3">Critical</th>
              </tr>
            </thead>

            <tbody>
              {landlords.length === 0 ? (
                <tr>
                  <td
                    colSpan={7}
                    className="py-6 text-gray-400 text-center"
                  >
                    No high-risk landlords found.
                  </td>
                </tr>
              ) : (
                landlords.map((landlord: any) => (
                  <tr
                    key={landlord.landlord_id}
                    className="border-b border-gray-800"
                  >
                    <td className="py-4">
                      {landlord.business_name || "Unnamed landlord"}
                    </td>

                    <td className="py-4">
                      <span className={riskTextColor(landlord.portfolio_risk_level)}>
                        {landlord.portfolio_risk_level}
                      </span>
                    </td>

                    <td className="py-4 text-green-400">
                      {landlord.collection_health?.portfolio_collection_health ||
                        0}
                      %
                    </td>

                    <td className="py-4 text-green-400">
                      {landlord.risk_distribution?.stable || 0}
                    </td>

                    <td className="py-4 text-yellow-400">
                      {landlord.risk_distribution?.watchlist || 0}
                    </td>

                    <td className="py-4 text-orange-400">
                      {landlord.risk_distribution?.risky || 0}
                    </td>

                    <td className="py-4 text-red-400">
                      {landlord.risk_distribution?.critical || 0}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function Card({
  title,
  value,
  color,
}: {
  title: string;
  value: string | number;
  color: string;
}) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
      <p className="text-gray-400 text-sm mb-2">{title}</p>

      <h2 className={`text-3xl font-bold ${color}`}>{value}</h2>
    </div>
  );
}

function RiskCard({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  return (
    <div className="bg-black rounded-xl p-5 border border-gray-800">
      <div className={`w-4 h-4 rounded-full ${color} mb-4`} />

      <p className="text-gray-400 mb-2">{label}</p>

      <h3 className="text-3xl font-bold">{value}</h3>
    </div>
  );
}

function riskTextColor(risk: string) {
  if (risk === "critical") return "text-red-400";
  if (risk === "risky") return "text-orange-400";
  if (risk === "watchlist") return "text-yellow-400";
  return "text-green-400";
}
