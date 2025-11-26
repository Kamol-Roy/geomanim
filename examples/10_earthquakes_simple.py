"""
Major Earthquakes 1990-2023 - Simple Version
============================================

Shows all very major earthquakes (magnitude >= 7.0) with dark basemap.
"""

from geomanim import animate

# Animate very major earthquakes
animate(
    file_path="examples/earthquakes_very_major.geojson",
    column="magnitudo",  # Color by magnitude
    basemap="CartoDB.DarkMatter",  # Dark basemap
    color_scheme="plasma",  # Hot colormap for earthquakes
    stroke_width=4,
    quality="high",
    background="black",
    output="earthquakes_1990_2023.mp4",
    show_preview=True,
)

print("\n✓ Done! Major Earthquakes 1990-2023")
print("Features:")
print("  - 498 very major earthquakes (magnitude >= 7.0)")
print("  - Dark basemap with hot plasma colormap")
print("  - Color coded by magnitude (7.0 - 9.1)")
