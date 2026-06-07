import { useState } from "react";

function App() {
  const [crop, setCrop] = useState("CORN");
  const [lat, setLat] = useState("48.42");
  const [lon, setLon] = useState("-122.33");
  const [year, setYear] = useState("2018");

  return (
    <div>
      <h1>Crop Yield Predictor</h1>

      <input
        value={crop}
        onChange={(e) => setCrop(e.target.value)}
        placeholder="Crop"
      />

      <input
        value={lat}
        onChange={(e) => setLat(e.target.value)}
        placeholder="Latitude"
      />

      <input
        value={lon}
        onChange={(e) => setLon(e.target.value)}
        placeholder="Longitude"
      />

      <input
        value={year}
        onChange={(e) => setYear(e.target.value)}
        placeholder="Year"
      />

      <button>Predict Yield</button>
    </div>
  );
}

export default App;
