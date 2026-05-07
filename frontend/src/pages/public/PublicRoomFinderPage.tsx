import { useEffect, useMemo, useState } from "react";
import { apiFetch } from "../../api/client";
import { useAuth } from "../../auth/AuthContext";
import { ErrorState, LoadingState } from "../../components/DataState";
import { StatusPill } from "../../components/StatusPill";
import type { Listing } from "../../types";

type LandlordGroup = {
  landlord_id: string;
  name: string;
  contact_phone?: string | null;
  location_area: string;
  min_rent: number;
  listings: Listing[];
};

function roomNumber(listing: Listing) {
  return listing.title.match(/[A-Z]-\d{3}/i)?.[0] ?? `${listing.room_type} room`;
}

function landlordNameFor(listing: Listing, index: number) {
  if (listing.contact_phone === "+26658000000") {
    return "Matsoso Holdings";
  }
  return `Landlord ${index + 1}`;
}

export function PublicRoomFinderPage() {
  const { user, logout } = useAuth();
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedLandlordId, setSelectedLandlordId] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [type, setType] = useState("all");

  useEffect(() => {
    apiFetch("/public/listings")
      .then(setListings)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load listings"))
      .finally(() => setLoading(false));
  }, []);

  const landlordGroups = useMemo(() => {
    const groups = new Map<string, Listing[]>();
    listings.forEach((listing) => {
      if (!groups.has(listing.landlord_id)) {
        groups.set(listing.landlord_id, []);
      }
      groups.get(listing.landlord_id)?.push(listing);
    });

    return Array.from(groups.entries()).map(([landlord_id, landlordListings], index): LandlordGroup => {
      const first = landlordListings[0];
      return {
        landlord_id,
        name: landlordNameFor(first, index),
        contact_phone: first.contact_phone,
        location_area: Array.from(new Set(landlordListings.map((listing) => listing.location_area))).join(", "),
        min_rent: Math.min(...landlordListings.map((listing) => Number(listing.rent_price))),
        listings: landlordListings
      };
    });
  }, [listings]);

  const selectedLandlord = landlordGroups.find((group) => group.landlord_id === selectedLandlordId) ?? null;

  const filteredRooms = useMemo(() => {
    const source = selectedLandlord?.listings ?? [];
    return source.filter((listing) => {
      const text = `${listing.title} ${listing.location_area} ${listing.description ?? ""}`.toLowerCase();
      const matchesQuery = text.includes(query.toLowerCase());
      const matchesType = type === "all" || listing.room_type === type;
      return matchesQuery && matchesType;
    });
  }, [query, selectedLandlord, type]);

  return (
    <section className="page-stack">
      <div className="public-topbar">
        <div className="brand-mark light">
          <span>LL</span>
          <div>
            <strong>LineLink</strong>
            <small>Room finder</small>
          </div>
        </div>
        <div className="public-actions">
          {user ? (
            <>
              <a href={`#/${user.role === "tenant" ? "tenant" : user.role === "admin" ? "admin" : "landlord"}`}>Dashboard</a>
              <button type="button" onClick={logout}>Sign out</button>
            </>
          ) : (
            <a href="#/login">Sign in</a>
          )}
        </div>
      </div>

      <div className="page-header">
        <div>
          <p className="eyebrow">Public room finder</p>
          <h1>{selectedLandlord ? `${selectedLandlord.name} vacancies` : "Landlords with vacant rooms"}</h1>
          <p>
            {selectedLandlord
              ? "Choose an available room from this landlord and use the contact details to arrange next steps."
              : "Start by choosing a landlord with published vacant rooms near Roma and NUL."}
          </p>
        </div>
        <div className="header-stat">
          <strong>{selectedLandlord ? filteredRooms.length : landlordGroups.length}</strong>
          <span>{selectedLandlord ? "vacant rooms" : "landlords"}</span>
        </div>
      </div>

      {loading ? <LoadingState /> : null}
      {error ? <ErrorState message={error} /> : null}

      {!loading && !error && !selectedLandlord ? (
        landlordGroups.length > 0 ? (
          <div className="landlord-grid">
            {landlordGroups.map((group) => (
              <article className="landlord-card" key={group.landlord_id}>
                <div>
                  <div className="card-topline">
                    <StatusPill value="vacant" />
                    <span>{group.location_area}</span>
                  </div>
                  <h2>{group.name}</h2>
                  <p>{group.listings.length} vacant room{group.listings.length === 1 ? "" : "s"} available from M{group.min_rent.toLocaleString()}.</p>
                </div>
                <footer>
                  <strong>{group.contact_phone}</strong>
                  <button type="button" onClick={() => setSelectedLandlordId(group.landlord_id)}>
                    View vacancies
                  </button>
                </footer>
              </article>
            ))}
          </div>
        ) : (
          <div className="data-state">No landlords currently have public vacant rooms.</div>
        )
      ) : null}

      {selectedLandlord ? (
        <>
          <div className="finder-subnav">
            <button type="button" onClick={() => setSelectedLandlordId(null)}>
              Back to landlords
            </button>
            <div className="toolbar">
              <input placeholder="Search rooms, area, or description" value={query} onChange={(event) => setQuery(event.target.value)} />
              <select value={type} onChange={(event) => setType(event.target.value)}>
                <option value="all">All room types</option>
                <option value="single">Single</option>
                <option value="double">Double</option>
              </select>
            </div>
          </div>
          <div className="listing-grid">
            {filteredRooms.map((listing) => (
              <article className="listing-card" key={listing.id}>
                <div>
                  <div className="card-topline">
                    <StatusPill value="vacant" />
                    <span>{listing.distance_from_nul}</span>
                  </div>
                  <h2>{roomNumber(listing)} · {listing.room_size} {listing.room_type}</h2>
                  <p>{listing.description}</p>
                </div>
                <dl className="detail-grid">
                  <div>
                    <dt>Rent</dt>
                    <dd>M{Number(listing.rent_price).toLocaleString()}</dd>
                  </div>
                  <div>
                    <dt>Deposit</dt>
                    <dd>M{Number(listing.deposit_amount).toLocaleString()}</dd>
                  </div>
                  <div>
                    <dt>Location</dt>
                    <dd>{listing.location_area}</dd>
                  </div>
                  <div>
                    <dt>Tenant</dt>
                    <dd>{listing.allowed_tenant_type.replace("_", " ")}</dd>
                  </div>
                </dl>
                <div className="amenities">
                  {listing.water_available ? <span>Water</span> : null}
                  {listing.electricity_available ? <span>Electricity</span> : null}
                  <span>{listing.security_features}</span>
                </div>
                <footer>
                  <span>{listing.house_rules}</span>
                  <strong>{listing.contact_phone}</strong>
                </footer>
              </article>
            ))}
          </div>
        </>
      ) : null}
    </section>
  );
}
