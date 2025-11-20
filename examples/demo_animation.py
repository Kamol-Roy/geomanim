"""
Demo Animation - Shows GeoManim capabilities with clear visuals

Usage:
    manim examples/demo_animation.py GeoDemo -pqh
"""

from manim import *
import geopandas as gpd
from shapely.geometry import Polygon, Point
from geomanim import GeoMap


class GeoDemo(Scene):
    """Impressive demo of GeoManim features."""

    def construct(self):
        # Title
        title = Text("GeoManim", font_size=72, gradient=(BLUE, GREEN))
        subtitle = Text(
            "Geospatial Animation with Manim", font_size=32, color=GREY
        )
        subtitle.next_to(title, DOWN)

        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(subtitle), run_time=1)
        self.wait()
        self.play(FadeOut(title), FadeOut(subtitle))

        # Create a mock world map with continents
        continents = {
            "name": [
                "North America",
                "South America",
                "Europe",
                "Africa",
                "Asia",
                "Australia",
            ],
            "population": [579, 422, 747, 1340, 4560, 42],
            "geometry": [
                # North America (upper left)
                Polygon([(-120, 30), (-80, 30), (-80, 70), (-120, 70)]),
                # South America (lower left)
                Polygon([(-80, -30), (-40, -30), (-40, 10), (-80, 10)]),
                # Europe (upper middle)
                Polygon([(0, 40), (40, 40), (40, 70), (0, 70)]),
                # Africa (middle)
                Polygon([(10, -20), (40, -20), (40, 20), (10, 20)]),
                # Asia (upper right)
                Polygon([(50, 20), (140, 20), (140, 70), (50, 70)]),
                # Australia (lower right)
                Polygon([(110, -40), (150, -40), (150, -10), (110, -10)]),
            ],
        }

        gdf = gpd.GeoDataFrame(continents, crs="EPSG:4326")

        # Create choropleth map by population
        world_map = GeoMap(
            data=gdf,
            projection="equirectangular",
            color_by="population",
            color_scheme="viridis",
            fill_opacity=0.9,
            stroke_color=WHITE,
            stroke_width=2,
        )

        # Animate map creation
        map_title = Text("World Continents", font_size=40)
        map_title.to_edge(UP)

        self.play(Write(map_title))
        self.play(Create(world_map), run_time=3)
        self.wait()

        # Add cities as points
        cities = [
            (40.7, -74),    # New York
            (-23.5, -46.6), # Sao Paulo
            (51.5, -0.1),   # London
            (0, 18),        # Central Africa
            (35.7, 139.7),  # Tokyo
            (-33.9, 151.2), # Sydney
        ]

        cities_group = world_map.plot_points(
            cities, color=YELLOW, radius=0.15
        )

        city_label = Text("Major Cities", font_size=32, color=YELLOW)
        city_label.to_edge(DOWN)

        self.play(FadeIn(city_label))
        self.play(Create(cities_group), run_time=2)
        self.wait()

        # Draw a route
        route = [(40.7, -74), (51.5, -0.1), (35.7, 139.7)]  # NY → London → Tokyo
        path = world_map.plot_path(route, color=RED, stroke_width=4)

        route_label = Text("Flight Route", font_size=32, color=RED)
        route_label.to_edge(DOWN)

        self.play(Transform(city_label, route_label))
        self.play(Create(path), run_time=3)
        self.wait()

        # Zoom in
        self.play(
            world_map.animate.scale(1.5),
            cities_group.animate.scale(1.5),
            path.animate.scale(1.5),
            run_time=2,
        )
        self.wait()

        # Final message
        final_msg = Text(
            "Built with GeoManim", font_size=40, color=BLUE, weight=BOLD
        )
        final_msg.to_edge(DOWN)

        self.play(
            FadeOut(map_title),
            FadeOut(city_label),
            FadeIn(final_msg),
        )
        self.wait(2)


class ChoroplethDemo(Scene):
    """Demo of choropleth visualization."""

    def construct(self):
        # Create regions with different values
        regions = {
            "name": ["Region 1", "Region 2", "Region 3", "Region 4", "Region 5"],
            "value": [10, 50, 30, 80, 20],
            "geometry": [
                Polygon([(-2, 1), (-1, 1), (-1, 2), (-2, 2)]),
                Polygon([(-1, 1), (0, 1), (0, 2), (-1, 2)]),
                Polygon([(0, 1), (1, 1), (1, 2), (0, 2)]),
                Polygon([(-1, 0), (0, 0), (0, 1), (-1, 1)]),
                Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
            ],
        }

        gdf = gpd.GeoDataFrame(regions, crs="EPSG:4326")

        title = Text("Choropleth Map", font_size=48)
        title.to_edge(UP)

        # Create map colored by value
        geo_map = GeoMap(
            data=gdf,
            projection="mercator",
            color_by="value",
            color_scheme="plasma",
            fill_opacity=0.85,
            stroke_color=WHITE,
            stroke_width=3,
        )

        self.play(Write(title))
        self.play(Create(geo_map), run_time=2)
        self.wait()

        # Rotate through color schemes
        schemes = ["blues", "reds", "viridis"]
        for scheme in schemes:
            new_map = GeoMap(
                data=gdf,
                projection="mercator",
                color_by="value",
                color_scheme=scheme,
                fill_opacity=0.85,
                stroke_color=WHITE,
                stroke_width=3,
            )

            scheme_text = Text(f"Scheme: {scheme}", font_size=28)
            scheme_text.to_edge(DOWN)

            self.play(Transform(geo_map, new_map), FadeIn(scheme_text))
            self.wait(1.5)
            self.play(FadeOut(scheme_text))

        self.wait(2)
