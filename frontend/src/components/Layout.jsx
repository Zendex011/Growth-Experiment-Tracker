import { Outlet, NavLink, useNavigate } from 'react-router-dom'

export default function Layout() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-ink flex">
      {/* Sidebar */}
      <aside className="w-56 shrink-0 border-r border-subtle flex flex-col sticky top-0 h-screen">
        {/* Logo */}
        <div className="px-6 pt-7 pb-6 border-b border-subtle">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-signal-blue flex items-center justify-center">
              <span className="text-xs font-bold font-display text-white">G</span>
            </div>
            <span className="font-display font-700 text-sm text-slate-white tracking-wide">
              GrowthTrack
            </span>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-body transition-all ${
                isActive
                  ? 'bg-signal-blue-dim text-signal-blue'
                  : 'text-slate-soft hover:text-slate-white hover:bg-ink-muted'
              }`
            }
          >
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            Dashboard
          </NavLink>
        </nav>

        {/* New Experiment CTA */}
        <div className="px-3 pb-6">
          <button
            onClick={() => navigate('/experiments/new')}
            className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg bg-signal-blue hover:bg-blue-500 text-white text-sm font-body font-medium transition-all active:scale-95"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Experiment
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 min-w-0 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
