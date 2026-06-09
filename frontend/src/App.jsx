import YieldPredictor from "./YieldPredictor";

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50 flex justify-center px-6 py-8">

      <div className="w-full max-w-4xl space-y-8">

        {/* HEADER */}
        <div className="text-center space-y-4">

          {/* status badge */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white border border-gray-200 text-emerald-600 text-xs font-medium shadow-sm">
            <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
            Live Agricultural Model
          </div>

          {/* title */}
          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-gray-900">
            Crop Forecasting System
          </h1>

          {/* subtitle */}
          <p className="text-gray-500 text-base md:text-lg max-w-2xl mx-auto leading-relaxed">
            Machine learning model that predicts crop yield and estimated profit
            using USDA historical data and climate conditions.
          </p>

        </div>

        {/* MAIN CARD */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 md:p-8">
          <YieldPredictor />
        </div>

        {/* FOOTER */}
        <div className="text-center text-xs text-gray-400 space-y-1">

          <p>
            © {new Date().getFullYear()} Crop Forecasting System
          </p>

          <p>
            Built by Annalee Nersten
          </p>

          <p>
            Data sources: USDA NASS QuickStats • Open-Meteo Climate API
          </p>

        </div>

      </div>
    </div>
  );
}