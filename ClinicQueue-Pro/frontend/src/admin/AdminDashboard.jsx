import { useEffect, useState, useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../AuthContext";
import Navbar from "../components/Navbar";
import "../pages/pages.css";

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const { apiCall } = useContext(AuthContext);

  useEffect(() => {
    async function loadStats() {
      try {
        const data = await apiCall("/api/admin/dashboard");
        setStats(data);
      } catch (err) {
        console.error("Error:", err);
      }
      setLoading(false);
    }
    loadStats();
  }, [apiCall]);

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div>
      <Navbar />
      <section className="dashboard-section">
        <h1>Admin Dashboard 🛡️</h1>
        
        {stats && (
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{stats.total_patients}</div>
              <div className="stat-label">Total Patients</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.total_bookings}</div>
              <div className="stat-label">Total Bookings</div>
            </div>
            <div className="stat-card highlight">
              <div className="stat-value">{stats.pending_bookings}</div>
              <div className="stat-label">Pending Bookings</div>
            </div>
            <div className="stat-card success">
              <div className="stat-value">{stats.completed_bookings}</div>
              <div className="stat-label">Completed</div>
            </div>
            <div className="stat-card info">
              <div className="stat-value">₹{stats.total_revenue}</div>
              <div className="stat-label">Total Revenue</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.total_packages}</div>
              <div className="stat-label">Active Packages</div>
            </div>
          </div>
        )}

        <div className="admin-actions">
          <Link to="/admin/packages" className="btn btn-primary">Manage Packages</Link>
          <Link to="/admin/bookings" className="btn btn-secondary">View Bookings</Link>
          <Link to="/admin/slots" className="btn btn-secondary">Manage Slots</Link>
        </div>
      </section>
    </div>
  );
}
