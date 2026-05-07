import { useEffect, useState } from "react";
import { apiFetch } from "../../api/client";
import { ErrorState, LoadingState } from "../../components/DataState";

type Landlord = {
  id: string;
  business_name?: string | null;
  contact_phone?: string | null;
  email?: string | null;
  address?: string | null;
};

export function AdminDashboardPage() {
  const [landlords, setLandlords] = useState<Landlord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch("/landlords")
      .then(setLandlords)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load landlords"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <section className="page-stack">
      <div className="page-header">
        <div>
          <p className="eyebrow">Admin</p>
          <h1>Platform overview</h1>
          <p>Early administrative view of onboarded landlords.</p>
        </div>
      </div>
      {loading ? <LoadingState /> : null}
      {error ? <ErrorState message={error} /> : null}
      <div className="list-stack">
        {landlords.map((landlord) => (
          <article className="row-item rich" key={landlord.id}>
            <div>
              <strong>{landlord.business_name}</strong>
              <p>{landlord.address}</p>
            </div>
            <span>{landlord.contact_phone}</span>
          </article>
        ))}
      </div>
    </section>
  );
}
