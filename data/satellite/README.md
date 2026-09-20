# Satellite Imagery Repository

Place real raw or processed satellite imagery files in this directory.

### Supported File Formats:
- **GeoTIFF / TIFF (`.tif`, `.tiff`)**: High-resolution multispectral imagery with embedded georeferencing coordinates.
- **JPEG / PNG (`.jpg`, `.jpeg`, `.png`)**: Standard infrared (TIR1), visible (VIS), or enhanced color images from:
  - INSAT-3D / INSAT-3DR (MOSDAC / ISRO)
  - GOES-East / GOES-West (NOAA)
  - Himawari-8 / Himawari-9 (JMA)
  - Sentinel-2 / Sentinel-3 (ESA)
- **NetCDF (`.nc`)**: Gridded brightness temperature and atmospheric sounding files.

### Demonstration Mode:
If real satellite files are not placed here, CycloneAI operates seamlessly in **Demo Mode** using the calibrated infrared sample in `data/demo/demo_satellite_ir.png`.
