"""
Example 2: Plotting Cities on a Map

This example demonstrates how to plot points (cities) on a map.

Usage:
    manim examples/02_plot_cities.py PlotCities -pql
"""

from manim import *
from geomanim import GeoMap, get_world_boundaries
import numpy as np


class PlotCities(Scene):
    """Plot major world cities on a map."""

    def construct(self):
        # Load world map
        world = get_world_boundaries()
        world_map = GeoMap(
            data=world,
            projection="mercator",
            fill_color=BLUE_E,
            fill_opacity=0.5,
            stroke_color=BLUE_B,
            stroke_width=0.5,
        )

        # Major cities (lat, lon)
        cities = [
            (40.7128, -74.0060),  # New York
            (51.5074, -0.1278),   # London
            (35.6762, 139.6503),  # Tokyo
            (-33.8688, 151.2093), # Sydney
            (19.4326, -99.1332),  # Mexico City
            (55.7558, 37.6173),   # Moscow
            (28.6139, 77.2090),   # Delhi
            (-23.5505, -46.6333), # São Paulo
            (1.3521, 103.8198),   # Singapore
            (30.0444, 31.2357),   # Cairo
        ]

        city_names = [
            "New York", "London", "Tokyo", "Sydney", "Mexico City",
            "Moscow", "Delhi", "São Paulo", "Singapore", "Cairo"
        ]

        # Add title
        title = Text("Major World Cities", font_size=40)
        title.to_edge(UP)

        # Create map
        self.play(Write(title))
        self.play(Create(world_map), run_time=2)
        self.wait()

        # Plot cities
        city_dots = world_map.plot_points(
            cities,
            color=YELLOW,
            radius=0.08,
        )

        # Animate cities appearing one by one
        for dot, name in zip(city_dots, city_names):
            label = Text(name, font_size=16, color=YELLOW)
            label.next_to(dot, UP, buff=0.1)

            self.play(
                GrowFromCenter(dot),
                FadeIn(label),
                run_time=0.3,
            )
            self.wait(0.1)
            self.play(FadeOut(label), run_time=0.2)

        self.wait(2)


class AnimatedCityGrowth(Scene):
    """Show city population growth animation."""

    def construct(self):
        # Load world map
        world = get_world_boundaries()
        world_map = GeoMap(
            data=world,
            projection="equirectangular",
            fill_color=GREY,
            fill_opacity=0.3,
            stroke_color=GREY_B,
            stroke_width=0.5,
        )

        # Cities with "population" (for size)
        cities = [
            (40.7128, -74.0060, 8.3),  # New York
            (51.5074, -0.1278, 9.0),   # London
            (35.6762, 139.6503, 37.4), # Tokyo
            (19.4326, -99.1332, 21.6), # Mexico City
            (28.6139, 77.2090, 28.5),  # Delhi
        ]

        # Title
        title = Text("City Populations", font_size=40)
        title.to_edge(UP)

        self.play(Write(title), FadeIn(world_map))
        self.wait()

        # Plot cities with sizes based on population
        max_pop = max(c[2] for c in cities)

        for lat, lon, pop in cities:
            # Radius proportional to population
            radius = 0.05 + (pop / max_pop) * 0.15

            city_dot = world_map.plot_points(
                [(lat, lon)],
                color=interpolate_color(YELLOW, RED, pop / max_pop),
                radius=radius,
            )

            self.play(GrowFromCenter(city_dot), run_time=0.5)

        self.wait(2)
