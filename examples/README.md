# GeoManim Examples

This directory contains example scripts demonstrating various features of GeoManim.

## Running Examples

To run any example, use the Manim command:

```bash
manim examples/01_basic_world_map.py BasicWorldMap -pql
```

### Quality Flags
- `-pql` - Preview quality, low resolution (fast)
- `-pqm` - Preview quality, medium resolution
- `-pqh` - Preview quality, high resolution (production)

### Other Useful Flags
- `-p` - Preview the animation when done
- `-s` - Save the last frame as an image
- `-a` - Render all scenes in the file

## Examples Overview

### 01_basic_world_map.py
**Scenes:**
- `BasicWorldMap` - Simple world map with Mercator projection
- `WorldMapProjections` - Compare different map projections

Demonstrates: Basic map creation, different projections, simple animations

### 02_plot_cities.py
**Scenes:**
- `PlotCities` - Plot major world cities on a map
- `AnimatedCityGrowth` - Show cities with sizes based on population

Demonstrates: Point plotting, animated markers, data visualization

### 03_choropleth_map.py
**Scenes:**
- `ChoroplethMap` - Color countries by population
- `AnimatedChoropleth` - Animated choropleth with GDP data
- `CompareRegions` - Side-by-side comparison of regions

Demonstrates: Choropleth maps, color schemes, data-driven coloring, legends

### 04_animated_paths.py
**Scenes:**
- `FlightPaths` - Animate flight routes between cities
- `MigrationFlow` - Show migration patterns
- `TradeRoutes` - Visualize the historic Silk Road

Demonstrates: Path animation, route visualization, animated movement

### 05_highlight_regions.py
**Scenes:**
- `HighlightCountries` - Highlight G7 countries
- `CompareCountries` - Compare sizes of different countries
- `AnimatedRegionGrowth` - Show EU expansion over time
- `ZoomToRegion` - Zoom into Southeast Asia

Demonstrates: Region highlighting, country filtering, zoom effects, historical visualization

### 06_custom_styling.py
**Scenes:**
- `CustomStyling` - Different visual styles for maps
- `GradientMap` - Color continents differently
- `AnimatedColorScheme` - Cycle through color schemes
- `StrokeVariations` - Different border stroke styles

Demonstrates: Custom colors, styling options, themes, visual customization

## Tips

1. **Start with low quality** (`-ql`) for faster previews while developing
2. **Use high quality** (`-qh`) only for final renders
3. **Multiple scenes**: Use `-a` to render all scenes in a file
4. **Save frames**: Use `-s` to save a single frame instead of animation

## Example Command Combinations

```bash
# Quick preview
manim examples/01_basic_world_map.py BasicWorldMap -pql

# High quality production render
manim examples/03_choropleth_map.py ChoroplethMap -pqh

# Save last frame as image
manim examples/02_plot_cities.py PlotCities -sqh

# Render all scenes in a file
manim examples/05_highlight_regions.py -pql -a
```

## Creating Your Own Examples

Feel free to use these examples as templates for your own geospatial visualizations!

Basic template:

```python
from manim import *
from geomanim import GeoMap, get_world_boundaries

class MyMapScene(Scene):
    def construct(self):
        # Load data
        world = get_world_boundaries()

        # Create map
        world_map = GeoMap(
            data=world,
            projection="mercator",
            fill_color=BLUE_D,
            fill_opacity=0.7,
        )

        # Animate
        self.play(Create(world_map))
        self.wait()
```

## Need Help?

- Check the [API documentation](../docs/)
- Read the main [README](../README.md)
- Open an issue on GitHub
