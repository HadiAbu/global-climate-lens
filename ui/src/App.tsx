import { useState } from "react";

import { HeaderControls } from "./components/HeaderControls";
import { MapChoropleth } from "./components/MapChoropleth";
import { ChartsPanel } from "./components/ChartsPanel";
import { useDebouncedValue } from "./hooks/useDebouncedValue";
import type { Metric } from "./types";

const DEFAULT_YEAR = 2020;
const DEFAULT_METRIC: Metric = "co2_total_mt";

export default function App() {
  const [year, setYear] = useState(DEFAULT_YEAR);
  const [metric, setMetric] = useState<Metric>(DEFAULT_METRIC);
  const [selectedIso3, setSelectedIso3] = useState<string | null>(null);

  const debouncedYear = useDebouncedValue(year, 350);
  const isDebouncing = debouncedYear !== year;

  return (
    <div className="app-shell">
      <HeaderControls
        year={year}
        onYearChange={setYear}
        metric={metric}
        onMetricChange={setMetric}
        selectedIso3={selectedIso3}
        isDebouncing={isDebouncing}
      />

      <main className="main-grid">
        <MapChoropleth
          year={debouncedYear}
          metric={metric}
          selectedIso3={selectedIso3}
          onSelectIso3={setSelectedIso3}
        />
        <ChartsPanel selectedIso3={selectedIso3} metric={metric} />
      </main>
    </div>
  );
}
