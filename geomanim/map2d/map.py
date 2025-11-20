"""Core 2D map visualization class."""

import numpy as np
from manim import *
from manim import Polygon as ManimPolygon
from typing import Optional, Union, List, Tuple
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon, Point, LineString, MultiLineString

from geomanim.utils.coordinates import get_projection_function, normalize_coords
from geomanim.utils.colors import value_to_color, get_color_scheme


class GeoMap(VGroup):
    """
    Main class for creating 2D geospatial maps with Manim.

    This class handles rendering of geospatial data (countries, regions, etc.)
    with support for various map projections, data visualization, and animations.

    Args:
        data: GeoDataFrame containing geometries to plot
        projection: Map projection to use ('mercator', 'equirectangular', 'robinson')
        use_axes: Whether to use Manim Axes for coordinate transformation (default: True)
        color_by: Column name to use for choropleth coloring
        color_scheme: Color scheme for choropleth ('blues', 'reds', 'viridis', etc.)
        fill_color: Default fill color for regions
        fill_opacity: Fill opacity (0-1)
        stroke_color: Stroke color for boundaries
        stroke_width: Width of boundary strokes
    """

    def __init__(
        self,
        data: Optional[gpd.GeoDataFrame] = None,
        projection: str = "mercator",
        use_axes: bool = True,
        color_by: Optional[str] = None,
        color_scheme: Union[str, List[str]] = "blues",
        fill_color: str = BLUE_D,
        fill_opacity: float = 0.7,
        stroke_color: str = WHITE,
        stroke_width: float = 1,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.data = data
        self.projection = projection
        self.use_axes = use_axes
        self.color_by = color_by
        self.color_scheme = color_scheme
        self.fill_color = fill_color
        self.fill_opacity = fill_opacity
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.axes = None

        # Get projection function
        self.proj_func = get_projection_function(projection)

        # If data is provided, render it
        if data is not None:
            self._setup_axes()
            self._render_data()

    def _setup_axes(self):
        """Set up Manim Axes based on data bounds."""
        if self.data is None or self.data.empty or not self.use_axes:
            return

        # Get bounds from data
        bounds = self.data.total_bounds  # (minx, miny, maxx, maxy)

        # Apply projection to bounds
        min_x, min_y = self.proj_func(bounds[1], bounds[0])  # lat, lon
        max_x, max_y = self.proj_func(bounds[3], bounds[2])

        # Create axes with padding
        padding = 0.1
        x_padding = (max_x - min_x) * padding
        y_padding = (max_y - min_y) * padding

        self.axes = Axes(
            x_range=[min_x - x_padding, max_x + x_padding],
            y_range=[min_y - y_padding, max_y + y_padding],
            axis_config={"include_numbers": False, "include_ticks": False},
        )
        # Hide the axes (we just use them for coordinate transformation)
        self.axes.set_opacity(0)

    def _render_data(self):
        """Render the geodata as Manim shapes."""
        if self.data is None or self.data.empty:
            return

        # Determine if we're doing choropleth coloring
        if self.color_by and self.color_by in self.data.columns:
            values = self.data[self.color_by].values
            min_val, max_val = values.min(), values.max()
        else:
            values = None
            min_val = max_val = None

        # Convert each geometry to Manim shapes
        for idx, row in self.data.iterrows():
            geom = row.geometry

            # Get color for this feature
            if values is not None and not np.isnan(row[self.color_by]):
                color = value_to_color(
                    row[self.color_by], min_val, max_val, self.color_scheme
                )
            else:
                color = self.fill_color

            # Convert geometry to Manim shape
            shape = self._geometry_to_mobject(
                geom, fill_color=color
            )

            if shape is not None:
                self.add(shape)

    def _geometry_to_mobject(
        self, geom, fill_color=None, stroke_color=None
    ) -> Optional[VMobject]:
        """
        Convert a Shapely geometry to a Manim VMobject.

        Args:
            geom: Shapely geometry (Polygon, MultiPolygon, etc.)
            fill_color: Fill color override
            stroke_color: Stroke color override

        Returns:
            VMobject representing the geometry, or None if conversion fails
        """
        if fill_color is None:
            fill_color = self.fill_color
        if stroke_color is None:
            stroke_color = self.stroke_color

        if isinstance(geom, Polygon):
            return self._polygon_to_mobject(geom, fill_color, stroke_color)
        elif isinstance(geom, MultiPolygon):
            group = VGroup()
            for poly in geom.geoms:
                mob = self._polygon_to_mobject(poly, fill_color, stroke_color)
                if mob is not None:
                    group.add(mob)
            return group if len(group) > 0 else None
        elif isinstance(geom, (LineString, MultiLineString)):
            return self._linestring_to_mobject(geom, stroke_color)
        elif isinstance(geom, Point):
            return self._point_to_mobject(geom)
        else:
            return None

    def _polygon_to_mobject(
        self, polygon: Polygon, fill_color, stroke_color
    ) -> Optional[Polygon]:
        """Convert a Shapely Polygon to a Manim Polygon."""
        try:
            # Extract exterior coordinates
            coords = list(polygon.exterior.coords)
            if len(coords) < 3:
                return None

            # Project coordinates
            projected = []
            for lon, lat in coords:
                x, y = self.proj_func(lat, lon)
                projected.append([x, y])

            projected = np.array(projected)

            # Use Axes to transform coordinates to Manim points
            if self.axes and self.use_axes:
                # Use axes.coords_to_point() like in the original article
                points = self.axes.coords_to_point(projected)
            else:
                # Fallback to manual normalization
                x_norm, y_norm = normalize_coords(
                    projected[:, 0], projected[:, 1], 14, 8
                )
                points = np.column_stack([x_norm, y_norm, np.zeros(len(x_norm))])

            # Create Manim Polygon
            poly = ManimPolygon(
                *points,
                fill_color=fill_color,
                fill_opacity=self.fill_opacity,
                stroke_color=stroke_color,
                stroke_width=self.stroke_width,
            )

            return poly

        except Exception as e:
            # Skip invalid geometries
            return None

    def _linestring_to_mobject(
        self, linestring: Union[LineString, MultiLineString], stroke_color
    ) -> Optional[VMobject]:
        """Convert a LineString to a Manim VMobject."""
        if isinstance(linestring, MultiLineString):
            group = VGroup()
            for line in linestring.geoms:
                mob = self._linestring_to_mobject(line, stroke_color)
                if mob is not None:
                    group.add(mob)
            return group if len(group) > 0 else None

        try:
            coords = list(linestring.coords)
            if len(coords) < 2:
                return None

            # Project coordinates
            projected = []
            for lon, lat in coords:
                x, y = self.proj_func(lat, lon)
                projected.append([x, y])

            projected = np.array(projected)

            # Normalize to Manim coordinate system
            x_norm, y_norm = normalize_coords(
                projected[:, 0], projected[:, 1], self.width, self.height
            )

            # Create VMobject path
            points = [np.array([x, y, 0]) for x, y in zip(x_norm, y_norm)]

            if len(points) < 2:
                return None

            # Create line
            line = VMobject()
            line.set_points_as_corners(points)
            line.set_stroke(color=stroke_color, width=self.stroke_width)

            return line

        except Exception:
            return None

    def _point_to_mobject(self, point: Point) -> Optional[Dot]:
        """Convert a Point to a Manim Dot."""
        try:
            lon, lat = point.x, point.y
            x, y = self.proj_func(lat, lon)

            # Normalize (using reference bounds if available)
            x_norm, y_norm = normalize_coords(
                np.array([x]), np.array([y]), self.width, self.height
            )

            return Dot(
                point=np.array([x_norm[0], y_norm[0], 0]),
                color=self.fill_color,
            )
        except Exception:
            return None

    def plot_points(
        self,
        data: Union[gpd.GeoDataFrame, List[Tuple[float, float]]],
        color: str = RED,
        radius: float = 0.05,
        **kwargs,
    ) -> VGroup:
        """
        Plot points on the map.

        Args:
            data: GeoDataFrame with Point geometries or list of (lat, lon) tuples
            color: Color for the points
            radius: Radius of the dots
            **kwargs: Additional arguments for Dot

        Returns:
            VGroup containing all the point dots
        """
        points_group = VGroup()

        if isinstance(data, gpd.GeoDataFrame):
            for idx, row in data.iterrows():
                geom = row.geometry
                if isinstance(geom, Point):
                    lon, lat = geom.x, geom.y
                    x, y = self.proj_func(lat, lon)

                    # Get all x, y coordinates for normalization
                    all_x = []
                    all_y = []
                    for _, r in data.iterrows():
                        if isinstance(r.geometry, Point):
                            loni, lati = r.geometry.x, r.geometry.y
                            xi, yi = self.proj_func(lati, loni)
                            all_x.append(xi)
                            all_y.append(yi)

                    x_norm, y_norm = normalize_coords(
                        np.array(all_x), np.array(all_y), self.width, self.height
                    )

                    # Find this point's index
                    point_idx = list(data.index).index(idx)
                    dot = Dot(
                        point=np.array([x_norm[point_idx], y_norm[point_idx], 0]),
                        color=color,
                        radius=radius,
                        **kwargs,
                    )
                    points_group.add(dot)

        else:  # List of (lat, lon) tuples
            # Project all points first
            projected = []
            for lat, lon in data:
                x, y = self.proj_func(lat, lon)
                projected.append([x, y])

            projected = np.array(projected)

            # Normalize
            x_norm, y_norm = normalize_coords(
                projected[:, 0], projected[:, 1], self.width, self.height
            )

            # Create dots
            for i in range(len(data)):
                dot = Dot(
                    point=np.array([x_norm[i], y_norm[i], 0]),
                    color=color,
                    radius=radius,
                    **kwargs,
                )
                points_group.add(dot)

        return points_group

    def plot_path(
        self,
        coordinates: List[Tuple[float, float]],
        color: str = YELLOW,
        stroke_width: float = 3,
        **kwargs,
    ) -> VMobject:
        """
        Plot a path (line) on the map.

        Args:
            coordinates: List of (lat, lon) tuples defining the path
            color: Color of the path
            stroke_width: Width of the path line
            **kwargs: Additional arguments for VMobject

        Returns:
            VMobject representing the path
        """
        # Project all points
        projected = []
        for lat, lon in coordinates:
            x, y = self.proj_func(lat, lon)
            projected.append([x, y])

        projected = np.array(projected)

        # Normalize
        x_norm, y_norm = normalize_coords(
            projected[:, 0], projected[:, 1], self.width, self.height
        )

        # Create path
        points = [np.array([x, y, 0]) for x, y in zip(x_norm, y_norm)]

        path = VMobject(**kwargs)
        path.set_points_as_corners(points)
        path.set_stroke(color=color, width=stroke_width)

        return path
