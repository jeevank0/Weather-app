import { NavLink } from 'react-router-dom';

function Navbar() {
  return (
    <header className="nav-wrap">
      <div className="nav-inner">
        <div className="brand-block">
          <h1 className="brand">Smart Weather Assistant</h1>
          <p className="brand-subtitle">Real-time weather with intelligent recommendations</p>
        </div>
        <nav className="nav-links" aria-label="Main navigation">
          <NavLink to="/" className={({ isActive }) => (isActive ? 'active' : '')} end>
            Home
          </NavLink>
          <NavLink to="/history" className={({ isActive }) => (isActive ? 'active' : '')}>
            History
          </NavLink>
        </nav>
      </div>
    </header>
  );
}

export default Navbar;
