"""
GeoManim - Geospatial visualization and animation library using Manim.

A Python package for creating beautiful animated maps and geospatial visualizations
using the Manim animation engine.
"""

from geomanim.__version__ import __version__
from geomanim.map2d import GeoMap
from geomanim.data import (
    load_geojson,
    load_shapefile,
    load_csv,
    load_data,
    get_world_boundaries,
)
from geomanim.utils import (
    get_color_scheme,
    value_to_color,
    create_color_legend,
)
from geomanim.animate import animate

__all__ = [
    "__version__",
    "GeoMap",
    "load_geojson",
    "load_shapefile",
    "load_csv",
    "load_data",
    "get_world_boundaries",
    "get_color_scheme",
    "value_to_color",
    "create_color_legend",
    "animate",
]
