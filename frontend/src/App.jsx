import YieldPredictor from "./YieldPredictor";

export default function App() {
  return (
    <div className="app-shell">
      <header className="site-header">
        <a className="brand" href="/" aria-label="Fieldnote home">
          <span className="brand-mark" aria-hidden="true">
            <svg viewBox="0 0 36 36" fill="none">
              <path d="M18 29V16" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
              <path d="M18 20c-7.3 0-10.2-4.1-10.2-10.2C14 9.8 18 12.8 18 20Z" fill="currentColor" />
              <path d="M18 24c0-6.1 3.4-9.2 10.2-9.2C28.2 21 24.9 24 18 24Z" fill="currentColor" opacity=".62" />
              <path d="M12.5 29h11" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
            </svg>
          </span>
          <span>fieldnote<span className="brand-period">.</span></span>
        </a>
        <span className="header-caption">Crop intelligence for your next season</span>
      </header>

      <main>
        <section className="hero">
          <div className="hero-copy">
            <div className="live-label">
              <span className="live-dot" />
              YIELD & WEATHER OUTLOOK
            </div>
            <h1>Crop forecasts<br /><span>using local data.</span></h1>
            <p>
              Explore county-level crop forecasts grounded in USDA yield history
              and local weather data.
            </p>
          </div>
          <div className="hero-stamp" aria-hidden="true">
            <span>GROW</span>
            <svg viewBox="0 0 80 80" fill="none">
              <path d="M40 65V38" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
              <path d="M40 47C25 47 17 39 17 24c15 0 23 8 23 23Z" fill="currentColor" />
              <path d="M40 55c0-14 8-22 23-22 0 15-8 22-23 22Z" fill="currentColor" opacity=".7" />
              <path d="M27 65h26" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
            </svg>
            <span>WITH INSIGHT</span>
          </div>
        </section>

        <YieldPredictor />
      </main>

      <footer className="site-footer">
        <span>© {new Date().getFullYear()} Fieldnote</span>
        <span>Data from USDA NASS and Open-Meteo</span>
        <span>Forecasts are estimates, not guarantees.</span>
      </footer>
    </div>
  );
}
