import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import cv2

def parse_netcdf_file(filepath: str) -> Dict[str, Any]:
    """
    Parses a NetCDF (.nc) satellite observation file, extracting:
    - variables list and dimensions
    - spatial coordinates (lat/lon grids or bounds)
    - representative 2D satellite brightness temperature / radiance array converted to an RGB visualization
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"NetCDF file not found: {filepath}")

    metadata = {
        "filename": path.name,
        "format": "NetCDF",
        "variables": [],
        "dimensions": {},
        "attributes": {},
        "has_spatial_grid": False,
        "bounds": None
    }

    # Attempt to open with netCDF4 or xarray or scipy
    nc_data = None
    try:
        import netCDF4 as nc
        with nc.Dataset(filepath, 'r') as ds:
            metadata["variables"] = list(ds.variables.keys())
            for dim_name, dim in ds.dimensions.items():
                metadata["dimensions"][dim_name] = len(dim)
            
            # Find candidate brightness temp or radiance variable
            candidate_vars = ['IMG_TIR1', 'TIR1', 'IR', 'BT', 'brightness_temp', 'temp', 'data', 'radiance']
            target_var = None
            for v in candidate_vars:
                if v in ds.variables:
                    target_var = v
                    break
            if target_var is None and len(ds.variables) > 0:
                # Pick the first 2D or 3D variable
                for v in ds.variables:
                    if len(ds.variables[v].shape) in [2, 3]:
                        target_var = v
                        break
            
            if target_var:
                raw_arr = np.ma.filled(ds.variables[target_var][:], np.nan)
                arr = np.asarray(raw_arr, dtype=np.float32).squeeze()
                while arr.ndim > 2:
                    arr = arr[0]
                if arr.ndim != 2:
                    raise ValueError(f"Selected variable {target_var} is not a 2D satellite grid")
                finite = arr[np.isfinite(arr)]
                if finite.size == 0:
                    raise ValueError(f"Selected variable {target_var} contains no finite values")
                arr = np.nan_to_num(arr, nan=float(np.median(finite)))
                # Normalize to 0-255
                norm = ((arr - np.min(arr)) / (np.max(arr) - np.min(arr) + 1e-6) * 255).astype(np.uint8)
                bgr = cv2.applyColorMap(norm, cv2.COLORMAP_TURBO)
                metadata["extracted_image_rgb"] = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                metadata["selected_variable"] = target_var

            # Extract lat / lon if available
            lat_names = ['lat', 'latitude', 'Latitude', 'LAT']
            lon_names = ['lon', 'longitude', 'Longitude', 'LON']
            lat_var = next((v for v in lat_names if v in ds.variables), None)
            lon_var = next((v for v in lon_names if v in ds.variables), None)
            if lat_var and lon_var:
                lats = ds.variables[lat_var][:]
                lons = ds.variables[lon_var][:]
                metadata["bounds"] = {
                    "min_lat": float(np.min(lats)),
                    "max_lat": float(np.max(lats)),
                    "min_lon": float(np.min(lons)),
                    "max_lon": float(np.max(lons)),
                }
                metadata["has_spatial_grid"] = True

            return metadata

    except ImportError as exc:
        raise RuntimeError("NetCDF support requires the netCDF4 package") from exc
    except Exception as e:
        raise RuntimeError(f"Error parsing NetCDF file: {str(e)}")
