import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { fetchCountryCo2, fetchGlobalCo2, fetchGlobalTemperature } from "../lib/api";
import type { Metric } from "../types";

interface ChartsPanelProps {
  selectedIso3: string | null;
  metric: Metric;
}

export function ChartsPanel({ selectedIso3, metric }: ChartsPanelProps) {
  const globalCo2Query = useQuery({
    queryKey: ["global-co2"],
    queryFn: fetchGlobalCo2,
    staleTime: Number.POSITIVE_INFINITY,
  });

  const globalTempQuery = useQuery({
    queryKey: ["global-temperature"],
    queryFn: fetchGlobalTemperature,
    staleTime: Number.POSITIVE_INFINITY,
  });

  const countryQuery = useQuery({
    queryKey: ["country-co2-series", selectedIso3],
    queryFn: () => fetchCountryCo2(selectedIso3 as string),
    enabled: Boolean(selectedIso3),
  });

  const mergedGlobalSeries = useMemo(() => {
    if (!globalCo2Query.data || !globalTempQuery.data) {
      return [];
    }

    const tempByYear = new Map(
      globalTempQuery.data.map((point) => [point.year, point.temp_anomaly_c] as const),
    );

    return globalCo2Query.data.map((point) => ({
      year: point.year,
      co2_total_mt: point.co2_total_mt,
      co2_cumulative_mt: point.co2_cumulative_mt,
      temp_anomaly_c: tempByYear.get(point.year) ?? null,
    }));
  }, [globalCo2Query.data, globalTempQuery.data]);

  const selectedMetricLabel =
    metric === "co2_total_mt" ? "Selected metric: Total CO2 (Mt)" : "Selected metric: CO2 per capita";

  const globalLoading = globalCo2Query.isPending || globalTempQuery.isPending;
  const globalError = globalCo2Query.isError || globalTempQuery.isError;

  return (
    <section className="zone card charts-zone">
      <div className="zone-title">ChartsPanel</div>

      <div className="chart-card">
        <h3>Global CO2 and Temperature</h3>
        <p className="chart-caption">{selectedMetricLabel}</p>
        {globalLoading && <div className="state-block">Loading global charts...</div>}
        {globalError && (
          <div className="state-block error">
            Could not load global series.
            {globalCo2Query.isError && <span> {(globalCo2Query.error as Error).message}</span>}
            {globalTempQuery.isError && <span> {(globalTempQuery.error as Error).message}</span>}
          </div>
        )}
        {!globalLoading && !globalError && (
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={mergedGlobalSeries}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis yAxisId="co2" width={70} tickFormatter={(value) => Number(value).toLocaleString()} />
                <YAxis yAxisId="temp" orientation="right" width={55} />
                <Tooltip />
                <Legend />
                <Line
                  yAxisId="co2"
                  type="monotone"
                  dataKey="co2_total_mt"
                  name="CO2 total (Mt)"
                  stroke="#0ea5e9"
                  dot={false}
                  strokeWidth={2}
                />
                <Line
                  yAxisId="co2"
                  type="monotone"
                  dataKey="co2_cumulative_mt"
                  name="CO2 cumulative (Mt)"
                  stroke="#1d4ed8"
                  dot={false}
                  strokeWidth={2}
                />
                <Line
                  yAxisId="temp"
                  type="monotone"
                  dataKey="temp_anomaly_c"
                  name="Temp anomaly (C)"
                  stroke="#dc2626"
                  dot={false}
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      <div className="chart-card">
        <h3>Country CO2 Series</h3>
        {!selectedIso3 && <div className="state-block">Select a country on the map to view its time series.</div>}
        {selectedIso3 && countryQuery.isPending && <div className="state-block">Loading {selectedIso3} series...</div>}
        {selectedIso3 && countryQuery.isError && (
          <div className="state-block error">
            Could not load {selectedIso3} series: {(countryQuery.error as Error).message}
          </div>
        )}
        {selectedIso3 && countryQuery.data && (
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={countryQuery.data.series}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis yAxisId="total" width={70} />
                <YAxis yAxisId="perCapita" orientation="right" width={70} />
                <Tooltip />
                <Legend />
                <Line
                  yAxisId="total"
                  type="monotone"
                  dataKey="co2_total_mt"
                  name="CO2 total (Mt)"
                  stroke={metric === "co2_total_mt" ? "#16a34a" : "#84cc16"}
                  dot={false}
                  strokeWidth={2}
                />
                <Line
                  yAxisId="perCapita"
                  type="monotone"
                  dataKey="co2_per_capita"
                  name="CO2 per capita"
                  stroke={metric === "co2_per_capita" ? "#f97316" : "#fb923c"}
                  dot={false}
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </section>
  );
}
