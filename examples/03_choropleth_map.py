"""
Example 3: Choropleth Map

This example shows how to create a choropleth map where regions are colored
based on data values (e.g., population, GDP, etc.).

Usage:
    manim examples/03_choropleth_map.py ChoroplethMap -pql
"""

from manim import *
from geomanim import GeoMap, get_world_boundaries, create_color_legend
import numpy as np


class ChoroplethMap(Scene):
    """Create a choropleth map colored by population."""

    def construct(self):
        # Load world data
        world = get_world_boundaries()

        # Create a choropleth map using population data
        world_map = GeoMap(
            data=world,
            projection="robinson",
            color_by="pop_est",  # Color by estimated population
            color_scheme="viridis",
            fill_opacity=0.8,
            stroke_color=WHITE,
            stroke_width=0.5,
        )

        # Add title
        title = Text("World Population by Country", font_size=40)
        title.to_edge(UP)

        # Create color legend
        min_pop = world["pop_est"].min()
        max_pop = world["pop_est"].max()

        legend = create_color_legend(
            min_pop,
            max_pop,
            color_scheme="viridis",
            n_steps=5,
        )
        legend.scale(0.5)
        legend.to_corner(DR)

        # Animate
        self.play(Write(title))
        self.play(FadeIn(world_map), run_time=3)
        self.wait()

        self.play(FadeIn(legend))
        self.wait(2)


class AnimatedChoropleth(Scene):
    """Animate a choropleth map with changing data."""

    def construct(self):
        # Load world data
        world = get_world_boundaries()

        # Title
        title = Text("GDP per Capita", font_size=40)
        title.to_edge(UP)

        # Create initial map
        world_map = GeoMap(
            data=world,
            projection="mercator",
            color_by="gdp_md_est",
            color_scheme="plasma",
            fill_opacity=0.8,
            stroke_color=GREY,
            stroke_width=0.5,
        )

        self.play(Write(title))
        self.play(Create(world_map), run_time=3)
        self.wait()

        # Highlight specific regions
        # Get data for a specific continent
        africa = world[world["continent"] == "Africa"]

        africa_map = GeoMap(
            data=africa,
            projection="mercator",
            fill_color=YELLOW,
            fill_opacity=0.9,
            stroke_color=ORANGE,
            stroke_width=2,
        )

        # Transition to highlight Africa
        new_title = Text("Focus: Africa", font_size=40)
        new_title.to_edge(UP)

        self.play(
            Transform(title, new_title),
            world_map.animate.set_opacity(0.3),
        )
        self.play(FadeIn(africa_map))
        self.wait(2)


class CompareRegions(Scene):
    """Compare different regions side by side."""

    def construct(self):
        # Load world data
        world = get_world_boundaries()

        # Filter regions
        europe = world[world["continent"] == "Europe"]
        asia = world[world["continent"] == "Asia"]

        # Create maps
        europe_map = GeoMap(
            data=europe,
            projection="mercator",
            width=6,
            height=4,
            color_by="pop_est",
            color_scheme="blues",
            fill_opacity=0.8,
        )

        asia_map = GeoMap(
            data=asia,
            projection="mercator",
            width=6,
            height=4,
            color_by="pop_est",
            color_scheme="reds",
            fill_opacity=0.8,
        )

        # Position maps
        europe_map.shift(LEFT * 3.5)
        asia_map.shift(RIGHT * 3.5)

        # Labels
        europe_label = Text("Europe", font_size=32).next_to(europe_map, UP)
        asia_label = Text("Asia", font_size=32).next_to(asia_map, UP)

        # Animate
        self.play(
            FadeIn(europe_map),
            Write(europe_label),
        )
        self.wait()

        self.play(
            FadeIn(asia_map),
            Write(asia_label),
        )
        self.wait(2)

        # Zoom in on both
        self.play(
            europe_map.animate.scale(1.3),
            asia_map.animate.scale(1.3),
        )
        self.wait(2)
