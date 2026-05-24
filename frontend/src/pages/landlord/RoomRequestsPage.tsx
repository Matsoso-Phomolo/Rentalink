import { useEffect, useMemo, useState } from "react";
import { apiFetch } from "../../api/client";
import { ErrorState, LoadingState } from "../../components/DataState";
import { StatusPill } from "../../components/StatusPill";
import type { Listing, TenantApplication } from "../../types";

function today() {
  return new Date().toISOString().slice(0, 10);
}

function currentMonthStart() {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth(), 1).toISOString().slice(0, 10);
}

function money(value: number) {
  return `M${Number(value).toLocaleString()}`;
}

export function RoomRequestsPage() {
  const [applications, setApplications] = useState<TenantApplication[]>([]);
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busyId, setBusyId] = useState("");
  const [links, setLinks] = useState<Record<string, string>>({});

  async function loadData() {
    setLoading(true);
    setError("");
    try {
      const [appItems, listingItems] = await Promise.all([
        apiFetch("/applications") as Promise<TenantApplication[]>,
        apiFetch("/listings/mine") as Promise<Listing[]>
      ]);
      setApplications(appItems);
      setListings(listingItems);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load room requests");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  const listingMap = useMemo(() => Object.fromEntries(listings.map((listing) => [listing.id, listing])), [listings]);
  const activeCount = applications.filter((application) => ["inquiry_pending", "form_sent", "submitted", "pending", "under_review", "info_requested"].includes(application.status)).length;

  async function sendForm(application: TenantApplication) {
    setBusyId(application.id);
    setNotice("");
    try {
      const result = await apiFetch(`/applications/${application.id}/send-form-link`, { method: "POST" }) as { application_url: string };
      setLinks((current) => ({ ...current, [application.id]: result.application_url }));
      setNotice("Application form link generated. Copy it and send it to the requester.");
      await loadData();
    } catch (err) {
      setNotice(err instanceof Error ? err.message : "Could not generate form link");
    } finally {
      setBusyId("");
    }
  }

  async function copyLink(applicationId: string) {
    const link = links[applicationId];
    if (!link) return;
    await navigator.clipboard.writeText(link);
    setNotice("Form link copied.");
  }

  async function decide(application: TenantApplication, action: "approve" | "reject" | "request-info") {
    setBusyId(application.id);
    setNotice("");
    const note = action === "reject" ? "Request rejected after review." : action === "request-info" ? "Please provide more information." : "Application approved for assignment.";
    try {
      await apiFetch(`/applications/${application.id}/${action}`, {
        method: action === "request-info" ? "POST" : "PUT",
        body: JSON.stringify({ landlord_note: note })
      });
      setNotice(`Request ${action.replace("-", " ")} completed.`);
      await loadData();
    } catch (err) {
      setNotice(err instanceof Error ? err.message : "Could not update request");
    } finally {
      setBusyId("");
    }
  }

  async function assign(application: TenantApplication) {
    const listing = listingMap[application.listing_id];
    if (!listing) return;
    setBusyId(application.id);
    setNotice("");
    try {
      await apiFetch(`/applications/${application.id}/assign-room`, {
        method: "POST",
        body: JSON.stringify({
          move_in_date: application.preferred_move_in_date ?? today(),
          monthly_rent: Number(listing.rent_price),
          deposit_amount: Number(listing.deposit_amount),
          billing_start_month: currentMonthStart(),
          create_invitation_if_no_user: true
        })
      });
      setNotice("Applicant assigned. The room is now occupied and hidden from public search.");
      await loadData();
    } catch (err) {
      setNotice(err instanceof Error ? err.message : "Could not assign room");
    } finally {
      setBusyId("");
    }
  }

  return (
    <section className="page-stack">
      <div className="page-header">
        <div>
          <p className="eyebrow">Room requests</p>
          <h1>Requester review and application links</h1>
          <p>Screen interested room seekers, send secure form links, then assign submitted applicants only after approval.</p>
        </div>
        <div className="header-stat">
          <strong>{activeCount}</strong>
          <span>active requests</span>
        </div>
      </div>

      {loading ? <LoadingState /> : null}
      {error ? <ErrorState message={error} /> : null}
      {notice ? <div className="data-state">{notice}</div> : null}

      {!loading && !error ? (
        <div className="list-stack">
          {applications.length === 0 ? <div className="data-state">No room requests yet.</div> : null}
          {applications.map((application) => {
            const listing = listingMap[application.listing_id];
            const canAssign = ["submitted", "approved"].includes(application.status) && listing?.status !== "rented";
            return (
              <article className="row-item rich listing-review-card" key={application.id}>
                <div className="listing-review-main">
                  <div className="card-topline">
                    <StatusPill value={application.status} />
                    <span>{listing?.property_name ?? listing?.location_area ?? "Listing"}</span>
                    <span>{listing?.room_number ?? application.room_id?.slice(0, 8)}</span>
                  </div>
                  <strong>{application.full_name}</strong>
                  <p>{application.phone}{application.alternative_phone ? ` / ${application.alternative_phone}` : ""}{application.email ? ` - ${application.email}` : ""}</p>
                  <p>{application.message}</p>
                  <dl className="detail-grid compact">
                    <div><dt>Room</dt><dd>{listing?.title ?? application.listing_id.slice(0, 8)}</dd></div>
                    <div><dt>Rent</dt><dd>{listing ? money(listing.rent_price) : "Pending"}</dd></div>
                    <div><dt>Tenant type</dt><dd>{application.tenant_type.replace("_", " ")}</dd></div>
                    <div><dt>Move-in</dt><dd>{application.preferred_move_in_date ?? "Not provided"}</dd></div>
                  </dl>
                  <div className="detail-grid compact">
                    <div><dt>ID</dt><dd>{application.national_id ?? application.passport_number ?? "Not provided"}</dd></div>
                    <div><dt>Student</dt><dd>{application.student_number ?? application.institution ?? "Not provided"}</dd></div>
                    <div><dt>Occupation</dt><dd>{application.occupation ?? "Not provided"}</dd></div>
                    <div><dt>Emergency</dt><dd>{application.emergency_contact_name ?? application.emergency_contact ?? "Not provided"}</dd></div>
                  </div>
                  {links[application.id] ? (
                    <div className="copy-field">
                      <input readOnly value={links[application.id]} />
                      <button type="button" onClick={() => copyLink(application.id)}>Copy form link</button>
                    </div>
                  ) : null}
                </div>
                <div className="review-actions vertical">
                  <button type="button" disabled={busyId === application.id || application.status === "rejected"} onClick={() => sendForm(application)}>
                    Send application form
                  </button>
                  <button type="button" disabled={busyId === application.id} onClick={() => decide(application, "approve")}>Approve</button>
                  <button type="button" disabled={busyId === application.id} onClick={() => decide(application, "request-info")}>Request info</button>
                  <button type="button" disabled={busyId === application.id} onClick={() => decide(application, "reject")}>Reject</button>
                  <button type="button" disabled={busyId === application.id || !canAssign} onClick={() => assign(application)}>Assign room</button>
                </div>
              </article>
            );
          })}
        </div>
      ) : null}
    </section>
  );
}
