"""Coordinate transformation utilities."""

import numpy as np
from typing import Tuple, Union


def lat_lon_to_mercator(lat: float, lon: float) -> Tuple[float, float]:
    """
    Convert latitude/longitude to Mercator projection coordinates.

    Args:
        lat: Latitude in degrees (-90 to 90)
        lon: Longitude in degrees (-180 to 180)

    Returns:
        Tuple of (x, y) coordinates in Mercator projection
    """
    # Clamp latitude to avoid infinity at poles
    lat = np.clip(lat, -85.0511, 85.0511)

    x = np.radians(lon)
    y = np.log(np.tan(np.pi / 4 + np.radians(lat) / 2))

    return (x, y)


def lat_lon_to_equirectangular(lat: float, lon: float) -> Tuple[float, float]:
    """
    Convert latitude/longitude to Equirectangular (Plate Carrée) projection.

    Args:
        lat: Latitude in degrees (-90 to 90)
        lon: Longitude in degrees (-180 to 180)

    Returns:
        Tuple of (x, y) coordinates
    """
    x = np.radians(lon)
    y = np.radians(lat)

    return (x, y)


def lat_lon_to_robinson(lat: float, lon: float) -> Tuple[float, float]:
    """
    Convert latitude/longitude to Robinson projection (simplified).

    Args:
        lat: Latitude in degrees (-90 to 90)
        lon: Longitude in degrees (-180 to 180)

    Returns:
        Tuple of (x, y) coordinates in Robinson projection
    """
    # Simplified Robinson projection coefficients
    # Full implementation would use lookup table
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)

    # Approximate Robinson projection
    x = lon_rad * np.cos(lat_rad * 0.5)
    y = lat_rad * 1.3

    return (x, y)


def normalize_coords(
    x: Union[float, np.ndarray],
    y: Union[float, np.ndarray],
    width: float = 14.0,
    height: float = 8.0,
) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
    """
    Normalize coordinates to fit within Manim's coordinate system.

    Args:
        x: X coordinate(s)
        y: Y coordinate(s)
        width: Desired width of the map in Manim units
        height: Desired height of the map in Manim units

    Returns:
        Tuple of normalized (x, y) coordinates
    """
    x = np.asarray(x)
    y = np.asarray(y)

    # Find bounds
    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()

    # Normalize to [0, 1]
    x_norm = (x - x_min) / (x_max - x_min) if x_max != x_min else x
    y_norm = (y - y_min) / (y_max - y_min) if y_max != y_min else y

    # Scale to desired size and center
    x_scaled = (x_norm - 0.5) * width
    y_scaled = (y_norm - 0.5) * height

    return (x_scaled, y_scaled)


def get_projection_function(projection: str):
    """
    Get the projection function by name.

    Args:
        projection: Name of projection ('mercator', 'equirectangular', 'robinson')

    Returns:
        Projection function

    Raises:
        ValueError: If projection name is not recognized
    """
    projections = {
        "mercator": lat_lon_to_mercator,
        "equirectangular": lat_lon_to_equirectangular,
        "plate_carree": lat_lon_to_equirectangular,
        "robinson": lat_lon_to_robinson,
    }

    proj_func = projections.get(projection.lower())
    if proj_func is None:
        available = ", ".join(projections.keys())
        raise ValueError(
            f"Unknown projection '{projection}'. Available: {available}"
        )

    return proj_func
