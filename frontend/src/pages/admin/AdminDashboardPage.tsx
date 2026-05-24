import { FormEvent, useEffect, useState } from "react";
import { apiFetch } from "../../api/client";
import { ErrorState, LoadingState } from "../../components/DataState";
import { StatusPill } from "../../components/StatusPill";
import type { Landlord, LandlordRequest } from "../../types";

type ManualLandlordForm = {
  business_name: string;
  full_name: string;
  email: string;
  phone: string;
  address: string;
  password: string;
};

const emptyManual: ManualLandlordForm = {
  business_name: "",
  full_name: "",
  email: "",
  phone: "",
  address: "",
  password: ""
};

function nullable(value: string) {
  return value.trim() ? value.trim() : null;
}

export function AdminDashboardPage() {
  const [landlords, setLandlords] = useState<Landlord[]>([]);
  const [requests, setRequests] = useState<LandlordRequest[]>([]);
  const [manual, setManual] = useState<ManualLandlordForm>(emptyManual);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busyId, setBusyId] = useState("");

  async function loadData() {
    setLoading(true);
    setError("");
    try {
      const [landlordItems, requestItems] = await Promise.all([
        apiFetch("/landlords") as Promise<Landlord[]>,
        apiFetch("/landlords/requests") as Promise<LandlordRequest[]>
      ]);
      setLandlords(landlordItems);
      setRequests(requestItems);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load admin data");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  function updateManual<K extends keyof ManualLandlordForm>(key: K, value: ManualLandlordForm[K]) {
    setManual((current) => ({ ...current, [key]: value }));
  }

  async function submitManual(event: FormEvent) {
    event.preventDefault();
    setNotice("");
    try {
      await apiFetch("/landlords/manual", {
        method: "POST",
        body: JSON.stringify({
          business_name: manual.business_name,
          full_name: manual.full_name,
          email: manual.email,
          phone: nullable(manual.phone),
          address: nullable(manual.address),
          password: manual.password
        })
      });
      setManual(emptyManual);
      setNotice("Landlord account created.");
      await loadData();
    } catch (err) {
      setNotice(err instanceof Error ? err.message : "Could not create landlord");
    }
  }

  async function decideRequest(request: LandlordRequest, action: "approve" | "reject") {
    setBusyId(request.id);
    setNotice("");
    try {
      const result = await apiFetch(`/landlords/requests/${request.id}/${action}`, {
        method: "POST",
        body: JSON.stringify({ admin_note: action === "approve" ? "Approved by admin." : "Rejected by admin." })
      }) as { temporary_password?: string | null };
      setNotice(action === "approve" && result.temporary_password ? `Landlord approved. Temporary password: ${result.temporary_password}` : `Request ${action}d.`);
      await loadData();
    } catch (err) {
      setNotice(err instanceof Error ? err.message : `Could not ${action} request`);
    } finally {
      setBusyId("");
    }
  }

  async function disableLandlord(landlord: Landlord) {
    setBusyId(landlord.id);
    setNotice("");
    try {
      await apiFetch(`/landlords/${landlord.id}/disable`, { method: "POST" });
      setNotice("Landlord disabled.");
      await loadData();
    } catch (err) {
      setNotice(err instanceof Error ? err.message : "Could not disable landlord");
    } finally {
      setBusyId("");
    }
  }

  return (
    <section className="page-stack">
      <div className="page-header">
        <div>
          <p className="eyebrow">Admin</p>
          <h1>Landlord onboarding</h1>
          <p>Only platform admins can approve, create, disable, or identify landlords in LineLink.</p>
        </div>
        <div className="header-stat">
          <strong>{landlords.length}</strong>
          <span>landlords</span>
        </div>
      </div>

      {loading ? <LoadingState /> : null}
      {error ? <ErrorState message={error} /> : null}
      {notice ? <div className="data-state">{notice}</div> : null}

      {!loading && !error ? (
        <>
          <div className="admin-grid">
            <form className="panel form-panel" onSubmit={submitManual}>
              <div>
                <p className="eyebrow">Manual onboarding</p>
                <h2>Add landlord</h2>
              </div>
              <label>Business name<input required value={manual.business_name} onChange={(event) => updateManual("business_name", event.target.value)} /></label>
              <label>Owner full name<input required value={manual.full_name} onChange={(event) => updateManual("full_name", event.target.value)} /></label>
              <div className="form-grid">
                <label>Email<input required type="email" value={manual.email} onChange={(event) => updateManual("email", event.target.value)} /></label>
                <label>Phone<input value={manual.phone} onChange={(event) => updateManual("phone", event.target.value)} /></label>
              </div>
              <label>Address<input value={manual.address} onChange={(event) => updateManual("address", event.target.value)} /></label>
              <label>Temporary password<input required minLength={8} type="password" value={manual.password} onChange={(event) => updateManual("password", event.target.value)} /></label>
              <button className="primary-button" type="submit">Create landlord</button>
            </form>

            <div className="panel">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">Requests</p>
                  <h2>Landlord requests</h2>
                </div>
              </div>
              <div className="list-stack compact-list">
                {requests.length === 0 ? <div className="data-state">No landlord requests yet.</div> : null}
                {requests.map((request) => (
                  <article className="application-card" key={request.id}>
                    <div>
                      <div className="card-topline">
                        <StatusPill value={request.status} />
                        <span>{request.email}</span>
                      </div>
                      <strong>{request.business_name}</strong>
                      <p>{request.full_name} - {request.phone ?? "No phone"}</p>
                      <p>{request.message}</p>
                    </div>
                    <div className="review-actions">
                      <button type="button" disabled={busyId === request.id || request.status !== "pending"} onClick={() => decideRequest(request, "approve")}>Approve</button>
                      <button type="button" disabled={busyId === request.id || request.status !== "pending"} onClick={() => decideRequest(request, "reject")}>Reject</button>
                    </div>
                  </article>
                ))}
              </div>
            </div>
          </div>

          <div className="list-stack">
            {landlords.map((landlord) => (
              <article className="row-item rich" key={landlord.id}>
                <div>
                  <div className="card-topline">
                    <StatusPill value={landlord.is_active ? "active" : "disabled"} />
                    <span>{landlord.system_landlord_number ?? "No system number"}</span>
                  </div>
                  <strong>{landlord.business_name}</strong>
                  <p>{landlord.address}</p>
                </div>
                <div className="review-actions">
                  <span>{landlord.contact_phone}</span>
                  <button type="button" disabled={busyId === landlord.id || !landlord.is_active} onClick={() => disableLandlord(landlord)}>Disable</button>
                </div>
              </article>
            ))}
          </div>
        </>
      ) : null}
    </section>
  );
}
