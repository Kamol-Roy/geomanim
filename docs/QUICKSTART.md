# GeoManim Quick Start Guide

Welcome to GeoManim! This guide will help you create your first animated geospatial visualization.

## Installation

```bash
pip install geomanim
```

## Your First Map

Create a file called `my_first_map.py`:

```python
from manim import *
from geomanim import GeoMap, get_world_boundaries

class MyFirstMap(Scene):
    def construct(self):
        # Load world data
        world = get_world_boundaries()

        # Create the map
        world_map = GeoMap(
            data=world,
            projection="mercator",
            fill_color=BLUE_D,
            fill_opacity=0.7,
            stroke_color=WHITE,
            stroke_width=1,
        )

        # Animate it!
        self.play(Create(world_map), run_time=3)
        self.wait(2)
```

Run it:

```bash
manim my_first_map.py MyFirstMap -pql
```

This will:
- `-p` Preview the animation when done
- `-q` Set quality
- `-l` Low resolution (fast for development)

## Common Tasks

### 1. Plot Cities on a Map

```python
from manim import *
from geomanim import GeoMap, get_world_boundaries

class CitiesMap(Scene):
    def construct(self):
        world = get_world_boundaries()
        world_map = GeoMap(data=world)

        # Define cities (latitude, longitude)
        cities = [
            (40.7128, -74.0060),  # New York
            (51.5074, -0.1278),   # London
            (35.6762, 139.6503),  # Tokyo
        ]

        # Plot them
        city_dots = world_map.plot_points(cities, color=RED, radius=0.08)

        self.play(Create(world_map))
        self.play(FadeIn(city_dots))
        self.wait()
```

### 2. Create a Choropleth Map

```python
from manim import *
from geomanim import GeoMap, get_world_boundaries

class ChoroplethMap(Scene):
    def construct(self):
        world = get_world_boundaries()

        # Color countries by population
        world_map = GeoMap(
            data=world,
            color_by="pop_est",
            color_scheme="viridis",
            fill_opacity=0.8,
        )

        self.play(FadeIn(world_map), run_time=3)
        self.wait()
```

### 3. Animate a Flight Path

```python
from manim import *
from geomanim import GeoMap, get_world_boundaries

class FlightPath(Scene):
    def construct(self):
        world = get_world_boundaries()
        world_map = GeoMap(data=world, fill_opacity=0.5)

        # Create route: New York → London
        route = [
            (40.7128, -74.0060),  # New York
            (51.5074, -0.1278),   # London
        ]

        path = world_map.plot_path(route, color=YELLOW, stroke_width=3)

        self.play(Create(world_map))
        self.play(Create(path), run_time=2)
        self.wait()
```

### 4. Use Different Projections

```python
from manim import *
from geomanim import GeoMap, get_world_boundaries

class Projections(Scene):
    def construct(self):
        world = get_world_boundaries()

        # Try different projections
        mercator = GeoMap(data=world, projection="mercator")
        robinson = GeoMap(data=world, projection="robinson")
        equirect = GeoMap(data=world, projection="equirectangular")

        self.play(FadeIn(mercator))
        self.wait()

        self.play(Transform(mercator, robinson))
        self.wait()

        self.play(Transform(mercator, equirect))
        self.wait()
```

## Loading Your Own Data

### From GeoJSON

```python
from geomanim import GeoMap, load_geojson

# Load your GeoJSON file
data = load_geojson("my_data.geojson")

# Create map
my_map = GeoMap(data=data)
```

### From CSV

```python
from geomanim import GeoMap, load_csv

# Load CSV with latitude/longitude columns
cities = load_csv(
    "cities.csv",
    lat_col="latitude",
    lon_col="longitude"
)

# Plot the points
world = get_world_boundaries()
world_map = GeoMap(data=world)
points = world_map.plot_points(cities)
```

### From Shapefile

```python
from geomanim import load_shapefile

data = load_shapefile("my_data.shp")
my_map = GeoMap(data=data)
```

## Customization

### Colors

```python
# Custom fill color
world_map = GeoMap(
    data=world,
    fill_color="#3498db",
    fill_opacity=0.6,
)

# Custom stroke
world_map = GeoMap(
    data=world,
    stroke_color="#e74c3c",
    stroke_width=2,
)
```

### Size

```python
# Custom map size
world_map = GeoMap(
    data=world,
    width=10,
    height=6,
)
```

### Color Schemes

Available color schemes:
- `blues`, `reds`, `greens`, `purples`, `oranges`
- `viridis`, `plasma`
- `warm`, `cool`, `diverging`

```python
world_map = GeoMap(
    data=world,
    color_by="gdp_md_est",
    color_scheme="plasma",
)
```

## Quality Settings

When rendering, use these quality flags:

- **Development** (fast): `-ql` (low quality)
- **Preview**: `-qm` (medium quality)
- **Production**: `-qh` (high quality)

```bash
# Low quality, fast preview
manim my_map.py MyMap -pql

# High quality, final render
manim my_map.py MyMap -pqh
```

## Next Steps

1. Check out the [examples directory](../examples/) for more complex examples
2. Read the full [API documentation](../README.md)
3. Join the community and share your visualizations!

## Tips

- Start with low quality (`-ql`) for fast iterations
- Use descriptive scene names
- Comment your code, especially coordinate data
- Save animations with `-p` flag to preview automatically
- Use `-s` to save just the last frame as an image

## Common Issues

### Import Error

If you get `ModuleNotFoundError: No module named 'geomanim'`:
- Ensure geomanim is installed: `pip install geomanim`
- Activate your virtual environment if using one

### Manim Not Found

Install Manim:
```bash
pip install manim
```

### Empty Map

If your map appears empty:
- Check that data is loaded correctly
- Verify projection coordinates
- Ensure geometry column exists in your data

## Getting Help

- Check the [examples](../examples/)
- Read the [README](../README.md)
- Open an issue on GitHub

Happy mapping!
