import { useState } from "react";
import { STATES } from "./data/states";
import { CROPS } from "./data/crops";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function YieldPredictor() {
  const [form, setForm] = useState({
    state: "",
    county: "",
    crop: "",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [counties, setCounties] = useState([]);
  const [error, setError] = useState(null);

  function handleChange(e) {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  }

  async function handleStateChange(e) {
    const state = e.target.value;

    setForm({
      ...form,
      state,
      county: "",
    });

    setError(null);
    setCounties([]);

    if (!state) return;

    try {
      const res = await fetch(`http://127.0.0.1:8000/counties/${state}`);

      if (!res.ok) throw new Error("Failed to load counties");

      const data = await res.json();

      if (!data?.counties || !Array.isArray(data.counties)) {
        setCounties([]);
        return;
      }

      setCounties(data.counties);
    } catch (err) {
      console.error(err);
      setError("Could not load counties");
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    if (!form.state || !form.county || !form.crop) {
      setError("Please fill all fields");
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/predict-yield", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          state: form.state.toUpperCase(),
          county: form.county.toUpperCase(),
          crop: form.crop.toUpperCase(),
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Prediction failed");
      }

      const data = await res.json();

      // protect against bad backend responses
      if (!data || typeof data.predicted_yield !== "number") {
        throw new Error("Invalid prediction response");
      }

      setResult(data);
    } catch (err) {
      console.error(err);
      setError(err.message || "Error fetching prediction");
    }

    setLoading(false);
  }

  return (
    <div className="space-y-6">

      {/* ERROR DISPLAY */}
      {error && (
        <div className="p-3 rounded bg-red-50 text-red-600 border border-red-200">
          {error}
        </div>
      )}

      {/* FORM */}
      <form onSubmit={handleSubmit} className="space-y-4">

        {/* STATE */}
        <select
          name="state"
          value={form.state}
          onChange={handleStateChange}
          className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50
          focus:bg-white focus:outline-none focus:border-emerald-500
          focus:ring-4 focus:ring-emerald-100 transition shadow-sm"
        >
          <option value="">Select State</option>
          {STATES.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>

        {/* COUNTY */}
        <select
          name="county"
          value={form.county}
          onChange={handleChange}
          disabled={!form.state || counties.length === 0}
          className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50
          focus:bg-white focus:outline-none focus:border-emerald-500
          focus:ring-4 focus:ring-emerald-100 transition shadow-sm"
        >
          <option value="">Select County</option>

          {counties.length === 0 ? (
            <option disabled>No counties available</option>
          ) : (
            counties.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))
          )}
        </select>

        {/* CROP */}
        <select
          name="crop"
          value={form.crop}
          onChange={handleChange}
          className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50
          focus:bg-white focus:outline-none focus:border-emerald-500
          focus:ring-4 focus:ring-emerald-100 transition shadow-sm"
        >
          <option value="">Select Crop</option>
          {CROPS.map((crop) => (
            <option key={crop} value={crop}>
              {crop}
            </option>
          ))}
        </select>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 rounded-xl bg-emerald-500 text-white"
        >
          {loading ? "Analyzing..." : "Predict Yield"}
        </button>
      </form>

    {/* RESULTS */}
    {result && (
      <div className="space-y-4 mt-6">

        {/* PREDICTION */}
        <div className="p-5 rounded-2xl bg-emerald-50 text-center shadow-sm hover:shadow-md transition">
          <p className="text-sm text-emerald-600">Predicted Yield</p>
          <p className="text-3xl font-bold mt-1">
            {result.predicted_yield?.toFixed?.(2) ?? "N/A"}
          </p>
        </div>

        {/* HISTORICAL AVG */}
        <div className="p-5 rounded-2xl bg-gray-50 text-center shadow-sm hover:shadow-md transition">
          <p className="text-sm text-gray-600">Historical Average</p>
          <p className="text-2xl font-semibold mt-1">
            {result.historical_yield?.avg?.toFixed?.(2) ?? "No data"}
          </p>
        </div>

        {/* WEATHER COMPARISON */}
        {result.weather && (
          
          <div className="grid grid-cols-2 gap-4">

            {/* FORECAST */}
            <div className="p-5 rounded-2xl bg-white border shadow-md hover:shadow-lg transition">
              <p className="text-sm text-gray-500 mb-4">Forecast Weather</p>

              <div className="space-y-3">

                <div>
                  <p className="text-xs text-gray-400">Average Temperature</p>
                  <p className="text-xl font-semibold text-gray-900">
                    {result.weather.forecast.avg_temp?.toFixed(1)}°C
                  </p>
                </div>

                <div>
                  <p className="text-xs text-gray-400">Total Rainfall</p>
                  <p className="text-xl font-semibold text-gray-900">
                    {result.weather.forecast.total_rain?.toFixed(1)} mm
                  </p>
                </div>

                <div>
                  <p className="text-xs text-gray-400">Average Wind Speed</p>
                  <p className="text-xl font-semibold text-gray-900">
                    {result.weather.forecast.avg_wind?.toFixed(1)} m/s
                  </p>
                </div>

              </div>
            </div>

            {/* HISTORICAL */}
            <div className="p-5 rounded-2xl bg-white border shadow-md hover:shadow-lg transition">
                <p className="text-sm text-gray-500 mb-4">Historical Average</p>

                <div className="space-y-3">

                  <div>
                    <p className="text-xs text-gray-400">Average Temperature</p>
                    <p className="text-xl font-semibold text-gray-900">
                      {result.weather.historical_avg.avg_temp?.toFixed(1)}°C
                    </p>
                  </div>

                  <div>
                    <p className="text-xs text-gray-400">Total Rainfall</p>
                    <p className="text-xl font-semibold text-gray-900">
                      {result.weather.historical_avg.total_rain?.toFixed(1)} mm
                    </p>
                  </div>

                  <div>
                    <p className="text-xs text-gray-400">Average Wind Speed</p>
                    <p className="text-xl font-semibold text-gray-900">
                      {result.weather.historical_avg.avg_wind?.toFixed(1)} m/s
                    </p>
                  </div>

                </div>
              </div>

          </div>
          
        )}

        {/* CHART */}
        {Array.isArray(result.historical_yield?.data) &&
          result.historical_yield.data.length > 0 && (

          <div className="p-5 rounded-2xl bg-white border shadow-md hover:shadow-lg transition">
            <h3 className="font-semibold mb-3">
              USDA Yield History (2020–2025)
            </h3>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={result.historical_yield.data}>
                  <XAxis dataKey="year" />
                  <YAxis />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="yield"
                    stroke="#10b981"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    )}
    </div>
  );
}