import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Layers, Eye, Compass, ShieldAlert, Crosshair } from 'lucide-react';

// Custom SVG Icon generators for Leaflet to ensure zero broken image asset bugs
function createCustomMarkerIcon(color, size = 28, isPulse = false) {
  const pulseHtml = isPulse ? `<div class="cyclone-marker-pulse"></div>` : '';
  return L.divIcon({
    className: 'custom-leaflet-icon',
    html: `
      <div style="position: relative; width: ${size}px; height: ${size}px; display: flex; items-center; justify-content: center;">
        ${pulseHtml}
        <div style="
          width: ${size}px; 
          height: ${size}px; 
          border-radius: 50%; 
          background: ${color}; 
          border: 2px solid #ffffff; 
          box-shadow: 0 0 14px ${color}; 
          display: flex; 
          align-items: center; 
          justify-content: center;
          color: #ffffff;
          font-weight: bold;
          font-size: 10px;
        ">
        </div>
      </div>
    `,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2]
  });
}

function MapUpdater({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (center && center[0] && center[1]) {
      map.setView(center, zoom, { animate: true });
    }
  }, [center, zoom, map]);
  return null;
}

export default function CycloneMap({ cyclone, selectedPoint, onPointClick }) {
  const [tileLayer, setTileLayer] = useState('dark');
  const [mapCenter, setMapCenter] = useState([16.0, 84.5]);
  const [mapZoom, setMapZoom] = useState(6);

  // Basemap Tile Providers
  const tileUrls = {
    dark: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    satellite: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    streets: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
  };

  const attributions = {
    dark: '&copy; CartoDB &copy; OpenStreetMap contributors',
    satellite: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye',
    streets: '&copy; OpenStreetMap contributors'
  };

  const currentLat = cyclone?.current_lat || 15.2;
  const currentLon = cyclone?.current_lon || 84.7;

  // Extract historical and forecast points
  const points = cyclone?.track_points || [];
  const historicalPoints = points.filter(p => p.point_type === 'historical');
  const forecastPoints = points.filter(p => p.point_type === 'forecast');

  // Coordinates for paths
  const historicalPath = [
    ...historicalPoints.map(p => [p.latitude, p.longitude]),
    [currentLat, currentLon]
  ];

  const forecastPath = [
    [currentLat, currentLon],
    ...forecastPoints.map(p => [p.latitude, p.longitude])
  ];

  const resetToCyclone = () => {
    setMapCenter([currentLat, currentLon]);
    setMapZoom(6);
  };

  useEffect(() => {
    if (selectedPoint) {
      setMapCenter([selectedPoint.lat, selectedPoint.lon]);
      setMapZoom(7);
    }
  }, [selectedPoint]);

  return (
    <div className="relative w-full h-[520px] rounded-2xl overflow-hidden border border-navy-750 shadow-2xl bg-navy-950">
      
      {/* Top Map Toolbar */}
      <div className="absolute top-3 left-3 z-[400] flex items-center gap-2 bg-navy-900/90 backdrop-blur-md p-1.5 rounded-xl border border-navy-750 shadow-lg">
        <span className="text-xs font-semibold text-slate-300 px-2 flex items-center gap-1.5 font-mono">
          <Compass className="w-3.5 h-3.5 text-cyan-400" />
          <span>Bay of Bengal Radar</span>
        </span>

        {/* Tile Layer Selector */}
        <div className="flex items-center gap-1 bg-navy-950 p-0.5 rounded-lg border border-navy-800 text-[11px]">
          <button
            onClick={() => setTileLayer('dark')}
            className={`px-2 py-1 rounded font-medium ${tileLayer === 'dark' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'text-slate-400'}`}
          >
            Dark Carto
          </button>
          <button
            onClick={() => setTileLayer('satellite')}
            className={`px-2 py-1 rounded font-medium ${tileLayer === 'satellite' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'text-slate-400'}`}
          >
            Satellite
          </button>
        </div>

        {/* Recenter Button */}
        <button
          onClick={resetToCyclone}
          title="Recenter Map on Cyclone Eye"
          className="p-1.5 text-slate-300 hover:text-cyan-300 hover:bg-navy-800 rounded-lg transition-colors"
        >
          <Crosshair className="w-4 h-4 text-cyan-400" />
        </button>
      </div>

      {/* Map Legend */}
      <div className="absolute bottom-4 left-4 z-[400] bg-navy-900/90 backdrop-blur-md p-3 rounded-xl border border-navy-750 shadow-xl text-xs space-y-1.5 font-mono">
        <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider mb-1">
          Track Symbology
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3.5 h-3.5 rounded-full bg-cyan-400 border-2 border-white shadow-glow-cyan" />
          <span className="text-slate-200">Current Position (Eye)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3.5 h-3.5 rounded-full bg-orange-500 border border-white" />
          <span className="text-slate-300">Forecast Fix (+6h to +48h)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3.5 h-3.5 rounded-full bg-slate-500 border border-slate-300" />
          <span className="text-slate-400">Observed History</span>
        </div>
        <div className="flex items-center gap-2 pt-1 border-t border-navy-800">
          <div className="w-4 h-0.5 bg-red-500" />
          <span className="text-red-300 text-[11px]">Predicted Trajectory</span>
        </div>
      </div>

      {/* Leaflet Map Component */}
      <MapContainer
        center={mapCenter}
        zoom={mapZoom}
        scrollWheelZoom={true}
        className="w-full h-full"
      >
        <MapUpdater center={mapCenter} zoom={mapZoom} />
        
        <TileLayer
          url={tileUrls[tileLayer]}
          attribution={attributions[tileLayer]}
        />

        {/* Historical Track Line (Muted Grey Dash) */}
        {historicalPath.length > 1 && (
          <Polyline
            positions={historicalPath}
            pathOptions={{ color: '#94a3b8', weight: 2.5, dashArray: '4, 6', opacity: 0.7 }}
          />
        )}

        {/* Predicted Track Line (Vibrant Red) */}
        {forecastPath.length > 1 && (
          <Polyline
            positions={forecastPath}
            pathOptions={{ color: '#ef4444', weight: 3.5, opacity: 0.95 }}
          />
        )}

        {/* Historical Observation Markers */}
        {historicalPoints.map((pt, idx) => (
          <Marker
            key={`hist-${idx}`}
            position={[pt.latitude, pt.longitude]}
            icon={createCustomMarkerIcon('#64748b', 16)}
          >
            <Popup>
              <div className="text-xs font-mono space-y-1">
                <div className="font-bold text-slate-300 border-b border-navy-700 pb-1">
                  Historical Observation
                </div>
                <div>Time: {pt.timestamp_str || 'Synoptic Fix'}</div>
                <div>Lat/Lon: {pt.latitude}°N, {pt.longitude}°E</div>
                <div>Wind Speed: {pt.wind_speed_kmph} km/h</div>
                <div>Pressure: {pt.pressure_hpa} hPa</div>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Current Active Cyclone Eye Marker (Blue/Cyan Pulse) */}
        <Marker
          position={[currentLat, currentLon]}
          icon={createCustomMarkerIcon('#06b6d4', 28, true)}
        >
          <Popup>
            <div className="text-xs font-mono space-y-1.5 p-1">
              <div className="font-bold text-cyan-400 text-sm border-b border-navy-700 pb-1 flex items-center justify-between">
                <span>{cyclone?.name || 'Active System'}</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-900/60 text-cyan-300 border border-cyan-700/50">LIVE</span>
              </div>
              <div className="text-slate-200 font-semibold">{cyclone?.status || 'Severe Cyclonic Storm'}</div>
              <div>Position: <strong>{currentLat}°N, {currentLon}°E</strong></div>
              <div>Max Wind: <strong>{cyclone?.wind_speed_kmph || 115} km/h</strong> (approx. {Math.round((cyclone?.wind_speed_kmph || 115) / 1.852)} kts)</div>
              <div>Pressure: <strong>{cyclone?.pressure_hpa || 978} hPa</strong></div>
              <div>Movement: <strong>{cyclone?.movement_direction || 'North-West'}</strong> @ {cyclone?.movement_speed_kmph || 18} km/h</div>
              <div className="text-[10px] text-amber-300 pt-1 border-t border-navy-800">
                Estimated direction towards NW Bay of Bengal.
              </div>
            </div>
          </Popup>
        </Marker>

        {/* Forecast Points Markers (+6h to +48h) */}
        {forecastPoints.map((pt, idx) => (
          <Marker
            key={`fore-${idx}`}
            position={[pt.latitude, pt.longitude]}
            icon={createCustomMarkerIcon('#f97316', 22)}
          >
            <Popup>
              <div className="text-xs font-mono space-y-1.5 p-1">
                <div className="font-bold text-orange-400 border-b border-navy-700 pb-1 flex items-center justify-between">
                  <span>Forecast Fix: +{pt.forecast_hour} hr</span>
                  <span className="text-[10px] px-1.5 rounded bg-orange-950 text-orange-300 border border-orange-800">Estimate</span>
                </div>
                <div className="text-slate-200 font-semibold">{pt.classification}</div>
                <div>Coordinates: <strong>{pt.latitude}°N, {pt.longitude}°E</strong></div>
                <div>Projected Wind: <strong>{pt.wind_speed_kmph} km/h</strong></div>
                <div>Central Pressure: <strong>{pt.pressure_hpa} hPa</strong></div>
                <div className="text-[10px] text-slate-400 italic pt-1 border-t border-navy-800">
                  Confidence Label: model estimate
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
