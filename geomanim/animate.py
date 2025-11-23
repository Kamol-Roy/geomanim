"""
Simple one-line API for creating geospatial animations.

This module provides an easy-to-use function for creating animated maps
without writing Manim scenes manually.
"""

from pathlib import Path
from typing import Optional
from manim import *
from geomanim.data import load_data
from geomanim.map2d import GeoMap
import os
import sys


def animate(
    file_path: str,
    column: Optional[str] = None,
    output: str = "output.mp4",
    projection: str = "mercator",
    color_scheme: str = "viridis",
    quality: str = "medium",
    show_preview: bool = True,
    background: str = "black",
    basemap: Optional[str] = None,
    order: Optional[str] = None,
    reverse_order: bool = False,
    format: str = "mp4",
    stroke_width: float = 2,
) -> str:
    """
    Create an animated geospatial visualization with a single function call.

    Args:
        file_path: Path to geospatial data file (GeoJSON, Shapefile, CSV, etc.)
        column: Optional column name for coloring. Supports both:
            - Numerical columns: Creates choropleth with continuous color gradient
            - Categorical columns: Auto-detects strings/categories, shows top 5 + "Other"
        output: Path to output file (default: "output.mp4")
        projection: Map projection ('mercator', 'robinson', 'equirectangular')
        color_scheme: Color scheme ('viridis', 'blues', 'reds', 'plasma', etc.)
        quality: Output quality ('low', 'medium', 'high')
        show_preview: Whether to show preview after rendering (default: True)
        background: Background color ('black' or 'white', default: 'black')
        basemap: Built-in basemap ('light', 'dark', 'neutral', or None)
        order: Column name to determine animation order (features animate sequentially by this value)
               Use with groupby().cumcount() for grouped sequential animation
        reverse_order: If True, animate in descending order; if False, ascending (default: False)
        format: Output format ('mp4' or 'gif', default: 'mp4')
        stroke_width: Width of boundary/line strokes (default: 2, increase for roads/lines)

    Returns:
        Path to the generated file

    Examples:
        # Numerical choropleth
        >>> from geomanim import animate
        >>> animate("countries.geojson", column="population")

        # Categorical coloring (auto-detects string columns)
        >>> animate("roads.geojson", column="road_type", stroke_width=3)

        # Ordered animation by value
        >>> animate("world.geojson", column="gdp", order="gdp", reverse_order=True)

        # Categorical with ordered animation using groupby cumcount
        >>> import geopandas as gpd
        >>> roads = gpd.read_file("roads.geojson")
        >>> roads['order'] = roads.groupby('road_name').cumcount()
        >>> roads.to_file("roads_ordered.geojson")
        >>> animate("roads_ordered.geojson", column="road_name", order="order", stroke_width=4)

        # With basemap
        >>> animate("cities.csv", basemap="light", column="population", background="white")

        # GIF output
        >>> animate("world.geojson", output="world.gif", format="gif")
    """
    # Validate inputs
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Load the data
    print(f"Loading data from {file_path}...")
    data = load_data(file_path)

    if data.empty:
        raise ValueError("No data loaded from file")

    print(f"✓ Loaded {len(data)} features")

    # Determine colors based on background
    if background.lower() == "white":
        bg_color = WHITE
        text_color = BLACK
        stroke_color = BLACK
        default_fill = BLUE_C
    else:
        bg_color = BLACK
        text_color = WHITE
        stroke_color = WHITE
        default_fill = BLUE_D

    # Create the Manim scene programmatically
    class GeoAnimScene(Scene):
        def construct(self):
            # Set background color
            self.camera.background_color = bg_color

            # Create title
            title_text = file_path.stem.replace("_", " ").title()
            title = Text(title_text, font_size=42, color=text_color)
            title.to_edge(UP)

            # Create the map
            geo_map = GeoMap(
                data=data,
                projection=projection,
                color_by=column,
                color_scheme=color_scheme if column else None,
                fill_color=default_fill if not column else None,
                fill_opacity=0.8,
                stroke_color=stroke_color,
                stroke_width=1,
            )

            # Animation sequence
            self.play(Write(title), run_time=1)
            self.play(Create(geo_map), run_time=3)
            self.wait()

            # If choropleth, add a colorbar
            if column:
                colorbar = geo_map.create_colorbar(text_color=text_color)
                self.play(FadeIn(colorbar), run_time=1)
                self.wait()

            # Zoom in slightly
            self.play(geo_map.animate.scale(1.2), run_time=2)
            self.wait(2)

    # Set quality parameters
    quality_map = {
        "low": ("-ql", "480p15"),
        "medium": ("-qm", "720p30"),
        "high": ("-qh", "1080p60"),
    }

    if quality not in quality_map:
        quality = "medium"

    quality_flag, resolution = quality_map[quality]

    # Prepare output path
    output_path = Path(output).resolve()
    output_dir = output_path.parent
    output_name = output_path.stem

    # Create temporary scene file
    import tempfile
    import textwrap

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as f:
        scene_code = textwrap.dedent(
            f"""
            from manim import *
            from geomanim import GeoMap
            from geomanim.data import load_data

            class GeoAnimScene(Scene):
                def construct(self):
                    # Determine colors based on background
                    background = "{background}"
                    if background.lower() == "white":
                        bg_color = WHITE
                        text_color = BLACK
                        stroke_color = BLACK
                        default_fill = BLUE_C
                    else:
                        bg_color = BLACK
                        text_color = WHITE
                        stroke_color = WHITE
                        default_fill = BLUE_D

                    # Set background color
                    self.camera.background_color = bg_color

                    # Load data
                    data = load_data(r"{file_path}")

                    # Create title
                    title_text = "{file_path.stem.replace('_', ' ').title()}"
                    title = Text(title_text, font_size=42, color=text_color)
                    title.to_edge(UP)

                    # Create the map
                    geo_map = GeoMap(
                        data=data,
                        projection="{projection}",
                        color_by={repr(column)},
                        color_scheme="{color_scheme}" if {repr(column)} else None,
                        fill_color=default_fill if not {repr(column)} else None,
                        fill_opacity=0.8,
                        stroke_color=stroke_color,
                        stroke_width={stroke_width},
                        basemap={repr(basemap)},
                        order={repr(order)},
                        reverse_order={reverse_order},
                    )

                    # Animation sequence
                    self.play(Write(title), run_time=1)

                    # Add basemap background if present (must be added before animating vector data)
                    if hasattr(geo_map, 'background_mobject') and geo_map.background_mobject:
                        self.add(geo_map.background_mobject)

                    # Use appropriate animation based on order parameter
                    if {repr(order)}:
                        # Ordered animation - features appear sequentially
                        self.play(geo_map.get_creation_animation(run_time=5, lag_ratio=0.08))
                    elif {repr(basemap)}:
                        # Basemap - use FadeIn
                        self.play(FadeIn(geo_map), run_time=2)
                    else:
                        # Standard - use Create
                        self.play(Create(geo_map), run_time=3)
                    self.wait()

                    # Add colorbar or legend based on data type
                    if {repr(column)}:
                        if geo_map.is_categorical:
                            # Create categorical legend
                            legend = VGroup()
                            for cat, color in geo_map.category_colors.items():
                                cat_label = Text(cat, font_size=20, color=color)
                                legend.add(cat_label)
                            legend.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
                            legend.to_corner(UR, buff=0.5)
                            self.play(FadeIn(legend), run_time=1)
                        else:
                            # Numerical - show colorbar
                            colorbar = geo_map.create_colorbar(text_color=text_color)
                            self.play(FadeIn(colorbar), run_time=1)
                        self.wait()

                    # Zoom in slightly (only if no basemap - zooming breaks basemap alignment)
                    if not {repr(basemap)}:
                        self.play(geo_map.animate.scale(1.2), run_time=2)
                    self.wait(2)
            """
        )
        f.write(scene_code)
        temp_scene_file = f.name

    try:
        # Run manim command
        print(f"Rendering animation...")
        print(f"Quality: {quality} ({resolution})")
        if column:
            print(f"Choropleth column: {column}")

        import subprocess
        import shutil

        # Find manim executable
        manim_path = shutil.which("manim")
        if not manim_path:
            # Try to use python -m manim
            manim_cmd = [sys.executable, "-m", "manim"]
        else:
            manim_cmd = [manim_path]

        cmd = manim_cmd + [
            temp_scene_file,
            "GeoAnimScene",
            quality_flag,
            "-o",
            output_name,
        ]

        # Add format flag for GIF
        if format.lower() == "gif":
            cmd.append("--format")
            cmd.append("gif")

        if show_preview:
            cmd.append("-p")

        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print("Error rendering animation:")
            print(result.stderr)
            raise RuntimeError(f"Manim rendering failed: {result.stderr}")

        # Find the generated file
        file_ext = "gif" if format.lower() == "gif" else "mp4"
        media_dir = Path("media/videos/").resolve()
        if media_dir.exists():
            for video_file in media_dir.rglob(f"{output_name}.{file_ext}"):
                # Copy to desired output location
                import shutil

                shutil.copy(video_file, output_path)
                print(f"\n✓ Animation saved to: {output_path}")
                return str(output_path)

        print(f"\n✓ Animation complete!")
        return output

    finally:
        # Cleanup temporary file
        try:
            os.unlink(temp_scene_file)
        except:
            pass


if __name__ == "__main__":
    # CLI interface
    import argparse

    parser = argparse.ArgumentParser(description="Animate geospatial data")
    parser.add_argument("file", help="Path to geospatial data file")
    parser.add_argument("-c", "--column", help="Column for choropleth coloring")
    parser.add_argument("-o", "--output", default="output.mp4", help="Output file")
    parser.add_argument(
        "-p",
        "--projection",
        default="mercator",
        choices=["mercator", "robinson", "equirectangular"],
    )
    parser.add_argument(
        "-s",
        "--color-scheme",
        default="viridis",
        help="Color scheme for choropleth",
    )
    parser.add_argument(
        "-q",
        "--quality",
        default="medium",
        choices=["low", "medium", "high"],
    )

    args = parser.parse_args()

    animate(
        args.file,
        column=args.column,
        output=args.output,
        projection=args.projection,
        color_scheme=args.color_scheme,
        quality=args.quality,
    )
