import { useEffect, useState, useContext } from "react";
import { AuthContext } from "../AuthContext";
import Navbar from "../components/Navbar";
import "../pages/pages.css";

export default function ManageSlots() {
  const [packages, setPackages] = useState([]);
  const [selectedPackage, setSelectedPackage] = useState("");
  const [formData, setFormData] = useState({ slot_date: "", slot_time: "", capacity: 10 });
  const { apiCall } = useContext(AuthContext);

  useEffect(() => {
    async function loadPackages() {
      try {
        const data = await apiCall("/api/packages");
        setPackages(data);
      } catch (err) {
        console.error("Error:", err);
      }
    }
    loadPackages();
  }, [apiCall]);

  async function handleAddSlot(e) {
    e.preventDefault();
    try {
      await apiCall("/api/admin/time-slots", {
        method: "POST",
        body: JSON.stringify({ package_id: selectedPackage, ...formData })
      });
      setFormData({ slot_date: "", slot_time: "", capacity: 10 });
      alert("Slot added successfully");
    } catch (err) {
      alert("Error: " + err.message);
    }
  }

  return (
    <div>
      <Navbar />
      <section className="admin-section">
        <h1>Manage Time Slots</h1>
        <form onSubmit={handleAddSlot} className="admin-form">
          <select value={selectedPackage} onChange={(e) => setSelectedPackage(e.target.value)} required>
            <option>Select Package</option>
            {packages.map(pkg => <option key={pkg.id} value={pkg.id}>{pkg.name}</option>)}
          </select>
          <input type="date" value={formData.slot_date} onChange={(e) => setFormData({...formData, slot_date: e.target.value})} required />
          <input type="time" value={formData.slot_time} onChange={(e) => setFormData({...formData, slot_time: e.target.value})} required />
          <input type="number" placeholder="Capacity" value={formData.capacity} onChange={(e) => setFormData({...formData, capacity: e.target.value})} required />
          <button type="submit" className="btn btn-primary">Add Slot</button>
        </form>
      </section>
    </div>
  );
}
