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
) -> str:
    """
    Create an animated geospatial visualization with a single function call.

    Args:
        file_path: Path to geospatial data file (GeoJSON, Shapefile, CSV, etc.)
        column: Optional column name for choropleth coloring
        output: Path to output MP4 file (default: "output.mp4")
        projection: Map projection ('mercator', 'robinson', 'equirectangular')
        color_scheme: Color scheme for choropleth ('viridis', 'blues', 'reds', etc.)
        quality: Output quality ('low', 'medium', 'high')
        show_preview: Whether to show preview after rendering (default: True)

    Returns:
        Path to the generated video file

    Examples:
        >>> from geomanim import animate
        >>> animate("countries.geojson", column="population")
        >>> animate("cities.csv", output="cities.mp4")
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

    # Create the Manim scene programmatically
    class GeoAnimScene(Scene):
        def construct(self):
            # Create title
            title_text = file_path.stem.replace("_", " ").title()
            title = Text(title_text, font_size=42)
            title.to_edge(UP)

            # Create the map
            geo_map = GeoMap(
                data=data,
                projection=projection,
                color_by=column,
                color_scheme=color_scheme if column else None,
                fill_color=BLUE_D if not column else None,
                fill_opacity=0.8,
                stroke_color=WHITE,
                stroke_width=1,
            )

            # Animation sequence
            self.play(Write(title), run_time=1)
            self.play(Create(geo_map), run_time=3)
            self.wait()

            # If choropleth, show a label
            if column:
                label = Text(f"Colored by: {column}", font_size=24, color=GREY)
                label.to_edge(DOWN)
                self.play(FadeIn(label))
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
                    # Load data
                    data = load_data(r"{file_path}")

                    # Create title
                    title_text = "{file_path.stem.replace('_', ' ').title()}"
                    title = Text(title_text, font_size=42)
                    title.to_edge(UP)

                    # Create the map
                    geo_map = GeoMap(
                        data=data,
                        projection="{projection}",
                        color_by={repr(column)},
                        color_scheme="{color_scheme}" if {repr(column)} else None,
                        fill_color=BLUE_D if not {repr(column)} else None,
                        fill_opacity=0.8,
                        stroke_color=WHITE,
                        stroke_width=1,
                    )

                    # Animation sequence
                    self.play(Write(title), run_time=1)
                    self.play(Create(geo_map), run_time=3)
                    self.wait()

                    # If choropleth, show a label
                    if {repr(column)}:
                        label = Text(f"Colored by: {repr(column)}", font_size=24, color=GREY)
                        label.to_edge(DOWN)
                        self.play(FadeIn(label))
                        self.wait()

                    # Zoom in slightly
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

        if show_preview:
            cmd.append("-p")

        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print("Error rendering animation:")
            print(result.stderr)
            raise RuntimeError(f"Manim rendering failed: {result.stderr}")

        # Find the generated file
        media_dir = Path("media/videos/tmpscene/").resolve()
        if media_dir.exists():
            for video_file in media_dir.rglob(f"{output_name}.mp4"):
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
