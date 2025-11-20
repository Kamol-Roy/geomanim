"""Utility functions and helpers."""

from geomanim.utils.coordinates import (
    lat_lon_to_mercator,
    lat_lon_to_equirectangular,
    lat_lon_to_robinson,
    normalize_coords,
    get_projection_function,
)

from geomanim.utils.colors import (
    get_color_scheme,
    value_to_color,
    interpolate_color_range,
    create_color_legend,
    COLOR_SCHEMES,
)

__all__ = [
    "lat_lon_to_mercator",
    "lat_lon_to_equirectangular",
    "lat_lon_to_robinson",
    "normalize_coords",
    "get_projection_function",
    "get_color_scheme",
    "value_to_color",
    "interpolate_color_range",
    "create_color_legend",
    "COLOR_SCHEMES",
]
