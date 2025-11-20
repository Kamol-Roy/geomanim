"""Pytest configuration and fixtures for geomanim tests."""

import pytest
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon
import tempfile
from pathlib import Path


@pytest.fixture
def sample_geodataframe():
    """Create a sample GeoDataFrame for testing."""
    data = {
        "name": ["Country A", "Country B", "Country C"],
        "population": [1000000, 2000000, 1500000],
        "gdp": [50000, 75000, 60000],
        "geometry": [
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
            Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),
            Polygon([(0, 1), (1, 1), (1, 2), (0, 2)]),
        ],
    }
    return gpd.GeoDataFrame(data, crs="EPSG:4326")


@pytest.fixture
def sample_points():
    """Create sample point coordinates for testing."""
    return [
        (40.7128, -74.0060),  # New York
        (51.5074, -0.1278),   # London
        (35.6762, 139.6503),  # Tokyo
    ]


@pytest.fixture
def sample_points_gdf():
    """Create a GeoDataFrame with point geometries."""
    data = {
        "city": ["New York", "London", "Tokyo"],
        "population": [8336817, 8982000, 13960000],
        "geometry": [
            Point(-74.0060, 40.7128),
            Point(-0.1278, 51.5074),
            Point(139.6503, 35.6762),
        ],
    }
    return gpd.GeoDataFrame(data, crs="EPSG:4326")


@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False
    ) as f:
        f.write("city,latitude,longitude,population\n")
        f.write("New York,40.7128,-74.0060,8336817\n")
        f.write("London,51.5074,-0.1278,8982000\n")
        f.write("Tokyo,35.6762,139.6503,13960000\n")
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def temp_geojson_file(sample_geodataframe):
    """Create a temporary GeoJSON file for testing."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".geojson", delete=False
    ) as f:
        temp_path = f.name

    sample_geodataframe.to_file(temp_path, driver="GeoJSON")

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)
