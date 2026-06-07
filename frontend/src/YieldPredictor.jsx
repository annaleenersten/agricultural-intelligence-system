import { useState } from "react";

export default function YieldPredictor() {
  const [form, setForm] = useState({
    location: "",
    crop: "",
    year: "",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  function handleChange(e) {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/predict-yield", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      const data = await res.json();
      setResult(data.predicted_yield);
    } catch (err) {
      console.error(err);
      alert("Error fetching prediction");
    }

    setLoading(false);
  }

  return (
    <div className="space-y-6">

      {/* FORM */}
      <form onSubmit={handleSubmit} className="space-y-4">

        <input
          name="location"
          placeholder="Location (e.g. WA)"
          className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 transition"
          value={form.location}
          onChange={handleChange}
        />

        <input
          name="crop"
          placeholder="Crop (e.g. CORN)"
          className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 transition"
          value={form.crop}
          onChange={handleChange}
        />

        <input
          name="year"
          placeholder="Year (e.g. 2018)"
          className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 transition"
          value={form.year}
          onChange={handleChange}
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 rounded-xl bg-emerald-500 text-white font-medium hover:bg-emerald-600 transition disabled:opacity-50"
        >
          {loading ? "Analyzing weather" : "Predict Yield"}
        </button>

      </form>

      {/* RESULT */}
      {result !== null && (
        <div className="p-5 rounded-2xl bg-emerald-50 border border-emerald-100 text-emerald-800 text-center">
          <p className="text-sm font-medium text-emerald-600">
            Predicted Yield
          </p>
          <p className="text-3xl font-bold mt-1">
            {result}
          </p>
        </div>
      )}

    </div>
  );
}