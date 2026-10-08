import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "./pages.css";

export default function About() {
  return <><Navbar /><main className="about-page"><section className="about-hero"><p className="eyebrow">CARE THAT FITS YOUR DAY</p><h1>Diagnostics made clear, convenient and human.</h1><p>ClinicQueue brings trusted diagnostic testing, transparent pricing and reliable appointment slots into one calm digital experience.</p></section><section className="about-grid"><article><h2>Built around patients</h2><p>From preventive screening to targeted testing, every step is designed to reduce waiting and make the next action obvious.</p></article><article><h2>Trusted clinical standards</h2><p>Our network model supports certified technicians, careful sample handling and fast digital reports.</p></article><article><h2>One connected workflow</h2><p>Patients, administrators and clinical staff share accurate booking, payment and appointment information.</p></article></section><section className="cta"><h2>Take the next step for your health</h2><p>Explore our packages and choose a time that works for you.</p><a href="/packages" className="btn btn-primary btn-large">Explore Packages</a></section></main><Footer /></>;
}
