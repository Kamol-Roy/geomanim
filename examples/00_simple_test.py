"""
Simple test animation - Creates geometric shapes as a map test

Usage:
    manim examples/00_simple_test.py SimpleTest -pql
"""

from manim import *
import geopandas as gpd
from shapely.geometry import Polygon
from geomanim import GeoMap


class SimpleTest(Scene):
    """Test animation with manually created geometric data."""

    def construct(self):
        # Create simple geometric data manually
        data = {
            "name": ["Region A", "Region B", "Region C"],
            "value": [100, 200, 150],
            "geometry": [
                Polygon([(-2, -1), (-1, -1), (-1, 0), (-2, 0)]),
                Polygon([(-1, -1), (0, -1), (0, 0), (-1, 0)]),
                Polygon([(0, -1), (1, -1), (1, 0), (0, 0)]),
            ],
        }
        gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")

        # Create a map
        geo_map = GeoMap(
            data=gdf,
            projection="mercator",
            color_by="value",
            color_scheme="viridis",
            fill_opacity=0.8,
            stroke_color=WHITE,
            stroke_width=2,
        )

        # Add title
        title = Text("GeoManim Test", font_size=48)
        title.to_edge(UP)

        # Animate
        self.play(Write(title))
        self.play(Create(geo_map), run_time=2)
        self.wait()

        # Scale animation
        self.play(geo_map.animate.scale(1.5), run_time=1)
        self.wait()


class PointTest(Scene):
    """Test point plotting."""

    def construct(self):
        # Create base geometric data
        data = {
            "name": ["Base"],
            "geometry": [
                Polygon([(-3, -2), (3, -2), (3, 2), (-3, 2)]),
            ],
        }
        gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")

        # Create map
        geo_map = GeoMap(
            data=gdf,
            projection="equirectangular",
            fill_color=BLUE_E,
            fill_opacity=0.3,
        )

        # Plot some points
        points = [
            (0, 0),    # Center
            (30, 45),  # Upper right
            (-30, -45), # Lower left
            (60, 20),  # Right
        ]

        points_group = geo_map.plot_points(
            points,
            color=YELLOW,
            radius=0.1,
        )

        # Animate
        self.play(FadeIn(geo_map))
        self.play(Create(points_group), run_time=2)
        self.wait(2)
