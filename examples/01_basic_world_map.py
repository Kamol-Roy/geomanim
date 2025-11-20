"""
Example 1: Basic World Map

This example shows how to create a simple world map with geomanim.
It loads world country boundaries and renders them with a smooth animation.

Usage:
    manim examples/01_basic_world_map.py BasicWorldMap -pql
"""

from manim import *
from geomanim import GeoMap, get_world_boundaries


class BasicWorldMap(Scene):
    """Create a basic animated world map."""

    def construct(self):
        # Load world boundaries
        world = get_world_boundaries()

        # Create a map with Mercator projection
        world_map = GeoMap(
            data=world,
            projection="mercator",
            fill_color=BLUE_D,
            fill_opacity=0.7,
            stroke_color=WHITE,
            stroke_width=1,
        )

        # Add title
        title = Text("World Map", font_size=48)
        title.to_edge(UP)

        # Animate
        self.play(Write(title))
        self.play(Create(world_map), run_time=3)
        self.wait(2)

        # Zoom in slightly
        self.play(world_map.animate.scale(1.2), run_time=2)
        self.wait()


class WorldMapProjections(Scene):
    """Compare different map projections."""

    def construct(self):
        # Load world data
        world = get_world_boundaries()

        # Create maps with different projections
        mercator_map = GeoMap(
            data=world,
            projection="mercator",
            width=6,
            height=4,
            fill_color=BLUE_D,
            fill_opacity=0.7,
        )

        robinson_map = GeoMap(
            data=world,
            projection="robinson",
            width=6,
            height=4,
            fill_color=GREEN_D,
            fill_opacity=0.7,
        )

        equirect_map = GeoMap(
            data=world,
            projection="equirectangular",
            width=6,
            height=4,
            fill_color=PURPLE_D,
            fill_opacity=0.7,
        )

        # Position maps
        mercator_map.shift(UP * 2)
        equirect_map.shift(DOWN * 2)

        # Add labels
        merc_label = Text("Mercator", font_size=24).next_to(mercator_map, UP)
        rob_label = Text("Robinson", font_size=24).next_to(robinson_map, UP)
        equi_label = Text("Equirectangular", font_size=24).next_to(
            equirect_map, UP
        )

        # Animate - show projections one by one
        self.play(
            FadeIn(mercator_map),
            Write(merc_label),
        )
        self.wait()

        self.play(
            Transform(mercator_map, robinson_map),
            Transform(merc_label, rob_label),
        )
        self.wait()

        self.play(
            Transform(mercator_map, equirect_map),
            Transform(merc_label, equi_label),
        )
        self.wait(2)
