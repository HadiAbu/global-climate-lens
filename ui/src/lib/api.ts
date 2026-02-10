import type {
  CountryCo2Response,
  GeoFeatureCollection,
  GlobalCo2Point,
  GlobalTemperaturePoint,
  Metric,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function fetchJson<T>(path: string, params?: Record<string, string | number | boolean>): Promise<T> {
  const url = new URL(path, API_BASE_URL);

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.set(key, String(value));
    });
  }

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`Request failed ${response.status}: ${response.statusText}`);
  }

  return (await response.json()) as T;
}

export function fetchMapCountries(year: number, metric: Metric): Promise<GeoFeatureCollection> {
  return fetchJson<GeoFeatureCollection>("/spatial/map/countries", {
    year,
    metric,
    limit_geometry: true,
  });
}

export function fetchGlobalCo2(): Promise<GlobalCo2Point[]> {
  return fetchJson<GlobalCo2Point[]>("/global/co2");
}

export function fetchGlobalTemperature(): Promise<GlobalTemperaturePoint[]> {
  return fetchJson<GlobalTemperaturePoint[]>("/global/temperature");
}

export function fetchCountryCo2(iso3: string): Promise<CountryCo2Response> {
  return fetchJson<CountryCo2Response>(`/spatial/country/${iso3}/co2`);
}
