import { FormEvent, useEffect, useState } from "react";
import { apiFetch } from "../../api/client";
import { ErrorState, LoadingState } from "../../components/DataState";
import type { PropertyItem } from "../../types";

type PropertyForm = {
  id?: string;
  name: string;
  description: string;
  location_area: string;
  address: string;
  country: string;
  distance_from_nul: string;
};

const emptyForm: PropertyForm = {
  name: "",
  description: "",
  location_area: "",
  address: "",
  country: "Lesotho",
  distance_from_nul: ""
};

const suggestedLocations = ["Mafikeng", "Hatabutle", "Thoteng", "Mangopeng", "Ten House", "Liphehleng", "Liphakoeng", "Ha Ntja"];

function nullable(value: string) {
  return value.trim() ? value.trim() : null;
}

function formFromProperty(property: PropertyItem): PropertyForm {
  return {
    id: property.id,
    name: property.name,
    description: property.description ?? "",
    location_area: property.location_area,
    address: property.address ?? "",
    country: property.country ?? "Lesotho",
    distance_from_nul: property.distance_from_nul ?? ""
  };
}

export function PropertiesPage() {
  const [properties, setProperties] = useState<PropertyItem[]>([]);
  const [form, setForm] = useState<PropertyForm>(emptyForm);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busyId, setBusyId] = useState("");

  async function loadData() {
    setLoading(true);
    setError("");
    try {
      setProperties(await apiFetch("/properties") as PropertyItem[]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load properties");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  function update<K extends keyof PropertyForm>(key: K, value: PropertyForm[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function chooseLocation(location: string) {
    setForm((current) => ({
      ...current,
      location_area: location,
      address: current.address || `${location}, Lesotho`
    }));
  }

  async function saveProperty(event: FormEvent) {
    event.preventDefault();
    setNotice("");
    const payload = {
      name: form.name,
      description: nullable(form.description),
      location_area: form.location_area,
      address: nullable(form.address),
      country: nullable(form.country),
      distance_from_nul: nullable(form.distance_from_nul)
    };
    try {
      if (form.id) {
        await apiFetch(`/properties/${form.id}`, { method: "PUT", body: JSON.stringify(payload) });
        setNotice("Property updated.");
      } else {
        await apiFetch("/properties", { method: "POST", body: JSON.stringify(payload) });
        setNotice("Property added.");
      }
      setForm(emptyForm);
      await loadData();
    } catch (err) {
      setNotice(err instanceof Error ? err.message : "Could not save property");
    }
  }

  async function removeProperty(property: PropertyItem) {
    setBusyId(property.id);
    setNotice("");
    try {
      await apiFetch(`/properties/${property.id}`, { method: "DELETE" });
      setNotice("Property removed.");
      await loadData();
    } catch (err) {
      setNotice(err instanceof Error ? err.message : "Could not remove property");
    } finally {
      setBusyId("");
    }
  }

  return (
    <section className="page-stack">
      <div className="page-header">
        <div>
          <p className="eyebrow">Line locations</p>
          <h1>Properties and apartments</h1>
          <p>Add each line-house, apartment, block, or branch with its village/location so rooms and listings appear under the correct area.</p>
        </div>
        <div className="header-stat">
          <strong>{properties.length}</strong>
          <span>locations</span>
        </div>
      </div>

      {loading ? <LoadingState /> : null}
      {error ? <ErrorState message={error} /> : null}
      {notice ? <div className="data-state">{notice}</div> : null}

      <div className="admin-grid">
        <form className="panel form-panel" onSubmit={saveProperty}>
          <div>
            <p className="eyebrow">{form.id ? "Edit property" : "New property"}</p>
            <h2>{form.id ? form.name : "Add line-house location"}</h2>
          </div>
          <label>Property or line name<input required value={form.name} onChange={(event) => update("name", event.target.value)} placeholder="Roma Student Residence" /></label>
          <div className="form-grid">
            <label>Location area<input required value={form.location_area} onChange={(event) => update("location_area", event.target.value)} placeholder="Mafikeng" /></label>
            <label>Distance from NUL<input value={form.distance_from_nul} onChange={(event) => update("distance_from_nul", event.target.value)} placeholder="10 minutes walk" /></label>
          </div>
          <label>Address<input value={form.address} onChange={(event) => update("address", event.target.value)} placeholder="Mafikeng, Roma, Lesotho" /></label>
          <label>Description<textarea value={form.description} onChange={(event) => update("description", event.target.value)} placeholder="Student rooms near transport and shops" /></label>
          <label>Country<input value={form.country} onChange={(event) => update("country", event.target.value)} /></label>
          <div className="amenities compact">
            {suggestedLocations.map((location) => (
              <button className="chip-button" type="button" key={location} onClick={() => chooseLocation(location)}>{location}</button>
            ))}
          </div>
          <div className="review-actions">
            <button className="primary-button" type="submit">{form.id ? "Save changes" : "Add property"}</button>
            {form.id ? <button type="button" onClick={() => setForm(emptyForm)}>Cancel edit</button> : null}
          </div>
        </form>

        <div className="panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Your coverage</p>
              <h2>Managed locations</h2>
            </div>
          </div>
          <div className="list-stack compact-list">
            {properties.length === 0 && !loading ? <div className="data-state">No properties yet. Add the first line-house location to start creating rooms.</div> : null}
            {properties.map((property) => (
              <article className="row-item rich" key={property.id}>
                <div>
                  <strong>{property.name}</strong>
                  <p>{property.location_area}{property.address ? ` - ${property.address}` : ""}</p>
                  <small>{property.distance_from_nul ?? "Distance not set"}</small>
                </div>
                <div className="review-actions">
                  <button type="button" onClick={() => setForm(formFromProperty(property))}>Edit</button>
                  <button type="button" disabled={busyId === property.id} onClick={() => removeProperty(property)}>Remove</button>
                </div>
              </article>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
