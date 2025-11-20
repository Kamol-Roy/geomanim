"""
Example 6: Custom Styling and Themes

This example demonstrates different styling options and visual themes
for geospatial visualizations.

Usage:
    manim examples/06_custom_styling.py CustomStyling -pql
"""

from manim import *
from geomanim import GeoMap, get_world_boundaries


class CustomStyling(Scene):
    """Show different styling options for maps."""

    def construct(self):
        # Load world data
        world = get_world_boundaries()

        # Style 1: Minimalist
        minimalist_map = GeoMap(
            data=world,
            projection="robinson",
            width=6,
            height=4,
            fill_color=WHITE,
            fill_opacity=0.2,
            stroke_color=BLACK,
            stroke_width=0.5,
        )

        title1 = Text("Minimalist Style", font_size=32)
        title1.next_to(minimalist_map, UP)

        self.play(Write(title1), FadeIn(minimalist_map))
        self.wait(1.5)

        # Style 2: Bold and Colorful
        colorful_map = GeoMap(
            data=world,
            projection="robinson",
            width=6,
            height=4,
            fill_color=BLUE,
            fill_opacity=0.9,
            stroke_color=YELLOW,
            stroke_width=3,
        )

        title2 = Text("Bold & Colorful", font_size=32)
        title2.next_to(colorful_map, UP)

        self.play(
            Transform(minimalist_map, colorful_map),
            Transform(title1, title2),
        )
        self.wait(1.5)

        # Style 3: Dark Theme
        dark_map = GeoMap(
            data=world,
            projection="robinson",
            width=6,
            height=4,
            fill_color="#2ecc71",
            fill_opacity=0.7,
            stroke_color="#27ae60",
            stroke_width=1,
        )

        title3 = Text("Dark Theme", font_size=32, color="#2ecc71")
        title3.next_to(dark_map, UP)

        self.camera.background_color = "#1a1a1a"

        self.play(
            Transform(minimalist_map, dark_map),
            Transform(title1, title3),
        )
        self.wait(2)


class GradientMap(Scene):
    """Create a map with gradient coloring by continent."""

    def construct(self):
        # Load world data
        world = get_world_boundaries()

        # Define colors for each continent
        continent_colors = {
            "Africa": RED,
            "Asia": BLUE,
            "Europe": GREEN,
            "North America": YELLOW,
            "South America": ORANGE,
            "Oceania": PURPLE,
            "Antarctica": GREY,
        }

        # Title
        title = Text("Continents", font_size=40)
        title.to_edge(UP)
        self.play(Write(title))

        # Create map for each continent
        for continent, color in continent_colors.items():
            continent_data = world[world["continent"] == continent]

            if not continent_data.empty:
                continent_map = GeoMap(
                    data=continent_data,
                    projection="robinson",
                    fill_color=color,
                    fill_opacity=0.7,
                    stroke_color=WHITE,
                    stroke_width=1,
                )

                # Label
                label = Text(continent, font_size=24, color=color)
                label.to_edge(DOWN)

                self.play(
                    FadeIn(continent_map),
                    Write(label),
                    run_time=0.8,
                )
                self.wait(0.3)
                self.play(FadeOut(label), run_time=0.2)

        self.wait(2)


class AnimatedColorScheme(Scene):
    """Animate between different color schemes."""

    def construct(self):
        # Load world data
        world = get_world_boundaries()

        # Title
        title = Text("Color Schemes", font_size=40)
        title.to_edge(UP)
        self.play(Write(title))

        # Color schemes to demonstrate
        schemes = ["blues", "reds", "greens", "plasma", "viridis"]

        for i, scheme in enumerate(schemes):
            world_map = GeoMap(
                data=world,
                projection="robinson",
                color_by="pop_est",
                color_scheme=scheme,
                fill_opacity=0.8,
                stroke_color=WHITE,
                stroke_width=0.5,
            )

            scheme_label = Text(scheme.capitalize(), font_size=28)
            scheme_label.to_edge(DOWN)

            if i == 0:
                self.play(
                    FadeIn(world_map),
                    Write(scheme_label),
                    run_time=1.5,
                )
            else:
                self.play(
                    FadeOut(prev_map),
                    FadeIn(world_map),
                    Transform(prev_label, scheme_label),
                    run_time=1.5,
                )

            prev_map = world_map
            prev_label = scheme_label
            self.wait(1)

        self.wait(2)


class StrokeVariations(Scene):
    """Demonstrate different stroke styles."""

    def construct(self):
        # Load world data
        world = get_world_boundaries()

        # Title
        title = Text("Stroke Variations", font_size=40)
        title.to_edge(UP)
        self.play(Write(title))

        # Variation 1: Thin strokes
        thin_map = GeoMap(
            data=world,
            projection="mercator",
            width=6,
            height=4,
            fill_color=BLUE_D,
            fill_opacity=0.6,
            stroke_color=WHITE,
            stroke_width=0.2,
        )

        label1 = Text("Thin Strokes (0.2)", font_size=24)
        label1.to_edge(DOWN)

        self.play(FadeIn(thin_map), Write(label1))
        self.wait(1.5)

        # Variation 2: Medium strokes
        medium_map = GeoMap(
            data=world,
            projection="mercator",
            width=6,
            height=4,
            fill_color=BLUE_D,
            fill_opacity=0.6,
            stroke_color=YELLOW,
            stroke_width=1.5,
        )

        label2 = Text("Medium Strokes (1.5)", font_size=24)
        label2.to_edge(DOWN)

        self.play(
            Transform(thin_map, medium_map),
            Transform(label1, label2),
        )
        self.wait(1.5)

        # Variation 3: Thick strokes
        thick_map = GeoMap(
            data=world,
            projection="mercator",
            width=6,
            height=4,
            fill_color=BLUE_D,
            fill_opacity=0.6,
            stroke_color=RED,
            stroke_width=3,
        )

        label3 = Text("Thick Strokes (3)", font_size=24)
        label3.to_edge(DOWN)

        self.play(
            Transform(thin_map, thick_map),
            Transform(label1, label3),
        )
        self.wait(2)
