import { useEffect, useState, useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../AuthContext";
import Navbar from "../components/Navbar";
import "./pages.css";

export default function Packages() {
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(true);
  const { apiCall } = useContext(AuthContext);

  useEffect(() => {
    async function loadPackages() {
      try {
        const data = await apiCall("/api/packages");
        setPackages(data);
      } catch (err) {
        console.error("Error loading packages:", err);
      }
      setLoading(false);
    }
    loadPackages();
  }, [apiCall]);

  if (loading) return <div className="loading">Loading packages...</div>;

  return (
    <div>
      <Navbar />
      <section className="packages-section">
        <h1>Health Packages & Tests</h1>
        <p>Choose from 12+ health packages to book your tests</p>
        <div className="packages-grid">
          {packages.map(pkg => (
            <div key={pkg.id} className="package-card">
              <div className="pkg-header">
                <h3>{pkg.name}</h3>
                <div className="pkg-price">₹{pkg.price}</div>
              </div>
              <p className="pkg-desc">{pkg.description}</p>
              <div className="pkg-info">
                <span>{pkg.tests_count} Tests</span>
                <span>{pkg.report_time}</span>
              </div>
              <Link to={`/book-test/${pkg.id}`} className="btn btn-primary">
                Book Now
              </Link>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
