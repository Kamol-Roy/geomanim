# GeoManim

**Geospatial visualization and animation library using Manim**

GeoManim is a Python package that makes it easy to create beautiful animated maps and geospatial visualizations using the [Manim](https://www.manim.community/) animation engine.

## Features

- **2D Map Visualization**: Create animated maps with support for multiple projections
- **Data Integration**: Load and visualize data from GeoJSON, Shapefiles, and CSV files
- **Choropleth Maps**: Color regions based on data values
- **Point Plotting**: Plot cities, locations, or any point data on maps
- **Path Animation**: Animate routes, migrations, and flows
- **Customizable**: Full control over colors, styles, and animations

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

# Custom output
animate("data.geojson", column="gdp", output="my_map.mp4")
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

### Creating a Choropleth Map

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

        # Animate
        self.play(FadeIn(world_map))
        self.wait()
```

## Documentation

For detailed documentation and more examples, visit:
- [Installation Guide](docs/installation.md)
- [API Reference](docs/api/)
- [Examples Gallery](examples/)

## Examples

Check out the `examples/` directory for more complete examples:

- **Basic Map**: Simple world map rendering
- **Plot Points**: Cities and locations on a map
- **Choropleth**: Data-driven coloring
- **Animated Paths**: Flight routes and migrations
- **Custom Regions**: Highlighting specific areas

Run an example:

```bash
manim examples/01_basic_map.py WorldMapScene -pql
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
- [ ] 3D Earth globe visualization
- [ ] Advanced camera movements
- [ ] Interactive map generation
- [ ] More projection types
- [ ] Animated legends and color bars
