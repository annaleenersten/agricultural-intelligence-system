import YieldPredictor from "./YieldPredictor";

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white flex items-center justify-center p-6">

      <div className="w-full max-w-4xl space-y-8">

        {/* HEADER */}
        <div className="text-center space-y-3">

          <h1 className="text-5xl font-semibold text-gray-900 tracking-tight">
            🌾 Crop Yield Predictor
          </h1>

          <p className="text-gray-500 text-lg">
            AI-powered yield forecasting using USDA + weather data
          </p>

          <div className="inline-flex items-center gap-2 text-sm text-emerald-600">
            <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
            Live ML Model
          </div>

        </div>

        {/* CARD */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8">
          <YieldPredictor />
        </div>

      </div>
    </div>
  );
}
