import { useEffect, useState, useContext } from "react";
import { AuthContext } from "../AuthContext";
import Navbar from "../components/Navbar";
import "./pages.css";

export default function Payments() {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const { apiCall } = useContext(AuthContext);

  useEffect(() => {
    async function loadPayments() {
      try {
        const data = await apiCall("/api/payments");
        setPayments(data);
      } catch (err) {
        console.error("Error:", err);
      }
      setLoading(false);
    }
    loadPayments();
  }, [apiCall]);

  const totalSpent = payments.reduce((sum, p) => sum + p.amount, 0);
  const completedPayments = payments.filter(p => p.payment_status === "completed").length;

  return (
    <div>
      <Navbar />
      <section className="payments-section">
        <h1>Payment History</h1>
        <div className="payment-summary">
          <div className="summary-card">
            <p>Total Payments</p>
            <h3>{payments.length}</h3>
          </div>
          <div className="summary-card">
            <p>Completed</p>
            <h3>{completedPayments}</h3>
          </div>
          <div className="summary-card highlight">
            <p>Total Spent</p>
            <h3>₹{totalSpent}</h3>
          </div>
        </div>
        <div className="payments-list">
          {loading ? <p>Loading...</p> : payments.length === 0 ? <p>No payments</p> : (
            payments.map(p => (
              <div key={p.id} className="payment-row">
                <div className="payment-info">
                  <p><strong>Transaction ID:</strong> {p.transaction_id}</p>
                  <p><strong>Method:</strong> {p.payment_method}</p>
                </div>
                <div className="payment-amount">₹{p.amount}</div>
                <span className={`status status-${p.payment_status}`}>{p.payment_status}</span>
              </div>
            ))
          )}
        </div>
      </section>
    </div>
  );
}
