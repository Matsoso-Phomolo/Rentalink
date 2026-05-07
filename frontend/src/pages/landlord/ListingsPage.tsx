import { useEffect, useState } from "react";
import { apiFetch } from "../../api/client";
import { ErrorState, LoadingState } from "../../components/DataState";
import { StatusPill } from "../../components/StatusPill";
import type { Listing } from "../../types";

export function ListingsPage() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch("/listings/mine")
      .then(setListings)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load listings"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <section className="page-stack">
      <div className="page-header">
        <div>
          <p className="eyebrow">Marketplace</p>
          <h1>Public room listings</h1>
          <p>Published rooms shown to public room seekers.</p>
        </div>
      </div>
      {loading ? <LoadingState /> : null}
      {error ? <ErrorState message={error} /> : null}
      <div className="list-stack">
        {listings.map((listing) => (
          <article className="row-item rich" key={listing.id}>
            <div>
              <div className="card-topline">
                <StatusPill value={listing.status} />
                <span>{listing.is_public ? "public" : "private"}</span>
              </div>
              <strong>{listing.title}</strong>
              <p>{listing.description}</p>
            </div>
            <div className="row-money">
              <strong>M{Number(listing.rent_price).toLocaleString()}</strong>
              <span>{listing.location_area}</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
