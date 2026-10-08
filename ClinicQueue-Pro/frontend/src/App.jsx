import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useContext } from "react";
import { AuthProvider, AuthContext } from "./AuthContext";
import Home from "./pages/Home";
import About from "./pages/About";
import Packages from "./pages/Packages";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import BookTest from "./pages/BookTest";
import BookingHistory from "./pages/BookingHistory";
import Payments from "./pages/Payments";
import PaymentGateway from "./pages/PaymentGateway";
import DoctorDashboard from "./pages/DoctorDashboard";
import AdminDashboard from "./admin/AdminDashboard";
import ManagePackages from "./admin/ManagePackages";
import ManageBookings from "./admin/ManageBookings";
import ManageSlots from "./admin/ManageSlots";

function ProtectedRoute({ children, roles }) { const { user, loading } = useContext(AuthContext); if (loading) return <div className="loading-screen">Loading...</div>; if (!user) return <Navigate to="/login" replace />; if (roles && !roles.includes(user.role)) return <Navigate to="/dashboard" replace />; return children; }
function AppRoutes() { return <Routes>
  <Route path="/" element={<Home />} /><Route path="/about" element={<About />} /><Route path="/packages" element={<Packages />} /><Route path="/login" element={<Login />} /><Route path="/register" element={<Register />} />
  <Route path="/dashboard" element={<ProtectedRoute roles={["patient"]}><Dashboard /></ProtectedRoute>} />
  <Route path="/book-test/:packageId" element={<ProtectedRoute roles={["patient"]}><BookTest /></ProtectedRoute>} />
  <Route path="/booking-history" element={<ProtectedRoute roles={["patient"]}><BookingHistory /></ProtectedRoute>} />
  <Route path="/payments" element={<ProtectedRoute roles={["patient"]}><Payments /></ProtectedRoute>} />
  <Route path="/payment/:bookingId" element={<ProtectedRoute roles={["patient"]}><PaymentGateway /></ProtectedRoute>} />
  <Route path="/doctor/dashboard" element={<ProtectedRoute roles={["doctor","staff","admin"]}><DoctorDashboard /></ProtectedRoute>} />
  <Route path="/admin/dashboard" element={<ProtectedRoute roles={["admin","staff"]}><AdminDashboard /></ProtectedRoute>} />
  <Route path="/admin/packages" element={<ProtectedRoute roles={["admin","staff"]}><ManagePackages /></ProtectedRoute>} />
  <Route path="/admin/bookings" element={<ProtectedRoute roles={["admin","staff"]}><ManageBookings /></ProtectedRoute>} />
  <Route path="/admin/slots" element={<ProtectedRoute roles={["admin","staff"]}><ManageSlots /></ProtectedRoute>} />
  <Route path="*" element={<Navigate to="/" replace />} />
</Routes>; }
export default function App() { return <AuthProvider><BrowserRouter><AppRoutes /></BrowserRouter></AuthProvider>; }
