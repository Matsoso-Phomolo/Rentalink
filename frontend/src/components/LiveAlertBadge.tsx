import { useEffect, useMemo, useState } from "react";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001";

type Severity =
  | "critical"
  | "risky"
  | "watchlist"
  | "stable";

type AlertState = {
  severity: Severity;
  count: number;
  label: string;
};

export default function LiveAlertBadge() {
  const [alertState, setAlertState] = useState<AlertState>({
    severity: "stable",
    count: 0,
    label: "No Active Alerts",
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAlerts();

    const interval = setInterval(() => {
      loadAlerts();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  async function loadAlerts() {
    try {
      const [nationalRes, portfolioRes] = await Promise.all([
        fetch(`${API_BASE}/national-risk/summary`),
        fetch(`${API_BASE}/portfolio-risk/high-risk-tenants`),
      ]);

      const national = await nationalRes.json();
      const tenants = await portfolioRes.json();

      const criticalTenants = tenants.filter(
        (tenant: any) => tenant.risk_level === "critical"
      );

      const riskyTenants = tenants.filter(
        (tenant: any) =>
          tenant.risk_level === "risky" ||
          tenant.risk_level === "watchlist"
      );

      if (criticalTenants.length > 0) {
        setAlertState({
          severity: "critical",
          count: criticalTenants.length,
          label: `${criticalTenants.length} Critical Alerts`,
        });
      } else if (riskyTenants.length > 0) {
        setAlertState({
          severity: "risky",
          count: riskyTenants.length,
          label: `${riskyTenants.length} Risk Alerts`,
        });
      } else if (
        national?.national_risk_level === "watchlist"
      ) {
        setAlertState({
          severity: "watchlist",
          count: 1,
          label: "Watchlist Activity",
        });
      } else {
        setAlertState({
          severity: "stable",
          count: 0,
          label: "System Stable",
        });
      }
    } catch (error) {
      console.error("Failed to load live intelligence alerts", error);

      setAlertState({
        severity: "watchlist",
        count: 0,
        label: "Intelligence Offline",
      });
    } finally {
      setLoading(false);
    }
  }

  const styles = useMemo(() => {
    switch (alertState.severity) {
      case "critical":
        return {
          wrapper:
            "bg-red-500/10 border-red-700 text-red-400",
          dot: "bg-red-500 animate-pulse",
        };

      case "risky":
        return {
          wrapper:
            "bg-orange-500/10 border-orange-700 text-orange-400",
          dot: "bg-orange-500",
        };

      case "watchlist":
        return {
          wrapper:
            "bg-yellow-500/10 border-yellow-700 text-yellow-400",
          dot: "bg-yellow-500",
        };

      default:
        return {
          wrapper:
            "bg-green-500/10 border-green-700 text-green-400",
          dot: "bg-green-500",
        };
    }
  }, [alertState.severity]);

  if (loading) {
    return (
      <div className="rounded-full border border-gray-700 bg-gray-900 px-4 py-2 text-sm text-gray-400">
        Loading Intelligence...
      </div>
    );
  }

  return (
    <div
      className={`flex items-center gap-3 rounded-full border px-4 py-2 text-sm font-medium transition ${styles.wrapper}`}
    >
      <span
        className={`h-3 w-3 rounded-full ${styles.dot}`}
      />

      <span>{alertState.label}</span>
    </div>
  );
}
