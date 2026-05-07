import { useEffect, useState } from "react";
import { apiFetch } from "../../api/client";
import { ErrorState, LoadingState } from "../../components/DataState";
import { StatusPill } from "../../components/StatusPill";

type TenantPortal = {
  tenant: null | { id: string; full_name: string; phone: string; email?: string; verification_status: string; student_number?: string; institution?: string };
  occupancies: Array<{ id: string; room_id: string; move_in_date: string; monthly_rent: number; deposit_amount: number; status: string }>;
  rent_dues: Array<{ id: string; due_month: string; amount_due: number; amount_paid: number; status: string }>;
};

export function TenantPortalPage() {
  const [portal, setPortal] = useState<TenantPortal | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch("/tenant-portal/me")
      .then(setPortal)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load tenant portal"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <section className="page-stack">
      <div className="page-header">
        <div>
          <p className="eyebrow">Tenant portal</p>
          <h1>{portal?.tenant?.full_name ?? "My rental"}</h1>
          <p>Rent status, occupancy information, and account verification.</p>
        </div>
      </div>
      {loading ? <LoadingState /> : null}
      {error ? <ErrorState message={error} /> : null}
      {portal?.tenant ? (
        <>
          <div className="metric-grid">
            <article className="metric-card wide">
              <span>Verification</span>
              <strong>{portal.tenant.verification_status.replaceAll("_", " ")}</strong>
            </article>
            <article className="metric-card wide">
              <span>Student number</span>
              <strong>{portal.tenant.student_number ?? "Not set"}</strong>
            </article>
            <article className="metric-card wide">
              <span>Institution</span>
              <strong>{portal.tenant.institution ?? "Not set"}</strong>
            </article>
          </div>
          <section className="panel">
            <h2>Rent dues</h2>
            <div className="list-stack">
              {portal.rent_dues.map((due) => (
                <article className="row-item" key={due.id}>
                  <div>
                    <strong>{new Date(due.due_month).toLocaleDateString(undefined, { month: "long", year: "numeric" })}</strong>
                    <p>M{Number(due.amount_paid).toLocaleString()} paid of M{Number(due.amount_due).toLocaleString()}</p>
                  </div>
                  <StatusPill value={due.status} />
                </article>
              ))}
            </div>
          </section>
          <section className="panel">
            <h2>Occupancy</h2>
            <div className="list-stack">
              {portal.occupancies.map((occupancy) => (
                <article className="row-item" key={occupancy.id}>
                  <div>
                    <strong>Room assignment</strong>
                    <p>Move-in {new Date(occupancy.move_in_date).toLocaleDateString()} · M{Number(occupancy.monthly_rent).toLocaleString()} monthly</p>
                  </div>
                  <StatusPill value={occupancy.status} />
                </article>
              ))}
            </div>
          </section>
        </>
      ) : null}
    </section>
  );
}
