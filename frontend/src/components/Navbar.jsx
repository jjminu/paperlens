import { NavLink } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <NavLink to="/" className="brand">
          <span className="brand-name">🔬 PaperLens</span>
          <span className="brand-tag">AI-powered research paper insight tool</span>
        </NavLink>
        <div className="nav-links">
          <NavLink to="/" end>
            요약하기
          </NavLink>
          <NavLink to="/history">기록</NavLink>
        </div>
      </div>
    </nav>
  );
}
