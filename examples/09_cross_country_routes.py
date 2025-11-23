"""
Cross-Country Road Trip Routes
================================

Example showing animated driving routes from Seattle to Miami to NYC
using OSRM routing and dynamic OpenStreetMap basemap.

Routes:
- Seattle, WA → Miami, FL (5,315 km, 59 hours)
- Miami, FL → New York City, NY (2,057 km, 24 hours)

Features demonstrated:
- OSRM API integration for realistic driving routes
- Dynamic contextily/OSM basemap matching data extent
- Categorical coloring by route
- Sequential ordered animation showing journey progression
"""

from manim import *
from geomanim import GeoMap, load_geojson


class CrossCountryRoutes(Scene):
    """Animated cross-country road trip: Seattle → Miami → NYC."""

    def construct(self):
        # White background for better visibility
        self.camera.background_color = WHITE

        # Load merged route data (2 complete LineStrings instead of 49,886 tiny segments!)
        import os
        data_path = os.path.join(os.path.dirname(__file__), "routes_merged.geojson")
        routes = load_geojson(data_path)

        print(f"\nRoute data loaded:")
        print(f"  Routes: {len(routes)} complete paths")
        for idx, row in routes.iterrows():
            print(f"  - {row['route_name']}: {row['distance_km']:.0f} km")

        # Create map with dynamic OSM basemap
        # Only 2 LineStrings to render = FAST!
        geo_map = GeoMap(
            data=routes,
            color_by='route_name',  # Color by route (categorical)
            color_scheme='plasma',
            stroke_width=5,
            fill_opacity=0,
            basemap="OpenStreetMap.Mapnik",  # Dynamic OSM basemap!
        )

        # Title
        title = Text(
            "Cross-Country Road Trip: Seattle → Miami → NYC",
            font_size=32,
            color=BLACK,
            weight=BOLD
        )
        title.to_edge(UP, buff=0.3)

        # Route legend
        legend = VGroup()
        for route_name, color in geo_map.category_colors.items():
            if route_name != 'Other':
                route_data = routes[routes['route_name'] == route_name].iloc[0]
                label = Text(
                    f"{route_name}",
                    font_size=20,
                    color=color,
                    weight=BOLD
                )
                stats = Text(
                    f"{route_data['distance_km']:.0f} km, {route_data['duration_hours']:.0f}h",
                    font_size=16,
                    color=GREY_D
                )
                route_group = VGroup(label, stats).arrange(RIGHT, buff=0.3)
                legend.add(route_group)

        legend.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        legend.to_corner(UL, buff=0.5).shift(DOWN * 0.5)

        # Info
        info = Text(
            "Routes from OSRM • OpenStreetMap basemap • Sequential animation",
            font_size=14,
            color=GREY_D
        )
        info.to_edge(DOWN, buff=0.3)

        # Render
        self.play(Write(title), run_time=1.5)

        # Add OSM basemap background
        if hasattr(geo_map, 'background_mobject') and geo_map.background_mobject:
            self.add(geo_map.background_mobject)

        self.play(FadeIn(legend), FadeIn(info), run_time=0.5)

        # Animate routes with Create() - fast since only 2 LineStrings!
        self.play(Create(geo_map), run_time=4)

        self.wait(2)
