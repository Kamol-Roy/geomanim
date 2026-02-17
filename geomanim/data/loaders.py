"""Data loading utilities for geospatial data."""

import geopandas as gpd
import pandas as pd
from pathlib import Path
from typing import Optional, Union
from shapely.geometry import Point
import warnings


def _is_url(path: Union[str, Path]) -> bool:
    """Check if a path is an HTTP/HTTPS URL."""
    return isinstance(path, str) and path.startswith(("http://", "https://"))


def load_geojson(
    filepath: Union[str, Path],
    **kwargs,
) -> gpd.GeoDataFrame:
    """
    Load a GeoJSON file from a local path or URL.

    Args:
        filepath: Path to the GeoJSON file, or an HTTP/HTTPS URL
        **kwargs: Additional arguments passed to geopandas.read_file

    Returns:
        GeoDataFrame containing the loaded data

    Raises:
        FileNotFoundError: If the local file doesn't exist
        ValueError: If the file cannot be parsed
    """
    if _is_url(filepath):
        try:
            gdf = gpd.read_file(filepath, **kwargs)
            return gdf
        except Exception as e:
            raise ValueError(f"Failed to load GeoJSON from URL: {e}")

    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    try:
        gdf = gpd.read_file(filepath, **kwargs)
        return gdf
    except Exception as e:
        raise ValueError(f"Failed to load GeoJSON file: {e}")


def load_shapefile(
    filepath: Union[str, Path],
    **kwargs,
) -> gpd.GeoDataFrame:
    """
    Load a Shapefile from a local path or URL.

    Args:
        filepath: Path to the .shp file, or an HTTP/HTTPS URL
        **kwargs: Additional arguments passed to geopandas.read_file

    Returns:
        GeoDataFrame containing the loaded data

    Raises:
        FileNotFoundError: If the local file doesn't exist
        ValueError: If the file cannot be parsed
    """
    if _is_url(filepath):
        try:
            gdf = gpd.read_file(filepath, **kwargs)
            return gdf
        except Exception as e:
            raise ValueError(f"Failed to load Shapefile from URL: {e}")

    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    try:
        gdf = gpd.read_file(filepath, **kwargs)
        return gdf
    except Exception as e:
        raise ValueError(f"Failed to load Shapefile: {e}")


def load_csv(
    filepath: Union[str, Path],
    lat_col: str = "latitude",
    lon_col: str = "longitude",
    crs: str = "EPSG:4326",
    **kwargs,
) -> gpd.GeoDataFrame:
    """
    Load a CSV file with latitude/longitude columns and convert to GeoDataFrame.

    Args:
        filepath: Path to the CSV file
        lat_col: Name of the latitude column
        lon_col: Name of the longitude column
        crs: Coordinate reference system (default: WGS84)
        **kwargs: Additional arguments passed to pandas.read_csv

    Returns:
        GeoDataFrame with Point geometries

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If required columns are missing
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    try:
        # Load CSV
        df = pd.read_csv(filepath, **kwargs)

        # Check for required columns
        if lat_col not in df.columns:
            raise ValueError(
                f"Latitude column '{lat_col}' not found in CSV. "
                f"Available columns: {', '.join(df.columns)}"
            )
        if lon_col not in df.columns:
            raise ValueError(
                f"Longitude column '{lon_col}' not found in CSV. "
                f"Available columns: {', '.join(df.columns)}"
            )

        # Drop rows with missing coordinates
        df = df.dropna(subset=[lat_col, lon_col])

        if len(df) == 0:
            warnings.warn("No valid coordinates found in CSV file")
            return gpd.GeoDataFrame()

        # Create Point geometries
        geometry = [Point(xy) for xy in zip(df[lon_col], df[lat_col])]

        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=crs)

        return gdf

    except pd.errors.ParserError as e:
        raise ValueError(f"Failed to parse CSV file: {e}")
    except Exception as e:
        raise ValueError(f"Failed to load CSV file: {e}")


def load_data(
    filepath: Union[str, Path],
    file_type: Optional[str] = None,
    **kwargs,
) -> gpd.GeoDataFrame:
    """
    Auto-detect file type and load geospatial data.

    Args:
        filepath: Path to the data file
        file_type: Force a specific file type ('geojson', 'shapefile', 'csv')
                   If None, will auto-detect from file extension
        **kwargs: Additional arguments passed to the specific loader

    Returns:
        GeoDataFrame containing the loaded data

    Raises:
        ValueError: If file type cannot be determined or is unsupported
    """
    # For URLs, infer type from URL path or use gpd.read_file directly
    if _is_url(filepath):
        if file_type is None:
            url_lower = str(filepath).lower().split("?")[0]
            if url_lower.endswith(".geojson") or url_lower.endswith(".json"):
                file_type = "geojson"
            elif url_lower.endswith(".shp"):
                file_type = "shapefile"
            elif url_lower.endswith(".csv"):
                file_type = "csv"
            else:
                file_type = "geojson"

    filepath = Path(filepath) if not _is_url(filepath) else filepath

    # Determine file type
    if file_type is None:
        suffix = Path(filepath).suffix.lower()
        if suffix in [".geojson", ".json"]:
            file_type = "geojson"
        elif suffix == ".shp":
            file_type = "shapefile"
        elif suffix == ".csv":
            file_type = "csv"
        else:
            # Try geopandas auto-detection for other formats
            try:
                return gpd.read_file(filepath, **kwargs)
            except Exception as e:
                raise ValueError(
                    f"Could not determine file type for '{filepath}'. "
                    f"Please specify file_type parameter. Error: {e}"
                )

    # Load based on file type
    if file_type == "geojson":
        return load_geojson(filepath, **kwargs)
    elif file_type == "shapefile":
        return load_shapefile(filepath, **kwargs)
    elif file_type == "csv":
        return load_csv(filepath, **kwargs)
    else:
        raise ValueError(
            f"Unsupported file type: '{file_type}'. "
            f"Supported types: geojson, shapefile, csv"
        )


def get_world_boundaries(resolution: str = "110m") -> gpd.GeoDataFrame:
    """
    Get world country boundaries from Natural Earth data (if available).

    This is a convenience function that attempts to load world boundaries.
    If Natural Earth data is not available, returns an empty GeoDataFrame.

    Args:
        resolution: Resolution of the boundaries ('10m', '50m', '110m')
                   Lower numbers = higher resolution = more detail

    Returns:
        GeoDataFrame with country boundaries
    """
    try:
        # Try to use Natural Earth data from geopandas datasets
        world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
        return world
    except Exception:
        warnings.warn(
            "Could not load world boundaries. "
            "Please provide your own data or install additional datasets."
        )
        return gpd.GeoDataFrame()
