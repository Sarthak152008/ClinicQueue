import { Link } from "react-router-dom";
import "./components.css";

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-section">
          <h4>ClinicQueue</h4>
          <p>Smart Hospital Appointment & Queue Management Platform</p>
        </div>
        <div className="footer-section">
          <h5>Quick Links</h5>
          <ul>
            <li><Link to="/packages">Packages</Link></li>
            <li><Link to="/login">Login</Link></li>
          </ul>
        </div>
        <div className="footer-section">
          <h5>Contact</h5>
          <p>📧 info@clinicqueue.com</p>
          <p>📞 1800-CLINIC-1</p>
        </div>
      </div>
      <div className="footer-bottom">
        <p>&copy; 2024 ClinicQueue. All rights reserved.</p>
      </div>
    </footer>
  );
}
