import { useEffect, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { STATES } from "./data/states";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function requestApi(path, options) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, options);
  } catch (error) {
    if (error.name === "AbortError") {
      throw error;
    }
    throw new Error(
      "Can't reach the prediction service. Check that the backend is running.",
      { cause: error },
    );
  }

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const message = typeof data?.detail === "string" ? data.detail : "The request failed.";
    throw new Error(message);
  }

  return data;
}

function formatNumber(value, decimals = 1) {
  if (value === null || value === undefined || value === "") {
    return "—";
  }

  const number = Number(value);
  return Number.isFinite(number)
    ? number.toLocaleString(undefined, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      })
    : "—";
}

function Metric({ label, value, unit, accent = false }) {
  return (
    <div className={`metric${accent ? " metric-accent" : ""}`}>
      <p className="metric-label">{label}</p>
      <p className="metric-value">
        {value}
        {unit && <span className="metric-unit">{unit}</span>}
      </p>
    </div>
  );
}

export default function YieldPredictor() {
  const [form, setForm] = useState({ state: "", county: "", crop: "" });
  const [crops, setCrops] = useState([]);
  const [counties, setCounties] = useState([]);
  const [countiesLoading, setCountiesLoading] = useState(false);
  const [cropsLoading, setCropsLoading] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [scenario, setScenario] = useState({
    price: "",
    cost: "",
    acres: "100",
  });

  useEffect(() => {
    const controller = new AbortController();

    requestApi("/crops", { signal: controller.signal })
      .then((data) => {
        if (!Array.isArray(data.crops)) {
          throw new Error("The prediction service returned an invalid crop list.");
        }
        setCrops(data.crops);
      })
      .catch((requestError) => {
        if (requestError.name !== "AbortError") {
          setError(requestError.message);
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setCropsLoading(false);
        }
      });

    return () => controller.abort();
  }, []);

  useEffect(() => {
    if (!form.state) {
      return undefined;
    }

    const controller = new AbortController();

    requestApi(`/counties/${encodeURIComponent(form.state)}`, {
      signal: controller.signal,
    })
      .then((data) => {
        if (!Array.isArray(data.counties)) {
          throw new Error("The prediction service returned an invalid county list.");
        }
        setCounties(data.counties);
      })
      .catch((requestError) => {
        if (requestError.name !== "AbortError") {
          setError(requestError.message);
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setCountiesLoading(false);
        }
      });

    return () => controller.abort();
  }, [form.state]);

  function handleChange(event) {
    const { name, value } = event.target;
    if (name === "state") {
      setForm((current) => ({ ...current, state: value, county: "" }));
      setCounties([]);
      setCountiesLoading(Boolean(value));
    } else {
      setForm((current) => ({ ...current, [name]: value }));
    }
    setResult(null);
    setError("");
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setResult(null);

    if (!form.state || !form.county || !form.crop) {
      setError("Choose a state, county, and crop to run a forecast.");
      return;
    }

    setLoading(true);
    try {
      const data = await requestApi("/predict-yield", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      if (!Number.isFinite(Number(data.predicted_yield))) {
        throw new Error("The service returned a prediction that could not be displayed.");
      }
      setResult(data);
      setScenario({
        price: data.profit?.price_per_unit == null
          ? ""
          : Number(data.profit.price_per_unit).toFixed(2),
        cost: data.profit?.cost_per_acre == null
          ? ""
          : String(data.profit.cost_per_acre),
        acres: "100",
      });
    } catch (requestError) {
      setError(requestError.message || "Unable to generate a forecast.");
    } finally {
      setLoading(false);
    }
  }

  const history = Array.isArray(result?.historical_yield)
    ? [...result.historical_yield]
        .filter((row) => (
          row.year !== null
          && row.year !== undefined
          && row.yield !== null
          && row.yield !== undefined
          && row.year !== ""
          && row.yield !== ""
          && Number.isFinite(Number(row.year))
          && Number.isFinite(Number(row.yield))
        ))
        .sort((a, b) => Number(a.year) - Number(b.year))
    : [];
  const annualHistory = Object.values(history.reduce((years, row) => {
    const year = Number(row.year);
    if (!years[year]) {
      years[year] = { year, total: 0, count: 0 };
    }
    years[year].total += Number(row.yield);
    years[year].count += 1;
    return years;
  }, {}))
    .map(({ year, total, count }) => ({
      year,
      yield: total / count,
    }))
    .sort((a, b) => a.year - b.year);
  const recentHistory = annualHistory.slice(-5);
  const recentAverage = recentHistory.length
    ? recentHistory.reduce((total, row) => total + row.yield, 0) / recentHistory.length
    : null;
  const lowestHistoricalYield = annualHistory.length
    ? Math.min(...annualHistory.map((row) => row.yield))
    : null;
  const highestHistoricalYield = annualHistory.length
    ? Math.max(...annualHistory.map((row) => row.yield))
    : null;
  const predictedYield = Number(result?.predicted_yield);
  const yieldDifference = recentAverage === null
    ? null
    : predictedYield - recentAverage;
  const yieldDifferencePercent = recentAverage
    ? (yieldDifference / recentAverage) * 100
    : null;
  const weather = result?.weather;
  const forecast = weather?.forecast || {};
  const historicalWeather = weather?.historical_average || {};
  const profit = result?.profit;
  const pricePerUnit = scenario.price === "" ? null : Number(scenario.price);
  const costPerAcre = scenario.cost === "" ? null : Number(scenario.cost);
  const farmAcres = scenario.acres === "" ? null : Number(scenario.acres);
  const validScenario = (
    Number.isFinite(pricePerUnit)
    && pricePerUnit >= 0
    && Number.isFinite(costPerAcre)
    && costPerAcre >= 0
    && Number.isFinite(farmAcres)
    && farmAcres > 0
  );
  const scenarioRevenuePerAcre = validScenario
    ? predictedYield * pricePerUnit
    : null;
  const scenarioProfitPerAcre = validScenario
    ? scenarioRevenuePerAcre - costPerAcre
    : null;
  const scenarioRevenue = validScenario
    ? scenarioRevenuePerAcre * farmAcres
    : null;
  const scenarioCost = validScenario
    ? costPerAcre * farmAcres
    : null;
  const scenarioProfit = validScenario
    ? scenarioProfitPerAcre * farmAcres
    : null;

  return (
    <div className={`forecast-layout${result ? " forecast-layout-results" : ""}`}>
      <section className="form-panel" aria-labelledby="form-title">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">YOUR FARM</p>
            <h2 id="form-title">Build a forecast</h2>
          </div>
        </div>

        <p className="panel-description">
          Select a location and crop to see a yield estimate based on your
          historical records and the latest forecast.
        </p>

        {error && (
          <div className="error-message" role="alert">
            <span className="error-icon" aria-hidden="true">!</span>
            <span>{error}</span>
          </div>
        )}

        <form className="forecast-form" onSubmit={handleSubmit}>
          <label className="field">
            <span className="field-label">State</span>
            <select name="state" value={form.state} onChange={handleChange}>
              <option value="">Choose a state</option>
              {STATES.map((state) => (
                <option key={state} value={state}>{state}</option>
              ))}
            </select>
          </label>

          <label className="field">
            <span className="field-label">County</span>
            <select
              name="county"
              value={form.county}
              onChange={handleChange}
              disabled={!form.state || countiesLoading || counties.length === 0}
            >
              <option value="">
                {countiesLoading ? "Loading counties…" : "Choose a county"}
              </option>
              {counties.map((county) => (
                <option key={county} value={county}>{county}</option>
              ))}
            </select>
          </label>

          <label className="field">
            <span className="field-label">Crop</span>
            <select
              name="crop"
              value={form.crop}
              onChange={handleChange}
              disabled={cropsLoading || crops.length === 0}
            >
              <option value="">
                {cropsLoading ? "Loading crops…" : "Choose a crop"}
              </option>
              {crops.map((crop) => (
                <option key={crop} value={crop}>{crop}</option>
              ))}
            </select>
          </label>

          <button className="submit-button" type="submit" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner" aria-hidden="true" />
                Gathering forecast…
              </>
            ) : (
              <>
                Generate forecast
                <span aria-hidden="true">→</span>
              </>
            )}
          </button>
        </form>

        <p className="form-note">
          Forecasts are estimates and should be used as a planning aid.
        </p>
      </section>

      <section className="results-panel" aria-live="polite">
        {!result ? (
          <div className="empty-state">
            <div className="empty-art" aria-hidden="true">
              <span className="sun" />
              <span className="field-line field-line-one" />
              <span className="field-line field-line-two" />
              <span className="field-line field-line-three" />
              <span className="sprout">✳</span>
            </div>
            <p className="eyebrow">YOUR NEXT SEASON</p>
            <h2>Your forecast starts here</h2>
            <p>Choose your county and crop to explore expected yield, weather, and profitability.</p>
          </div>
        ) : (
          <div className="results-content">
            <div className="results-heading">
              <div>
                <p className="eyebrow">FORECAST OVERVIEW</p>
                <h2>{result.location?.county}, {result.location?.state}</h2>
                <p className="location-subtitle">{result.location?.crop} · Estimated for {new Date().getFullYear()}</p>
              </div>
              <span className="result-badge">Model estimate</span>
            </div>

            <div className="metrics-grid">
              <Metric
                label="Predicted yield"
                value={formatNumber(result.predicted_yield, 2)}
                unit=" bu / acre"
                accent
              />
              <Metric
                label={recentHistory.length
                  ? `Latest ${recentHistory.length} recorded-year avg`
                  : "Historical average unavailable"}
                value={formatNumber(recentAverage, 2)}
                unit=" bu / acre"
              />
            </div>

            {annualHistory.length > 0 && (
              <section className="data-section history-comparison">
                <div className="section-title-row">
                  <div>
                    <p className="eyebrow">HOW IT COMPARES</p>
                    <h3>Forecast vs. county history</h3>
                  </div>
                  <span className="section-caption">
                    Latest {recentHistory.length} recorded years · {annualHistory.length} total
                  </span>
                </div>
                {yieldDifference !== null && (
                  <p className={`comparison-summary${yieldDifference >= 0 ? " comparison-positive" : " comparison-negative"}`}>
                    {yieldDifference === 0
                      ? "Forecast is in line with the recent average."
                      : (
                        <>
                          Forecast is <strong>{formatNumber(Math.abs(yieldDifference), 2)} bu / acre</strong>
                          {yieldDifference > 0 ? " above" : " below"} the recent average
                          {yieldDifferencePercent !== null && (
                            <> ({formatNumber(Math.abs(yieldDifferencePercent))}%)</>
                          )}
                        </>
                      )}
                  </p>
                )}
                <div className="history-range">
                  <div className="range-label">
                    <span>Lowest annual avg</span>
                    <strong>{formatNumber(lowestHistoricalYield, 2)} bu / acre</strong>
                  </div>
                  <div className="range-track" aria-hidden="true">
                    <span className="range-line" />
                    <span className="range-marker range-marker-low" />
                    <span className="range-marker range-marker-high" />
                  </div>
                  <div className="range-label range-label-right">
                    <span>Highest annual avg</span>
                    <strong>{formatNumber(highestHistoricalYield, 2)} bu / acre</strong>
                  </div>
                </div>
                <p className="history-note">
                  Historical range uses annual averages from the available USDA records.
                  The forecast is a model estimate, not a guarantee.
                </p>
              </section>
            )}

            <section className="data-section scenario-section">
              <div className="section-title-row">
                <div>
                  <p className="eyebrow">PLAN YOUR NUMBERS</p>
                  <h3>Farm scenario</h3>
                </div>
                {profit && (
                  <span className="section-caption">
                    Price defaults from {profit.price_year} USDA data
                  </span>
                )}
              </div>
              <div className="scenario-inputs">
                <label className="scenario-field">
                  <span>Crop price <small>$/bu</small></span>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={scenario.price}
                    onChange={(event) => setScenario((current) => ({
                      ...current,
                      price: event.target.value,
                    }))}
                    aria-label="Crop price per bushel"
                  />
                </label>
                <label className="scenario-field">
                  <span>Growing cost <small>$/acre</small></span>
                  <input
                    type="number"
                    min="0"
                    step="1"
                    value={scenario.cost}
                    onChange={(event) => setScenario((current) => ({
                      ...current,
                      cost: event.target.value,
                    }))}
                    aria-label="Growing cost per acre"
                  />
                </label>
                <label className="scenario-field">
                  <span>Farm size <small>acres</small></span>
                  <input
                    type="number"
                    min="0.01"
                    step="1"
                    value={scenario.acres}
                    onChange={(event) => setScenario((current) => ({
                      ...current,
                      acres: event.target.value,
                    }))}
                    aria-label="Farm size in acres"
                  />
                </label>
              </div>
              {validScenario ? (
                <div className="scenario-results">
                  <div className="scenario-total">
                    <span>Estimated whole-farm profit</span>
                    <strong>${formatNumber(scenarioProfit, 2)}</strong>
                    <small>${formatNumber(scenarioProfitPerAcre, 2)} per acre</small>
                  </div>
                  <div className="scenario-breakdown">
                    <span>Projected revenue<strong>${formatNumber(scenarioRevenue, 2)}</strong></span>
                    <span>Estimated costs<strong>${formatNumber(scenarioCost, 2)}</strong></span>
                    <span>Based on<strong>{formatNumber(farmAcres, 0)} acres</strong></span>
                  </div>
                </div>
              ) : (
                <p className="scenario-note" role="status">
                  Enter a valid price, cost, and farm size to calculate your scenario.
                </p>
              )}
              <p className="scenario-note">
                Adjust these assumptions to match your operation. Estimates exclude
                any costs not included in the growing-cost input.
              </p>
              {profit && (
                <p className="profit-source-note">
                  Starting assumptions: ${formatNumber(profit.price_per_unit, 2)} / bu crop price
                  and ${formatNumber(profit.cost_per_acre, 2)} / acre growing cost.
                </p>
              )}
            </section>

            {weather && (
              <section className="data-section weather-section">
                <div className="section-title-row">
                  <div>
                    <p className="eyebrow">LOCAL CONDITIONS</p>
                    <h3>Weather snapshot</h3>
                  </div>
                  <span className="section-caption">16-day forecast · county historical average</span>
                </div>
                <div className="weather-grid">
                  <Metric label="Forecast temperature" value={formatNumber(forecast.avg_temp)} unit=" °C" />
                  <Metric label="Forecast rainfall" value={formatNumber(forecast.total_rain)} unit=" mm" />
                  <Metric label="Historical temperature" value={formatNumber(historicalWeather.temperature)} unit=" °C" />
                  <Metric label="Historical rainfall" value={formatNumber(historicalWeather.rain)} unit=" mm" />
                </div>
              </section>
            )}

            {annualHistory.length > 0 && (
              <section className="data-section history-section">
                <div className="section-title-row">
                  <div>
                    <p className="eyebrow">USDA RECORDS</p>
                    <h3>Yield history</h3>
                  </div>
                  <span className="section-caption">
                    {annualHistory[0].year}–{annualHistory.at(-1).year} · annual avg, bu / acre
                  </span>
                </div>
                <div className="chart-wrap">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={annualHistory} margin={{ top: 10, right: 12, left: -18, bottom: 0 }}>
                      <CartesianGrid stroke="#e9eee8" strokeDasharray="4 5" vertical={false} />
                      <XAxis dataKey="year" tickLine={false} axisLine={false} tick={{ fill: "#829087", fontSize: 11 }} />
                      <YAxis tickLine={false} axisLine={false} tick={{ fill: "#829087", fontSize: 11 }} />
                      <Tooltip
                        contentStyle={{ border: "1px solid #e6ebe4", borderRadius: 12, boxShadow: "0 8px 24px #172a1a14" }}
                        formatter={(value) => [`${formatNumber(value, 2)} bu / acre`, "Yield"]}
                        labelFormatter={(label) => `Year ${label}`}
                      />
                      <Line
                        type="monotone"
                        dataKey="yield"
                        stroke="#26734d"
                        strokeWidth={3}
                        dot={{ r: 3, fill: "#26734d", strokeWidth: 0 }}
                        activeDot={{ r: 5, fill: "#26734d" }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </section>
            )}
          </div>
        )}
      </section>
    </div>
  );
}
