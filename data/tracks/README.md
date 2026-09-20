# Cyclone Track Dataset Repository

Place historical or operational tropical cyclone track data in this directory.

### Supported Sources:
- **IBTrACS (International Best Track Archive for Climate Stewardship)**: Standard global tropical cyclone best track archive (`.csv`).
- **IMD Cyclone e-Atlas**: Best track data from the India Meteorological Department.
- **Custom CSV / JSON**: Files containing at minimum:
  - `latitude` (degrees North/South)
  - `longitude` (degrees East/West)
  - `wind_speed_kmph` or `wmo_wind` (knots or km/h)
  - `pressure_hpa` or `mslp` (hPa / mb)
  - `timestamp` (ISO format e.g. `2026-09-20 06:00:00`)

### Adding New Datasets:
You can also drag-and-drop these files directly into the **Dataset Manager** web dashboard without editing source code or restarting the server.
