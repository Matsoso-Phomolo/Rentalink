import { useEffect, useMemo, useState } from "react";

import { useIntelligenceSocket } from "../hooks/useIntelligenceSocket";

const API_BASE =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:9000";

type FeedEvent = {
  id: string;
  severity: "critical" | "risky" | "watchlist" | "stable";
  title: string;
  description: string;
  timestamp: string;
};

export default function IntelligenceActivityFeed() {
  const [events, setEvents] = useState<FeedEvent[]>([]);
  const [loading, setLoading] = useState(true);

  const { connected, lastMessage } = useIntelligenceSocket();

  useEffect(() => {
    loadFeed();

    const interval = setInterval(() => {
      loadFeed();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!lastMessage) return;

    const liveEvent: FeedEvent = {
      id: `live-${Date.now()}`,
      severity: lastMessage.severity || "watchlist",
      title:
        lastMessage.title ||
        "Live intelligence update",
      description:
        lastMessage.description ||
        "A live operational intelligence event was received.",
      timestamp:
        lastMessage.created_at ||
        new Date().toISOString(),
    };

    setEvents((current) =>
      [liveEvent, ...current].slice(0, 50)
    );
  }, [lastMessage]);

  async function loadFeed() {
    try {
      const [
        nationalRes,
        districtsRes,
        tenantsRes,
        clustersRes,
      ] = await Promise.all([
        fetch(`${API_BASE}/national-risk/summary`),
        fetch(`${API_BASE}/national-risk/high-risk-districts`),
        fetch(`${API_BASE}/portfolio-risk/high-risk-tenants`),
        fetch(`${API_BASE}/portfolio-risk/overdue-clusters`),
      ]);

      const national = await nationalRes.json();
      const districts = await districtsRes.json();
      const tenants = await tenantsRes.json();
      const clusters = await clustersRes.json();

      const generatedEvents: FeedEvent[] = [];

      if (national?.national_risk_level !== "stable") {
        generatedEvents.push({
          id: "national-risk",
          severity:
            national?.national_risk_level || "watchlist",
          title: "National operational instability detected",
          description: `National risk level is currently ${national?.national_risk_level}.`,
          timestamp: new Date().toISOString(),
        });
      }

      districts.forEach((district: any, index: number) => {
        generatedEvents.push({
          id: `district-${index}`,
          severity: "risky",
          title: `${district.district_name} flagged`,
          description: `District overdue exposure is M${district.overdue_exposure}.`,
          timestamp: new Date().toISOString(),
        });
      });

      tenants.slice(0, 10).forEach((tenant: any, index: number) => {
        generatedEvents.push({
          id: `tenant-${index}`,
          severity:
            tenant.risk_level || "watchlist",
          title: `${tenant.tenant_name || "Tenant"} risk escalation`,
          description: `Outstanding balance is M${tenant.outstanding_balance}.`,
          timestamp: new Date().toISOString(),
        });
      });

      if ((clusters?.["30_plus_days"] || 0) > 0) {
        generatedEvents.push({
          id: "overdue-cluster",
          severity: "critical",
          title: "Severe overdue cluster detected",
          description: `${clusters["30_plus_days"]} dues are overdue by 30+ days.`,
          timestamp: new Date().toISOString(),
        });
      }

      setEvents(generatedEvents);
    } catch (error) {
      console.error(
        "Failed to load intelligence activity feed",
        error
      );
    } finally {
      setLoading(false);
    }
  }

  const sortedEvents = useMemo(() => {
    return [...events].sort(
      (a, b) =>
        new Date(b.timestamp).getTime() -
        new Date(a.timestamp).getTime()
    );
  }, [events]);

  if (loading) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
        <p className="text-gray-400">
          Loading intelligence activity feed...
        </p>
      </div>
    );
  }

  return (
    <section className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <p className="text-xs uppercase tracking-widest text-cyan-400 font-semibold">
            Live Intelligence
          </p>

          <h2 className="text-2xl font-bold mt-1">
            Activity Feed
          </h2>
        </div>

        <span
          className={`rounded-full border px-3 py-1 text-sm ${
            connected
              ? "bg-green-500/10 text-green-400 border-green-700"
              : "bg-yellow-500/10 text-yellow-400 border-yellow-700"
          }`}
        >
          {connected ? "Live WebSocket" : "Reconnecting"}
        </span>
      </div>

      <div className="space-y-4 max-h-[600px] overflow-auto pr-2">
        {sortedEvents.length === 0 ? (
          <div className="bg-black border border-green-700 rounded-xl p-5">
            <p className="text-green-400 font-semibold">
              No active operational intelligence events.
            </p>

            <p className="text-gray-400 mt-2">
              Rentalink currently reports stable operational conditions.
            </p>
          </div>
        ) : (
          sortedEvents.map((event) => (
            <FeedItem
              key={event.id}
              severity={event.severity}
              title={event.title}
              description={event.description}
              timestamp={event.timestamp}
            />
          ))
        )}
      </div>
    </section>
  );
}

function FeedItem({
  severity,
  title,
  description,
  timestamp,
}: {
  severity: string;
  title: string;
  description: string;
  timestamp: string;
}) {
  return (
    <div
      className={`rounded-xl border p-5 bg-black ${severityBorder(
        severity
      )}`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <span
            className={`mt-1 h-3 w-3 rounded-full ${severityDot(
              severity
            )}`}
          />

          <div>
            <h3
              className={`font-semibold ${severityText(
                severity
              )}`}
            >
              {title}
            </h3>

            <p className="text-gray-400 mt-2">
              {description}
            </p>
          </div>
        </div>

        <span className="text-xs text-gray-500 whitespace-nowrap">
          {formatTimestamp(timestamp)}
        </span>
      </div>
    </div>
  );
}

function severityText(severity?: string) {
  if (severity === "critical")
    return "text-red-400";

  if (severity === "risky")
    return "text-orange-400";

  if (severity === "watchlist")
    return "text-yellow-400";

  return "text-green-400";
}

function severityBorder(severity?: string) {
  if (severity === "critical")
    return "border-red-700";

  if (severity === "risky")
    return "border-orange-700";

  if (severity === "watchlist")
    return "border-yellow-700";

  return "border-green-700";
}

function severityDot(severity?: string) {
  if (severity === "critical")
    return "bg-red-500 animate-pulse";

  if (severity === "risky")
    return "bg-orange-500";

  if (severity === "watchlist")
    return "bg-yellow-500";

  return "bg-green-500";
}

function formatTimestamp(value: string) {
  try {
    return new Date(value).toLocaleTimeString();
  } catch {
    return value;
  }
}
