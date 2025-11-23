"""
Cross-Country Routes - Simple API Example
==========================================

Same visualization using the simple animate() API.
Just one function call instead of writing a Manim Scene!
"""

from geomanim import animate

# One line to create the animation!
animate(
    file_path="examples/routes_merged.geojson",
    column="route_name",  # Categorical coloring by route
    order="order",  # Sequential animation: Seattle→Miami, then Miami→NYC
    output="cross_country_routes.mp4",
    basemap="OpenStreetMap.Mapnik",  # Dynamic OSM basemap
    stroke_width=5,
    quality="high",
    background="white",
    show_preview=True,
)

print("\n✓ Done! Animation saved to cross_country_routes.mp4")
print("Features:")
print("  - Sequential animation (Seattle→Miami, then Miami→NYC)")
print("  - Dynamic OSM basemap (auto-fetched for data bounds)")
print("  - Categorical coloring by route name")
print("  - Legend showing both routes")
print("  - All in one function call!")
