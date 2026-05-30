import { NavLink, Outlet } from "react-router-dom";

const intelligenceLinks = [
  {
    label: "Executive Overview",
    to: "/intelligence",
  },
  {
    label: "National Intelligence",
    to: "/intelligence/national",
  },
  {
    label: "District Intelligence",
    to: "/intelligence/district",
  },
  {
    label: "Portfolio Intelligence",
    to: "/intelligence/portfolio",
  },
  {
    label: "Tenant Financial",
    to: "/intelligence/tenant",
  },
  {
    label: "Operational Alerts",
    to: "/intelligence/alerts",
  },
];

export default function IntelligenceLayout() {
  return (
    <div className="min-h-screen bg-black text-white flex">
      <aside className="w-72 bg-gray-950 border-r border-gray-800 p-6 hidden lg:block">
        <div className="mb-10">
          <p className="text-cyan-400 text-sm font-semibold uppercase tracking-widest">
            Rentalink
          </p>

          <h1 className="text-2xl font-bold mt-2">
            Intelligence Center
          </h1>

          <p className="text-gray-500 text-sm mt-2">
            Governance, finance, risk and operational intelligence.
          </p>
        </div>

        <nav className="space-y-2">
          {intelligenceLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/intelligence"}
              className={({ isActive }) =>
                [
                  "block rounded-xl px-4 py-3 text-sm font-medium transition",
                  isActive
                    ? "bg-cyan-500/15 text-cyan-300 border border-cyan-700"
                    : "text-gray-400 hover:bg-gray-900 hover:text-white border border-transparent",
                ].join(" ")
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <main className="flex-1 min-w-0">
        <header className="bg-gray-950 border-b border-gray-800 px-6 py-4 flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-widest text-cyan-400 font-semibold">
              AI-Enhanced Rental Governance
            </p>

            <h2 className="text-xl font-bold">
              Operational Intelligence Console
            </h2>
          </div>

          <div className="hidden md:flex items-center gap-3">
            <span className="rounded-full bg-green-500/10 text-green-400 border border-green-700 px-3 py-1 text-sm">
              Live Intelligence
            </span>

            <span className="rounded-full bg-gray-900 text-gray-400 border border-gray-700 px-3 py-1 text-sm">
              Rentalink API
            </span>
          </div>
        </header>

        <section className="min-h-[calc(100vh-73px)]">
          <Outlet />
        </section>
      </main>
    </div>
  );
}
