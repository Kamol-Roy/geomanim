"""
Real World Example - Using actual country data

This demonstrates GeoManim with real-world GeoJSON data.

Download the data:
curl -o world_countries.geojson "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"

Then run:
python examples/real_world_example.py
"""

from geomanim import animate
import geopandas as gpd

# Example 1: Simple world map
print("Creating world map animation...")
animate(
    "world_countries.geojson",
    output="world_basic.mp4",
    quality="low",
    show_preview=False
)
print("✓ Created: world_basic.mp4")

# Example 2: Focus on a continent
print("\nCreating Europe map...")
data = gpd.read_file("world_countries.geojson")

# Filter for European countries (simplified)
europe_names = [
    'France', 'Germany', 'Spain', 'Italy', 'United Kingdom',
    'Poland', 'Romania', 'Netherlands', 'Belgium', 'Greece',
    'Portugal', 'Czech Republic', 'Hungary', 'Sweden', 'Austria',
    'Bulgaria', 'Serbia', 'Switzerland', 'Denmark', 'Finland',
    'Slovakia', 'Norway', 'Ireland', 'Croatia', 'Bosnia and Herzegovina',
    'Albania', 'Lithuania', 'Slovenia', 'Latvia', 'Estonia'
]

europe = data[data['name'].isin(europe_names)]
europe.to_file("europe.geojson", driver="GeoJSON")

animate(
    "europe.geojson",
    output="europe_map.mp4",
    quality="low",
    show_preview=False
)
print("✓ Created: europe_map.mp4")

print("\n" + "="*60)
print("✓ All animations created successfully!")
print("  - world_basic.mp4 (258 countries)")
print("  - europe_map.mp4 (30 countries)")
print("="*60)
