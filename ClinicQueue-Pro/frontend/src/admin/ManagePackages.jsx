import { useEffect, useState, useContext } from "react";
import { AuthContext } from "../AuthContext";
import Navbar from "../components/Navbar";
import "../pages/pages.css";

export default function ManagePackages() {
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: "", price: "", category: "", description: "" });

  const { apiCall } = useContext(AuthContext);

  useEffect(() => {
    loadPackages();
  }, [apiCall]);

  async function loadPackages() {
    try {
      const data = await apiCall("/api/packages");
      setPackages(data);
    } catch (err) {
      console.error("Error:", err);
    }
    setLoading(false);
  }

  async function handleAddPackage(e) {
    e.preventDefault();
    try {
      await apiCall("/api/admin/packages", {
        method: "POST",
        body: JSON.stringify({...formData, tests_count: 5, includes_tests: "Multiple tests"})
      });
      loadPackages();
      setShowForm(false);
      setFormData({ name: "", price: "", category: "", description: "" });
    } catch (err) {
      console.error("Error:", err);
    }
  }

  return (
    <div>
      <Navbar />
      <section className="admin-section">
        <h1>Manage Packages</h1>
        
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancel" : "Add New Package"}
        </button>

        {showForm && (
          <form onSubmit={handleAddPackage} className="admin-form">
            <input type="text" placeholder="Package Name" value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} required />
            <input type="number" placeholder="Price" value={formData.price} onChange={(e) => setFormData({...formData, price: e.target.value})} required />
            <input type="text" placeholder="Category" value={formData.category} onChange={(e) => setFormData({...formData, category: e.target.value})} required />
            <textarea placeholder="Description" value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})}></textarea>
            <button type="submit" className="btn btn-primary">Add Package</button>
          </form>
        )}

        <div className="packages-table">
          {loading ? <p>Loading...</p> : (
            <table>
              <thead>
                <tr><th>Name</th><th>Category</th><th>Price</th><th>Tests</th></tr>
              </thead>
              <tbody>
                {packages.map(pkg => (
                  <tr key={pkg.id}>
                    <td>{pkg.name}</td>
                    <td>{pkg.category}</td>
                    <td>₹{pkg.price}</td>
                    <td>{pkg.tests_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </div>
  );
}
