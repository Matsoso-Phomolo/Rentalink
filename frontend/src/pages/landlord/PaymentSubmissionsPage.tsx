import { useEffect, useState } from "react";
import { apiFetch } from "../../api/client";
import { ErrorState, LoadingState } from "../../components/DataState";
import { StatusPill } from "../../components/StatusPill";
import type { PaymentSubmission } from "../../types";

export function PaymentSubmissionsPage() {
  const [payments, setPayments] = useState<PaymentSubmission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch("/payment-submissions")
      .then(setPayments)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load payment submissions"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <section className="page-stack">
      <div className="page-header">
        <div>
          <p className="eyebrow">Payments</p>
          <h1>Payment submissions</h1>
          <p>Review tenant payment proofs and transaction references.</p>
        </div>
      </div>
      {loading ? <LoadingState /> : null}
      {error ? <ErrorState message={error} /> : null}
      <div className="table-panel">
        <table>
          <thead>
            <tr>
              <th>Reference</th>
              <th>Method</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Submitted</th>
            </tr>
          </thead>
          <tbody>
            {payments.map((payment) => (
              <tr key={payment.id}>
                <td>{payment.transaction_reference}</td>
                <td>{payment.method}</td>
                <td>M{Number(payment.amount).toLocaleString()}</td>
                <td><StatusPill value={payment.status} /></td>
                <td>{new Date(payment.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
