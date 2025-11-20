"""Color schemes and utilities for geospatial visualizations."""

import numpy as np
from manim import *
from typing import List, Union


# Predefined color schemes for choropleth maps
COLOR_SCHEMES = {
    "blues": [BLUE_E, BLUE_D, BLUE_C, BLUE_B, BLUE_A],
    "reds": [RED_E, RED_D, RED_C, RED_B, RED_A],
    "greens": [GREEN_E, GREEN_D, GREEN_C, GREEN_B, GREEN_A],
    "purples": [PURPLE_E, PURPLE_D, PURPLE_C, PURPLE_B, PURPLE_A],
    "oranges": [ORANGE, "#FF8C00", "#FF6347", "#FF4500", "#DC143C"],
    "viridis": ["#440154", "#31688e", "#35b779", "#fde724"],
    "plasma": ["#0d0887", "#7e03a8", "#cc4778", "#f89540", "#f0f921"],
    "warm": [YELLOW_E, YELLOW_C, ORANGE, RED_C, RED_A],
    "cool": [BLUE_E, TEAL_E, GREEN_C, GREEN_A],
    "diverging": [BLUE_E, BLUE_C, WHITE, RED_C, RED_E],
}


def get_color_scheme(name: str) -> List[str]:
    """
    Get a predefined color scheme by name.

    Args:
        name: Name of the color scheme

    Returns:
        List of color hex codes

    Raises:
        ValueError: If color scheme name is not recognized
    """
    scheme = COLOR_SCHEMES.get(name.lower())
    if scheme is None:
        available = ", ".join(COLOR_SCHEMES.keys())
        raise ValueError(
            f"Unknown color scheme '{name}'. Available: {available}"
        )
    return scheme


def interpolate_color_range(
    value: float, min_val: float, max_val: float, colors: List[str]
) -> str:
    """
    Interpolate a color from a range based on a value.

    Args:
        value: The value to map to a color
        min_val: Minimum value in the range
        max_val: Maximum value in the range
        colors: List of colors to interpolate between

    Returns:
        Hex color code
    """
    if max_val == min_val:
        return colors[0]

    # Normalize value to [0, 1]
    normalized = (value - min_val) / (max_val - min_val)
    normalized = np.clip(normalized, 0, 1)

    # Find position in color list
    n_colors = len(colors)
    position = normalized * (n_colors - 1)
    idx = int(position)

    # If exactly at a color, return it
    if idx >= n_colors - 1:
        return colors[-1]

    # Interpolate between two colors
    t = position - idx
    color1 = ManimColor(colors[idx])
    color2 = ManimColor(colors[idx + 1])

    return interpolate_color(color1, color2, t)


def value_to_color(
    value: float,
    min_val: float,
    max_val: float,
    color_scheme: Union[str, List[str]] = "blues",
) -> str:
    """
    Map a data value to a color.

    Args:
        value: The value to map
        min_val: Minimum value in the dataset
        max_val: Maximum value in the dataset
        color_scheme: Name of color scheme or list of colors

    Returns:
        Hex color code
    """
    if isinstance(color_scheme, str):
        colors = get_color_scheme(color_scheme)
    else:
        colors = color_scheme

    return interpolate_color_range(value, min_val, max_val, colors)


def create_color_legend(
    min_val: float,
    max_val: float,
    color_scheme: Union[str, List[str]] = "blues",
    n_steps: int = 5,
) -> VGroup:
    """
    Create a color legend for a choropleth map.

    Args:
        min_val: Minimum value
        max_val: Maximum value
        color_scheme: Color scheme to use
        n_steps: Number of steps in the legend

    Returns:
        VGroup containing the color legend
    """
    if isinstance(color_scheme, str):
        colors = get_color_scheme(color_scheme)
    else:
        colors = color_scheme

    legend = VGroup()

    # Create color bars
    bar_height = 0.3
    bar_width = 1.5
    values = np.linspace(min_val, max_val, n_steps)

    for i, val in enumerate(values):
        color = value_to_color(val, min_val, max_val, colors)
        bar = Rectangle(
            height=bar_height,
            width=bar_width / n_steps,
            fill_color=color,
            fill_opacity=1,
            stroke_width=1,
        )
        bar.shift(RIGHT * (i - n_steps / 2 + 0.5) * bar_width / n_steps)

        # Add label
        label = Text(f"{val:.1f}", font_size=16)
        label.next_to(bar, DOWN, buff=0.1)

        legend.add(bar, label)

    return legend
