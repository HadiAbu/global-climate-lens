export type Metric = "co2_total_mt" | "co2_per_capita";

export interface GeoFeatureProperties {
  iso3: string;
  name: string;
  value: number | null;
  year: number;
  metric: Metric;
}

export interface GeoFeature {
  type: "Feature";
  geometry: unknown;
  properties: GeoFeatureProperties;
}

export interface GeoFeatureCollection {
  type: "FeatureCollection";
  features: GeoFeature[];
}

export interface GlobalCo2Point {
  year: number;
  co2_total_mt: number | null;
  co2_cumulative_mt: number | null;
}

export interface GlobalTemperaturePoint {
  year: number;
  temp_anomaly_c: number | null;
  temp_uncertainty_c: number | null;
}

export interface CountryCo2Point {
  year: number;
  co2_total_mt: number | null;
  co2_per_capita: number | null;
}

export interface CountryCo2Response {
  iso3: string;
  series: CountryCo2Point[];
}
