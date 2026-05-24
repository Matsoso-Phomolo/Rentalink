import { useEffect, useState } from "react";
import { apiFetch } from "../../api/client";
import { ErrorState, LoadingState } from "../../components/DataState";
import { StatusPill } from "../../components/StatusPill";
import type { LeaseAgreement } from "../../types";

function money(value: number) {
  return `M${Number(value).toLocaleString()}`;
}

export function LeasesPage() {
  const [leases, setLeases] = useState<LeaseAgreement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busyId, setBusyId] = useState("");

  async function loadData() {
    setLoading(true);
    setError("");
    try {
      setLeases(await apiFetch("/leases") as LeaseAgreement[]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load leases");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  async function issueLease(lease: LeaseAgreement) {
    setBusyId(lease.id);
    setNotice("");
    try {
      await apiFetch(`/leases/${lease.id}/issue`, { method: "POST" });
      setNotice("Lease issued to tenant.");
      await loadData();
    } catch (err) {
      setNotice(err instanceof Error ? err.message : "Could not issue lease");
    } finally {
      setBusyId("");
    }
  }

  async function updateLease(lease: LeaseAgreement, status: LeaseAgreement["status"]) {
    setBusyId(lease.id);
    setNotice("");
    try {
      await apiFetch(`/leases/${lease.id}`, {
        method: "PUT",
        body: JSON.stringify({ status })
      });
      setNotice(`Lease marked ${status}.`);
      await loadData();
    } catch (err) {
      setNotice(err instanceof Error ? err.message : "Could not update lease");
    } finally {
      setBusyId("");
    }
  }

  return (
    <section className="page-stack">
      <div className="page-header">
        <div>
          <p className="eyebrow">Legal operations</p>
          <h1>Lease agreements</h1>
          <p>Issue agreements, track electronic tenant acceptance, and keep rental terms tied to occupancies.</p>
        </div>
        <div className="header-stat">
          <strong>{leases.length}</strong>
          <span>leases</span>
        </div>
      </div>
      {loading ? <LoadingState /> : null}
      {error ? <ErrorState message={error} /> : null}
      {notice ? <div className="data-state">{notice}</div> : null}
      <div className="list-stack">
        {leases.length === 0 && !loading ? <div className="data-state">No leases yet. Assigning an applicant creates the first draft automatically.</div> : null}
        {leases.map((lease) => (
          <article className="row-item rich" key={lease.id}>
            <div>
              <div className="card-topline">
                <StatusPill value={lease.status} />
                <span>{lease.lease_number}</span>
              </div>
              <strong>{money(lease.monthly_rent)} monthly</strong>
              <p>Start {new Date(lease.start_date).toLocaleDateString()} - Deposit {money(lease.deposit_amount)}</p>
              <small>Tenant signed: {lease.tenant_signed_at ? new Date(lease.tenant_signed_at).toLocaleString() : "Pending"}</small>
            </div>
            <div className="review-actions">
              <a className="text-button" href={`${import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8001"}/leases/${lease.id}/pdf`} target="_blank" rel="noreferrer">PDF scaffold</a>
              <button type="button" disabled={busyId === lease.id || lease.status !== "draft"} onClick={() => issueLease(lease)}>Issue</button>
              <button type="button" disabled={busyId === lease.id} onClick={() => updateLease(lease, "active")}>Mark active</button>
              <button type="button" disabled={busyId === lease.id} onClick={() => updateLease(lease, "terminated")}>Terminate</button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
