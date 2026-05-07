import { Link } from "react-router-dom";

export function VacantRoomsPreview() {
  return (
    <section className="room-finder-cta" aria-labelledby="room-finder-cta-title">
      <div>
        <p className="eyebrow">Room finder</p>
        <h3 id="room-finder-cta-title">Find vacant rooms</h3>
        <p>Browse landlords with available rooms near Roma and NUL.</p>
      </div>
      <Link to="/rooms">Room Finder</Link>
    </section>
  );
}
