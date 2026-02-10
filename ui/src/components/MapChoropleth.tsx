import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { GeoJSON, MapContainer, TileLayer } from "react-leaflet";
import L, { type PathOptions } from "leaflet";

import { fetchMapCountries } from "../lib/api";
import type { GeoFeature, Metric } from "../types";

interface MapChoroplethProps {
  year: number;
  metric: Metric;
  selectedIso3: string | null;
  onSelectIso3: (iso3: string) => void;
}

const COLOR_RAMP = ["#eff3ff", "#c6dbef", "#9ecae1", "#6baed6", "#3182bd", "#08519c"];

export function MapChoropleth({ year, metric, selectedIso3, onSelectIso3 }: MapChoroplethProps) {
  const mapQuery = useQuery({
    queryKey: ["spatial-map-countries", year, metric],
    queryFn: () => fetchMapCountries(year, metric),
    placeholderData: (previous) => previous,
  });

  const breaks = useMemo(() => {
    if (!mapQuery.data) {
      return [];
    }
    const values = mapQuery.data.features
      .map((feature) => feature.properties.value)
      .filter((value): value is number => typeof value === "number")
      .sort((a, b) => a - b);
    if (values.length === 0) {
      return [];
    }

    const quantiles = 5;
    return Array.from({ length: quantiles }, (_, index) => {
      const percentile = (index + 1) / quantiles;
      const position = Math.floor(percentile * (values.length - 1));
      return values[position];
    });
  }, [mapQuery.data]);

  const getFillColor = (value: number | null) => {
    if (value === null || Number.isNaN(value)) {
      return "#d9d9d9";
    }
    if (breaks.length === 0) {
      return COLOR_RAMP[0];
    }
    if (value <= breaks[0]) return COLOR_RAMP[0];
    if (value <= breaks[1]) return COLOR_RAMP[1];
    if (value <= breaks[2]) return COLOR_RAMP[2];
    if (value <= breaks[3]) return COLOR_RAMP[3];
    if (value <= breaks[4]) return COLOR_RAMP[4];
    return COLOR_RAMP[5];
  };

  const styleFeature = (feature?: GeoFeature): PathOptions => {
    const props = feature?.properties;
    const isSelected = props?.iso3 === selectedIso3;
    return {
      color: isSelected ? "#111827" : "#4b5563",
      fillColor: getFillColor(props?.value ?? null),
      weight: isSelected ? 1.5 : 0.6,
      fillOpacity: isSelected ? 0.9 : 0.75,
      opacity: 1,
    };
  };

  const formatValue = (value: number | null) => {
    if (value === null || Number.isNaN(value)) {
      return "No data";
    }
    if (metric === "co2_total_mt") {
      return `${value.toLocaleString(undefined, { maximumFractionDigits: 2 })} Mt`;
    }
    return `${value.toLocaleString(undefined, { maximumFractionDigits: 2 })} t/person`;
  };

  const onEachFeature = (feature: GeoFeature, layer: L.Layer) => {
    const geoLayer = layer as L.Path;
    const props = feature.properties;

    geoLayer.bindTooltip(
      `<strong>${props.name}</strong><br/>${props.iso3}<br/>${formatValue(props.value)}`,
      { sticky: true },
    );

    geoLayer.on({
      click: () => onSelectIso3(props.iso3),
      mouseover: () => {
        geoLayer.setStyle({ weight: 2, color: "#111827", fillOpacity: 0.95 });
      },
      mouseout: () => {
        geoLayer.setStyle(styleFeature(feature));
      },
    });
  };

  return (
    <section className="zone card map-zone">
      <div className="zone-title">MapChoropleth</div>

      {mapQuery.isError && (
        <div className="state-block error">
          Could not load map data: {(mapQuery.error as Error).message}
        </div>
      )}

      {!mapQuery.isError && (
        <div className="map-shell">
          <MapContainer center={[20, 0]} zoom={2} minZoom={2} scrollWheelZoom className="leaflet-map">
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {mapQuery.data && (
              <GeoJSON
                key={`${year}-${metric}-${selectedIso3 ?? "none"}`}
                data={mapQuery.data as any}
                style={(feature) => styleFeature(feature as GeoFeature)}
                onEachFeature={(feature, layer) => onEachFeature(feature as GeoFeature, layer)}
              />
            )}
          </MapContainer>

          {mapQuery.isPending && (
            <div className="map-overlay">
              <span>Loading choropleth...</span>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
