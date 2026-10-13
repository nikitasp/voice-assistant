import { NavLink, Outlet } from "react-router-dom";

const links = [
  { to: "/", label: "Playground", end: true },
  { to: "/admin/playground", label: "Test Mode" },
  { to: "/admin/faqs", label: "FAQs" },
  { to: "/admin/unanswered", label: "Unanswered" },
  { to: "/admin/voices", label: "Voices" },
  { to: "/admin/health", label: "Health Check" },
];

export function AppShell() {
  return (
    <div className="shell">
      <aside className="nav">
        <div className="brand">
          <div className="brand-kicker">The Meridian</div>
          <h1>Voice Concierge</h1>
        </div>
        <nav className="nav-links">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) => (isActive ? "active" : undefined)}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  );
}
