import type { Metric } from "../types";

interface HeaderControlsProps {
  year: number;
  onYearChange: (year: number) => void;
  metric: Metric;
  onMetricChange: (metric: Metric) => void;
  selectedIso3: string | null;
  isDebouncing: boolean;
}

export function HeaderControls({
  year,
  onYearChange,
  metric,
  onMetricChange,
  selectedIso3,
  isDebouncing,
}: HeaderControlsProps) {
  return (
    <header className="zone card header-controls">
      <div className="title-block">
        <h1>Global Climate Lens</h1>
        <p>Country-level emissions mapped against long-run global climate signals.</p>
      </div>

      <div className="controls-grid">
        <label className="control-group" htmlFor="year-slider">
          <span className="label-row">
            <span>Year: {year}</span>
            {isDebouncing && <span className="status-chip">Updating map...</span>}
          </span>
          <input
            id="year-slider"
            type="range"
            min={1750}
            max={2020}
            value={year}
            onChange={(event) => onYearChange(Number(event.target.value))}
          />
        </label>

        <div className="control-group">
          <span className="label-row">Metric</span>
          <div className="toggle-row">
            <button
              type="button"
              className={metric === "co2_total_mt" ? "toggle-btn active" : "toggle-btn"}
              onClick={() => onMetricChange("co2_total_mt")}
            >
              Total CO2 (Mt)
            </button>
            <button
              type="button"
              className={metric === "co2_per_capita" ? "toggle-btn active" : "toggle-btn"}
              onClick={() => onMetricChange("co2_per_capita")}
            >
              CO2 per Capita
            </button>
          </div>
        </div>

        <div className="control-group">
          <span className="label-row">Selected country</span>
          <div className="selection-pill">{selectedIso3 ?? "None"}</div>
        </div>
      </div>
    </header>
  );
}
