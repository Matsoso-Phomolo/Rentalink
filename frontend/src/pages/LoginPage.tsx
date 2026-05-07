import { FormEvent, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { VacantRoomsPreview } from "../components/VacantRoomsPreview";

const demoAccounts = [
  { label: "Landlord", email: "landlord1@linelink.com", password: "Password123!" },
  { label: "Tenant", email: "tenant1@linelink.com", password: "Password123!" },
  { label: "Admin", email: "admin@linelink.local", password: "ChangeMe123!" }
];

export function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("landlord1@linelink.com");
  const [password, setPassword] = useState("Password123!");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (user) {
    return <Navigate to={user.role === "tenant" ? "/tenant" : user.role === "admin" ? "/admin" : "/landlord"} replace />;
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const currentUser = await login(email, password);
      navigate(currentUser.role === "tenant" ? "/tenant" : currentUser.role === "admin" ? "/admin" : "/landlord");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sign in");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-panel">
        <div className="login-copy">
          <p className="eyebrow">LineLink</p>
          <h1>Manage line-houses remotely. Find vacant rooms faster.</h1>
          <p>
            A focused workspace for Roma and NUL landlords, caretakers, tenants, and room seekers.
          </p>
          <div className="demo-grid">
            {demoAccounts.map((account) => (
              <button
                type="button"
                key={account.email}
                onClick={() => {
                  setEmail(account.email);
                  setPassword(account.password);
                }}
              >
                <span>{account.label}</span>
                <small>{account.email}</small>
              </button>
            ))}
          </div>
        </div>
        <form className="login-card" onSubmit={handleSubmit}>
          <div>
            <p className="eyebrow">Secure access</p>
            <h2>Sign in</h2>
          </div>
          <label>
            Email
            <input value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" />
          </label>
          <label>
            Password
            <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" autoComplete="current-password" />
          </label>
          {error ? <div className="form-error">{error}</div> : null}
          <button type="submit" className="primary-button" disabled={submitting}>
            {submitting ? "Signing in..." : "Sign in"}
          </button>
          <VacantRoomsPreview />
        </form>
      </section>
    </main>
  );
}
