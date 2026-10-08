import { useEffect, useState, useContext } from "react";
import { AuthContext } from "../AuthContext";
import Navbar from "../components/Navbar";
import "./pages.css";

export default function BookingHistory() {
  const [bookings, setBookings] = useState([]);
  const [filter, setFilter] = useState("all");
  const [error, setError] = useState("");
  const { apiCall } = useContext(AuthContext);

  async function loadBookings() {
    try { setBookings(await apiCall("/api/bookings")); } catch (err) { setError(err.message); }
  }
  useEffect(() => { loadBookings(); }, [apiCall]);

  async function cancelBooking(booking) {
    if (!window.confirm(`Cancel booking #${booking.id} for ${booking.package.name}? This will release the appointment slot.`)) return;
    const reason = window.prompt("Optional cancellation reason:", "") || null;
    try { setError(""); await apiCall(`/api/bookings/${booking.id}/cancel`, { method: "POST", body: JSON.stringify({ reason }) }); await loadBookings(); }
    catch (err) { setError(err.message); }
  }

  const filtered = filter === "all" ? bookings : bookings.filter(b => b.status === filter);
  return <><Navbar /><section className="history-section"><h1>Booking History</h1>{error && <div className="error-box">{error}</div>}<div className="filter-buttons">{["all", "pending", "confirmed", "completed", "cancelled"].map(f => <button key={f} className={`filter-btn ${filter === f ? "active" : ""}`} onClick={() => setFilter(f)}>{f.charAt(0).toUpperCase() + f.slice(1)}</button>)}</div><div className="bookings-list-full">{filtered.length === 0 ? <p>No bookings found</p> : filtered.map(booking => <div key={booking.id} className={`booking-card ${booking.status === "cancelled" ? "booking-cancelled" : ""}`}><div className="booking-header"><h4>{booking.package.name}</h4><span className={`status status-${booking.status}`}>{booking.status}</span></div><div className="booking-details"><p><strong>Booking ID:</strong> #{booking.id}</p><p><strong>Date:</strong> {booking.appointment_date}</p><p><strong>Time:</strong> {booking.appointment_time}</p><p><strong>Price:</strong> ₹{booking.package.price}</p>{booking.token_number && <p><strong>Token:</strong> {booking.token_number}</p>}{booking.cancellations?.length > 0 && <p className="cancellation-note"><strong>Cancelled:</strong> {booking.cancellations[0].reason || "No reason provided"}</p>}</div>{!["cancelled", "completed"].includes(booking.status) && <button className="btn btn-danger" onClick={() => cancelBooking(booking)}>Cancel Booking</button>}</div>)}</div></section></>;
}
