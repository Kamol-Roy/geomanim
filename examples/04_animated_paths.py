"""
Example 4: Animated Flight Paths

This example shows how to animate paths on a map, such as flight routes,
migration patterns, or trade routes.

Usage:
    manim examples/04_animated_paths.py FlightPaths -pql
"""

from manim import *
from geomanim import GeoMap, get_world_boundaries


class FlightPaths(Scene):
    """Animate flight paths between major cities."""

    def construct(self):
        # Load world map
        world = get_world_boundaries()
        world_map = GeoMap(
            data=world,
            projection="mercator",
            fill_color=BLUE_E,
            fill_opacity=0.4,
            stroke_color=BLUE_D,
            stroke_width=0.5,
        )

        # Title
        title = Text("Global Flight Routes", font_size=40)
        title.to_edge(UP)

        # Cities (lat, lon)
        cities = {
            "New York": (40.7128, -74.0060),
            "London": (51.5074, -0.1278),
            "Tokyo": (35.6762, 139.6503),
            "Sydney": (-33.8688, 151.2093),
            "Dubai": (25.2048, 55.2708),
        }

        # Flight routes
        routes = [
            ("New York", "London"),
            ("London", "Dubai"),
            ("Dubai", "Tokyo"),
            ("Tokyo", "Sydney"),
            ("Sydney", "Los Angeles"),
        ]

        self.play(Write(title), FadeIn(world_map))
        self.wait()

        # Plot cities
        city_coords = list(cities.values())
        city_dots = world_map.plot_points(
            city_coords,
            color=YELLOW,
            radius=0.06,
        )

        self.play(FadeIn(city_dots), run_time=1)
        self.wait()

        # Animate flight paths
        for start_city, end_city in routes:
            if start_city in cities and end_city in cities:
                start_coord = cities[start_city]
                end_coord = cities.get(end_city, cities["New York"])

                # Create path
                path = world_map.plot_path(
                    [start_coord, end_coord],
                    color=RED,
                    stroke_width=2,
                )

                # Animate path being drawn
                self.play(Create(path), run_time=1.5)
                self.wait(0.3)

        self.wait(2)


class MigrationFlow(Scene):
    """Show migration or flow patterns."""

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

        # Title
        title = Text("Global Migration Patterns", font_size=40)
        title.to_edge(UP)

        self.play(Write(title), FadeIn(world_map))
        self.wait()

        # Define migration routes with multiple waypoints for curved paths
        migrations = [
            # Africa to Europe
            [(10, 20), (25, 20), (40, 10)],
            # Asia to North America
            [(35, 100), (45, 140), (40, -120)],
            # South America to North America
            [(-20, -60), (0, -80), (30, -100)],
            # Middle East to Europe
            [(30, 50), (40, 30), (50, 10)],
        ]

        colors = [YELLOW, BLUE, GREEN, RED]

        # Animate each migration route
        for migration, color in zip(migrations, colors):
            path = world_map.plot_path(
                migration,
                color=color,
                stroke_width=3,
            )

            # Add arrow at the end
            arrow = Arrow(
                start=path.get_start(),
                end=path.get_end(),
                color=color,
                buff=0,
                stroke_width=3,
            )

            self.play(Create(path), run_time=2)
            self.wait(0.5)

        self.wait(2)


class TradeRoutes(Scene):
    """Visualize historical trade routes."""

    def construct(self):
        # Load world map
        world = get_world_boundaries()
        world_map = GeoMap(
            data=world,
            projection="robinson",
            fill_color="#2c3e50",
            fill_opacity=0.8,
            stroke_color="#34495e",
            stroke_width=1,
        )

        # Title
        title = Text("Silk Road Trade Route", font_size=40, color=GOLD)
        title.to_edge(UP)

        self.play(Write(title), FadeIn(world_map))
        self.wait()

        # Silk Road route (simplified)
        silk_road = [
            (34.05, 108.93),  # Xi'an, China
            (37.87, 58.38),   # Merv, Turkmenistan
            (41.32, 69.25),   # Samarkand, Uzbekistan
            (35.69, 51.42),   # Tehran, Iran
            (33.31, 44.36),   # Baghdad, Iraq
            (41.01, 28.98),   # Istanbul, Turkey
            (41.90, 12.50),   # Rome, Italy
        ]

        # Create the route
        route = world_map.plot_path(
            silk_road,
            color=GOLD,
            stroke_width=4,
        )

        # Mark key cities
        cities = world_map.plot_points(
            silk_road,
            color=GOLD,
            radius=0.08,
        )

        # Animate the trade route
        self.play(Create(route), run_time=4)
        self.play(FadeIn(cities), run_time=1)
        self.wait()

        # Add a traveler moving along the route
        traveler = Dot(color=RED, radius=0.08)
        traveler.move_to(route.get_start())

        self.play(
            MoveAlongPath(traveler, route),
            run_time=5,
            rate_func=smooth,
        )
        self.wait(2)
