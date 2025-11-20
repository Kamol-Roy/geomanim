"""
Example 5: Highlighting Regions

This example shows how to highlight specific countries or regions on a map.

Usage:
    manim examples/05_highlight_regions.py HighlightCountries -pql
"""

from manim import *
from geomanim import GeoMap, get_world_boundaries


class HighlightCountries(Scene):
    """Highlight specific countries on the world map."""

    def construct(self):
        # Load world data
        world = get_world_boundaries()

        # Create base map (greyed out)
        base_map = GeoMap(
            data=world,
            projection="mercator",
            fill_color=GREY,
            fill_opacity=0.3,
            stroke_color=GREY_B,
            stroke_width=0.5,
        )

        # Title
        title = Text("G7 Countries", font_size=40)
        title.to_edge(UP)

        self.play(Write(title), FadeIn(base_map))
        self.wait()

        # G7 countries
        g7_countries = [
            "United States of America",
            "Canada",
            "United Kingdom",
            "France",
            "Germany",
            "Italy",
            "Japan",
        ]

        # Filter and create highlighted map
        g7_data = world[world["name"].isin(g7_countries)]

        # Highlight G7 countries one by one
        for idx, row in g7_data.iterrows():
            # Create map for single country
            country_map = GeoMap(
                data=g7_data[g7_data["name"] == row["name"]],
                projection="mercator",
                fill_color=YELLOW,
                fill_opacity=0.8,
                stroke_color=ORANGE,
                stroke_width=2,
            )

            # Label
            country_label = Text(row["name"], font_size=24, color=YELLOW)
            country_label.to_edge(DOWN)

            self.play(
                FadeIn(country_map),
                Write(country_label),
                run_time=0.8,
            )
            self.wait(0.3)
            self.play(FadeOut(country_label), run_time=0.3)

        self.wait(2)


class CompareCountries(Scene):
    """Compare the size and shape of different countries."""

    def construct(self):
        # Load world data
        world = get_world_boundaries()

        # Select countries to compare
        countries = ["Brazil", "Australia", "India"]
        colors = [GREEN, YELLOW, ORANGE]

        # Title
        title = Text("Comparing Country Sizes", font_size=40)
        title.to_edge(UP)
        self.play(Write(title))

        # Show all countries overlaid
        maps = []
        for country, color in zip(countries, colors):
            country_data = world[world["name"] == country]
            country_map = GeoMap(
                data=country_data,
                projection="mercator",
                width=8,
                height=6,
                fill_color=color,
                fill_opacity=0.5,
                stroke_color=color,
                stroke_width=2,
            )
            maps.append(country_map)

        # Show countries one by one
        for i, (country_map, country) in enumerate(zip(maps, countries)):
            label = Text(country, font_size=28, color=colors[i])
            label.to_edge(DOWN)

            self.play(FadeIn(country_map), Write(label))
            self.wait(0.5)
            self.play(FadeOut(label))

        self.wait(2)


class AnimatedRegionGrowth(Scene):
    """Show historical expansion of a region or empire."""

    def construct(self):
        # Load world data
        world = get_world_boundaries()

        # Base map
        world_map = GeoMap(
            data=world,
            projection="mercator",
            fill_color=GREY_E,
            fill_opacity=0.2,
            stroke_color=GREY_D,
            stroke_width=0.3,
        )

        # Title
        title = Text("European Union Expansion", font_size=36)
        title.to_edge(UP)

        self.play(Write(title), FadeIn(world_map))
        self.wait()

        # EU countries (simplified, not chronological)
        eu_waves = [
            # Founding members (1957)
            ["France", "Germany", "Italy", "Belgium", "Netherlands"],
            # 1973
            ["United Kingdom", "Ireland", "Denmark"],
            # 1981-1986
            ["Greece", "Spain", "Portugal"],
            # 1995
            ["Austria", "Sweden", "Finland"],
            # 2004 (partial)
            ["Poland", "Czech Rep.", "Hungary"],
        ]

        colors_gradient = [BLUE_E, BLUE_D, BLUE_C, BLUE_B, BLUE_A]

        year_labels = ["1957", "1973", "1986", "1995", "2004"]

        # Show expansion waves
        for wave, color, year in zip(eu_waves, colors_gradient, year_labels):
            # Filter countries in this wave
            wave_data = world[world["name"].isin(wave)]

            if not wave_data.empty:
                wave_map = GeoMap(
                    data=wave_data,
                    projection="mercator",
                    fill_color=color,
                    fill_opacity=0.8,
                    stroke_color=BLUE,
                    stroke_width=1.5,
                )

                year_label = Text(year, font_size=32, color=color)
                year_label.to_corner(DL)

                self.play(
                    FadeIn(wave_map),
                    Write(year_label),
                    run_time=1.5,
                )
                self.wait(0.8)
                self.play(FadeOut(year_label), run_time=0.3)

        self.wait(2)


class ZoomToRegion(Scene):
    """Demonstrate zooming into a specific region."""

    def construct(self):
        # Load world data
        world = get_world_boundaries()

        # Full world map
        world_map = GeoMap(
            data=world,
            projection="mercator",
            fill_color=BLUE_D,
            fill_opacity=0.6,
            stroke_color=WHITE,
            stroke_width=0.5,
        )

        title = Text("Zoom to Southeast Asia", font_size=40)
        title.to_edge(UP)

        self.play(Write(title), FadeIn(world_map))
        self.wait()

        # Highlight Southeast Asia
        se_asia_countries = [
            "Thailand",
            "Vietnam",
            "Malaysia",
            "Indonesia",
            "Philippines",
            "Singapore",
        ]

        se_asia_data = world[world["name"].isin(se_asia_countries)]

        se_asia_map = GeoMap(
            data=se_asia_data,
            projection="mercator",
            width=10,
            height=8,
            fill_color=YELLOW,
            fill_opacity=0.8,
            stroke_color=ORANGE,
            stroke_width=2,
        )

        # Zoom transition
        self.play(
            world_map.animate.set_opacity(0.2),
            run_time=1,
        )
        self.play(
            FadeIn(se_asia_map),
            run_time=2,
        )
        self.wait(2)
