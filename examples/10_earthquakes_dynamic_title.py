"""
Major Earthquakes 1990-2023 with Dynamic Year Title
===================================================

Demonstrates dynamic title updates as earthquakes appear chronologically.
Shows all major earthquakes (magnitude >= 6.0) with year updating in title.
"""

from geomanim import animate

# Animate very major earthquakes with dynamic year in title
animate(
    file_path="earthquakes_very_major.geojson",
    column="magnitudo",  # Color by magnitude
    size_by="magnitudo",  # Size points by magnitude
    order="order",  # Chronological animation
    title_column="year",  # Dynamic title showing year
    basemap="CartoDB.DarkMatter",  # Dark basemap
    color_scheme="plasma",  # Hot colormap for earthquakes
    stroke_width=4,
    min_size=0.04,  # Smaller earthquakes visible
    max_size=0.20,  # Larger for big quakes
    quality="high",
    background="black",
    output="earthquakes_1990_2023.mp4",
    colorbar_bbox=(5.8, 0),  # Position colorbar on right
    show_preview=True,
)

print("\n✓ Done! Major Earthquakes 1990-2023")
print("Features:")
print("  - Dynamic title showing current year (fast year transitions!)")
print("  - 498 very major earthquakes (magnitude >= 7.0)")
print("  - Chronological animation (1990 → 2023)")
print("  - Dark basemap with hot plasma colormap")
print("  - Point size AND color both scaled by magnitude")
print("  - Colorbar positioned on right side")
print("  - Faster animation (0.75s per year)")
