import { useEffect, useMemo, useState } from "react";
import { apiFetch } from "../../api/client";
import { ErrorState, LoadingState } from "../../components/DataState";
import { StatusPill } from "../../components/StatusPill";
import type { Room } from "../../types";

export function RoomsPage() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("all");

  useEffect(() => {
    apiFetch("/rooms")
      .then(setRooms)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load rooms"))
      .finally(() => setLoading(false));
  }, []);

  const visibleRooms = useMemo(() => rooms.filter((room) => status === "all" || room.status === status), [rooms, status]);

  return (
    <section className="page-stack">
      <div className="page-header">
        <div>
          <p className="eyebrow">Rooms</p>
          <h1>Room inventory</h1>
          <p>Track availability, rent, deposits, and room types across the property.</p>
        </div>
        <select value={status} onChange={(event) => setStatus(event.target.value)}>
          <option value="all">All statuses</option>
          <option value="vacant">Vacant</option>
          <option value="occupied">Occupied</option>
          <option value="maintenance">Maintenance</option>
        </select>
      </div>
      {loading ? <LoadingState /> : null}
      {error ? <ErrorState message={error} /> : null}
      <div className="table-panel">
        <table>
          <thead>
            <tr>
              <th>Room</th>
              <th>Status</th>
              <th>Type</th>
              <th>Size</th>
              <th>Rent</th>
              <th>Deposit</th>
            </tr>
          </thead>
          <tbody>
            {visibleRooms.map((room) => (
              <tr key={room.id}>
                <td>{room.room_number}</td>
                <td><StatusPill value={room.status} /></td>
                <td>{room.room_type}</td>
                <td>{room.room_size}</td>
                <td>M{Number(room.rent_price).toLocaleString()}</td>
                <td>M{Number(room.deposit_amount).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
