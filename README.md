# GeoManim

**Geospatial visualization and animation library using Manim**

GeoManim is a Python package that makes it easy to create beautiful animated maps and geospatial visualizations using the [Manim](https://www.manim.community/) animation engine.

## Features

- **2D Map Visualization**: Create animated maps with support for multiple projections
- **Data Integration**: Load and visualize data from GeoJSON, Shapefiles, and CSV files
- **Choropleth Maps**: Color regions based on data values with automatic colorbars/legends
- **Dynamic Basemaps**: Automatically fetch OpenStreetMap tiles for your data bounds
- **Categorical Coloring**: Auto-detect and color categorical data with legends
- **Ordered Animations**: Control animation sequence based on any data column (GDP, time, rankings, etc.)
- **Point Plotting**: Plot cities, locations, or any point data on maps
- **Path Animation**: Animate routes, migrations, and flows
- **Customizable**: Full control over colors, styles, and animations

## Showcase

### Cross-Country Routes: Seattle → Miami → NYC

![Cross-Country Routes](examples/cross_country_routes.gif)

Animated driving routes using OSRM API with dynamic OpenStreetMap basemap. Created with just a few lines of code:

```python
from geomanim import animate

animate(
    file_path="routes.geojson",
    column="route_name",
    order="order",
    basemap="OpenStreetMap.Mapnik",
    stroke_width=5,
    quality="high",
)
```

[See full example →](examples/README_cross_country.md)

## Installation

```bash
pip install geomanim
```

### Requirements

- Python >= 3.8
- Manim >= 0.17.0

## Quick Start

### One-Line API (Simplest)

Create an animated map with a single line of code:

```python
from geomanim import animate

# Animate any geospatial file
animate("path/to/file.geojson")

# With choropleth coloring
animate("countries.geojson", column="population")

# Custom output and white background (great for presentations!)
animate("data.geojson", column="gdp", output="my_map.mp4", background="white")

# With built-in basemap
animate("world.geojson", basemap="light", column="population")

# Ordered animation - countries appear by GDP (richest first)
animate("world.geojson", column="gdp", order="gdp", reverse_order=True)
```

That's it! The `animate()` function handles everything automatically.

**Real World Example:**
```python
# Download real country data
# curl -o world.geojson "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"

from geomanim import animate
animate("world.geojson", output="world_map.mp4")  # Creates animated world map!
```

### Using Manim Scenes (Advanced)

For more control, use the GeoMap class directly in Manim scenes:

```python
from manim import *
from geomanim import GeoMap, load_geojson

class WorldMapScene(Scene):
    def construct(self):
        # Load your data
        data = load_geojson("countries.geojson")

        # Create a map
        world_map = GeoMap(data=data, projection="mercator")

        # Add it to the scene with animation
        self.play(Create(world_map))
        self.wait()
```

### Plotting Points on a Map

```python
from manim import *
from geomanim.map2d import GeoMap
from geomanim.data import load_csv

class CitiesScene(Scene):
    def construct(self):
        # Create map
        world_map = GeoMap()
        self.add(world_map)

        # Load city data
        cities = load_csv("cities.csv", lat_col="latitude", lon_col="longitude")

        # Plot cities
        points = world_map.plot_points(cities)
        self.play(Create(points))
        self.wait()
```

### Creating a Choropleth Map with Colorbar

```python
from manim import *
from geomanim.map2d import GeoMap
from geomanim.data import load_geojson

class ChoroplethScene(Scene):
    def construct(self):
        # Load data with values
        countries = load_geojson("countries.geojson")

        # Create choropleth map
        world_map = GeoMap(data=countries, color_by="population")

        # Create colorbar/legend
        colorbar = world_map.create_colorbar(
            title="Population",
            num_labels=5,
            font_size=18
        )

        # Animate
        self.play(FadeIn(world_map))
        self.play(FadeIn(colorbar))
        self.wait()
```

**Note**: When using the simple `animate()` API with a `column` parameter, the colorbar is automatically added!

### Using Built-in Basemaps

Add beautiful background maps to your visualizations with the `basemap` parameter:

```python
from manim import *
from geomanim import GeoMap
import geopandas as gpd
from shapely.geometry import box

class BasemapExample(Scene):
    def construct(self):
        # Create your data
        data = gpd.GeoDataFrame({
            "geometry": [box(-50, -20, 50, 20)],
            "name": ["Region"],
            "value": [100]
        }, crs="EPSG:4326")

        # Create map with built-in basemap
        geo_map = GeoMap(
            data=data,
            basemap="light",  # Options: "light", "dark", "neutral"
            color_by="value",
            fill_opacity=0.6,
            stroke_color=WHITE,
            stroke_width=2,
        )

        # Animate (use FadeIn for maps with basemaps)
        self.play(FadeIn(geo_map), run_time=2)
        self.wait()
```

**Available Basemaps:**

Static basemaps:
- `basemap="light"` - Light theme with ocean and land colors (great for presentations)
- `basemap="dark"` - Dark theme basemap
- `basemap="neutral"` - Simple gradient background

Dynamic basemaps (automatically fetched using contextily):
- `basemap="OpenStreetMap.Mapnik"` - Standard OpenStreetMap tiles
- `basemap="CartoDB.Positron"` - Light, minimalist basemap
- `basemap="CartoDB.DarkMatter"` - Dark basemap
- `basemap="CartoDB.Voyager"` - Colorful basemap
- `basemap="auto"` - Auto-select based on data

No basemap:
- `basemap=None` - No basemap (default)

**Dynamic Basemaps**: GeoManim automatically fetches map tiles from OpenStreetMap providers based on your data's geographic bounds. This gives you up-to-date, detailed background maps without any manual setup.

**Custom Basemaps**: You can also provide your own basemap images with the `background_image` parameter for custom backgrounds with automatic projection handling.

### Ordered Animations

Control the order in which features appear during animation using the `order` parameter. Perfect for creating dramatic reveals based on rankings, time series, or any data column:

```python
from geomanim import animate

# Countries appear in order of GDP (richest first)
animate(
    "world.geojson",
    column="gdp_billions",
    order="gdp_billions",
    reverse_order=True,  # Highest values first
    basemap="light",
    output="gdp_reveal.mp4"
)

# Population growth over time (chronological)
animate(
    "cities.geojson",
    column="population",
    order="year",  # Animate chronologically
    reverse_order=False,  # Oldest first
)
```

**Parameters:**
- `order`: Column name to sort by (features animate in sorted order)
- `reverse_order`: `False` for ascending (default), `True` for descending

**Use Cases:**
- **Rankings**: Reveal countries by GDP, population, or any metric
- **Time series**: Animate events chronologically
- **Route tracking**: Waypoints appear in sequence
- **Story telling**: Control narrative flow with data-driven ordering

## Documentation

For detailed documentation and more examples, visit:
- [Installation Guide](docs/installation.md)
- [API Reference](docs/api/)
- [Examples Gallery](examples/)

## Examples

Check out the `examples/` directory for complete examples:

- **Basic Map**: Simple world map rendering
- **Plot Points**: Cities and locations on a map
- **Choropleth**: Data-driven coloring with colorbars
- **Cross-Country Routes**: OSRM routing with dynamic OSM basemap ([README](examples/README_cross_country.md))
- **Animated Paths**: Flight routes and migrations
- **Custom Regions**: Highlighting specific areas

Run an example:

```bash
# Simple API
python examples/09_cross_country_routes_simple.py

# Full Manim Scene
manim examples/09_cross_country_routes.py CrossCountryRoutes -pqh
```

## Articles & Tutorials

Learn more about GeoManim through these articles:
- [Create Geo-Spatial Visualization using Manim](https://medium.com/@kamol.roy08/create-geo-spatial-visualization-using-manim-2d179b2c21b9)
- [Create 3D Earth Animation using Manim](https://medium.com/@kamol.roy08/create-3d-earth-animation-using-manim-892245675f62)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on top of [Manim Community](https://www.manim.community/)
- Uses [GeoPandas](https://geopandas.org/) for geospatial data handling
- Inspired by the need to make geospatial animations accessible to everyone

## Author

**Kamol Roy**
- Medium: [@kamol.roy08](https://medium.com/@kamol.roy08)
- GitHub: [@kamolroy](https://github.com/kamolroy)

## Roadmap

- [x] 2D map visualization
- [x] Data integration (GeoJSON, Shapefile, CSV)
- [x] Choropleth maps
- [x] Point plotting and path animation
- [x] Colorbar/legend support for choropleth maps
- [x] White/black background themes
- [x] Built-in basemap support with custom image backgrounds
- [x] Dynamic basemap fetching (OpenStreetMap, CartoDB via contextily)
- [x] Categorical coloring with automatic legend generation
- [x] Ordered animations based on data columns
- [ ] 3D Earth globe visualization
- [ ] Advanced camera movements
- [ ] Interactive map generation
- [ ] More projection types
