# Cross-Country Routes Example

This example demonstrates routing from Seattle → Miami → NYC using OSRM API with dynamic OpenStreetMap basemaps.

![Cross-Country Routes Animation](cross_country_routes.gif)

## Files

- `routes_merged.geojson` - Merged route data (2 LineStrings)
- `09_cross_country_routes.py` - Full Manim Scene implementation
- `09_cross_country_routes_simple.py` - Simple one-line API

## Data Source

Routes fetched from OSRM (Open Source Routing Machine):
- **Seattle, WA → Miami, FL**: 5,315 km (59 hours driving)
- **Miami, FL → New York City, NY**: 2,057 km (24 hours driving)

## Method 1: Simple API (Recommended)

```python
from geomanim import animate

animate(
    file_path="examples/routes_merged.geojson",
    column="route_name",  # Categorical coloring
    order="order",  # Sequential animation
    basemap="OpenStreetMap.Mapnik",  # Dynamic OSM basemap
    stroke_width=5,
    quality="high",
    output="cross_country_routes.mp4",
)
```

**Run:**
```bash
python examples/09_cross_country_routes_simple.py
```

## Method 2: Full Manim Scene (Advanced)

For more control over animations, use the full Manim Scene:

```python
from manim import *
from geomanim import GeoMap, load_geojson

class CrossCountryRoutes(Scene):
    def construct(self):
        self.camera.background_color = WHITE

        routes = load_geojson("routes_merged.geojson")

        geo_map = GeoMap(
            data=routes,
            color_by='route_name',
            basemap="OpenStreetMap.Mapnik",
            stroke_width=5,
        )

        self.play(Create(geo_map), run_time=4)
        self.wait(2)
```

**Run:**
```bash
manim -pqh examples/09_cross_country_routes.py CrossCountryRoutes
```

## Features Demonstrated

1. **Sequential Animation**: Routes appear in order (Seattle→Miami, then Miami→NYC)
2. **Dynamic Basemap**: OSM tiles auto-fetched for route bounds
3. **Categorical Coloring**: Different colors for each route
4. **Performance**: 2 merged LineStrings vs 49,886 segments (1000x faster!)
5. **Legend**: Automatic legend for categorical data

## Generating Your Own Routes

To fetch routes from OSRM:

```python
# See fetch_routes_osrm.py for full implementation
import requests
from shapely.geometry import LineString
from shapely.ops import linemerge

# Fetch route from OSRM
url = "http://router.project-osrm.org/route/v1/driving/lon1,lat1;lon2,lat2"
response = requests.get(url, params={'overview': 'full', 'geometries': 'geojson'})
geometry = response.json()['routes'][0]['geometry']

# Create LineString and save
linestring = LineString(geometry['coordinates'])
gdf = gpd.GeoDataFrame({'route_name': ['My Route'], 'geometry': [linestring]}, crs='EPSG:4326')
gdf.to_file('my_route.geojson')
```

## Performance Tips

**Important:** OSRM returns thousands of tiny segments. Always merge them first!

```python
from shapely.ops import linemerge

# BAD: 49,886 segments = slow rendering
routes_raw = gpd.read_file('routes_raw.geojson')

# GOOD: 2 merged LineStrings = fast!
routes_merged = routes_raw.dissolve(by='route_name').reset_index()
```

## Output

- **MP4 Video**: 1920x1080 (1080p60), ~1.2 MB
- **GIF Animation**: 960x540 (15fps), ~1.4 MB
- Duration: ~13 seconds
- Basemap: OpenStreetMap tiles (dynamically fetched)
