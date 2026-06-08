// import { useState } from "react";
// import { STATES } from "./data/states";
// import { CROPS } from "./data/crops";

// export default function YieldPredictor() {
//   const [form, setForm] = useState({
//     location: "",
//     crop: "",
//   });

//   const [result, setResult] = useState(null);
//   const [loading, setLoading] = useState(false);

//   function handleChange(e) {
//     setForm({
//       ...form,
//       [e.target.name]: e.target.value,
//     });
//   }

//   async function handleSubmit(e) {

//     if (!form.location || !form.crop) {
//       alert("Please fill all fields");
//       setLoading(false);
//       return;
//     }
//     e.preventDefault();
//     setLoading(true);
//     setResult(null);

//     try {
//       const res = await fetch("http://127.0.0.1:8000/predict-yield", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify(form),
//       });

//       const data = await res.json();
//       setResult(data);
//     } catch (err) {
//       console.error(err);
//       alert("Error fetching prediction");
//     }

//     setLoading(false);
//   }

//   return (
//     <div className="space-y-6">

//       {/* FORM */}
//       <form onSubmit={handleSubmit} className="space-y-4">

//         <select
//           name="location"
//           value={form.location}
//           onChange={handleChange}
//           className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 transition"
//         >
//           <option value="">Select State</option>

//           {STATES.map((state) => (
//             <option key={state} value={state}>
//               {state}
//             </option>
//           ))}
//         </select>

//         <select
//           name="crop"
//           value={form.crop}
//           onChange={handleChange}
//           className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 transition"
//         >
//           <option value="">Select Crop</option>

//           {CROPS.map((crop) => (
//             <option key={crop} value={crop}>
//               {crop}
//             </option>
//           ))}
//         </select>

//         <button
//           type="submit"
//           disabled={loading}
//           className="w-full py-3 rounded-xl bg-emerald-500 text-white font-medium hover:bg-emerald-600 transition disabled:opacity-50"
//         >
//           {loading ? "Analyzing weather" : "Predict Yield"}
//         </button>

//       </form>

//       {/* RESULT */}
//       {result && (
//       <div className="space-y-4 mt-6">
        
//         {/* Prediction Card */}
//         <div className="p-5 rounded-2xl bg-emerald-50 border border-emerald-100 text-center">
//           <p className="text-sm font-medium text-emerald-600">
//             Predicted Yield
//           </p>

//           <p className="text-3xl font-bold mt-1">
//             {result.predicted_yield.toFixed(2)}
//           </p>
//         </div>

//         {/* Historical Average */}
//         <div className="p-5 rounded-2xl bg-gray-50 border border-gray-200 text-center">
//           <p className="text-sm font-medium text-gray-600">
//             Historical Average
//           </p>

//           <p className="text-2xl font-semibold mt-1">
//             {result.historical_avg ?? "No data"}
//           </p>
//         </div>

//             {/* Historical Data */}
//         {result.historical_data?.length > 0 && (
//           <div className="p-5 rounded-2xl bg-white border border-gray-200">
            
//             <h3 className="font-semibold mb-3">
//               Recent Yield History
//             </h3>

//             <div className="space-y-2">
//               {result.historical_data.map((item) => (
//                 <div
//                   key={item.year}
//                   className="flex justify-between text-sm border-b py-1"
//                 >
//                   <span className="text-gray-600">
//                     {item.year}
//                   </span>

//                   <span className="font-medium">
//                     {item.yield}
//                   </span>
//                 </div>
//               ))}
//             </div>

//           </div>
//         )}

//           </div>
// )}

//     </div>
//   );
// }

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
    location: "",
    crop: "",
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

    if (!form.location || !form.crop) {
      alert("Please fill all fields");
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/predict-yield", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      const data = await res.json();
      setResult(data);
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

        <select
          name="location"
          value={form.location}
          onChange={handleChange}
          className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 transition"
        >
          <option value="">Select State</option>
          {STATES.map((state) => (
            <option key={state} value={state}>
              {state}
            </option>
          ))}
        </select>

        <select
          name="crop"
          value={form.crop}
          onChange={handleChange}
          className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 transition"
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
          className="w-full py-3 rounded-xl bg-emerald-500 text-white font-medium hover:bg-emerald-600 transition disabled:opacity-50"
        >
          {loading ? "Analyzing weather..." : "Predict Yield"}
        </button>

      </form>

      {/* RESULTS */}
      {result && (
        <div className="space-y-4 mt-6">

          {/* Prediction */}
          <div className="p-5 rounded-2xl bg-emerald-50 border border-emerald-100 text-center">
            <p className="text-sm font-medium text-emerald-600">
              Predicted Yield
            </p>

            <p className="text-3xl font-bold mt-1">
              {result.predicted_yield.toFixed(2)}
            </p>
          </div>

          {/* Historical Average */}
          <div className="p-5 rounded-2xl bg-gray-50 border border-gray-200 text-center">
            <p className="text-sm font-medium text-gray-600">
              Historical Average
            </p>

            <p className="text-2xl font-semibold mt-1">
              {result.historical_avg ?? "No data"}
            </p>
          </div>

          {/* Chart */}
          {result.historical_data?.length > 0 && (
            <div className="p-5 rounded-2xl bg-white border border-gray-200">
              <h3 className="font-semibold mb-3">
                Recent Yield History
              </h3>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={result.historical_data}>
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