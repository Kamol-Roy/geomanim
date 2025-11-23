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
        basemap: Built-in basemap ('light', 'dark', 'neutral', or None)
        background_image: Path to custom background image file
        background_bounds: Geographic bounds of image (minx, miny, maxx, maxy)
        background_crs: CRS of background image (default: 'EPSG:4326')
        background_opacity: Opacity of background image (0-1, default: 0.7)
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
        order: Optional[str] = None,
        reverse_order: bool = False,
        basemap: Optional[str] = None,
        background_image: Optional[str] = None,
        background_bounds: Optional[Tuple[float, float, float, float]] = None,
        background_crs: str = "EPSG:4326",
        background_opacity: float = 0.7,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.data = data
        self.use_axes = use_axes
        self.color_by = color_by
        self.color_scheme = color_scheme
        self.fill_color = fill_color
        self.fill_opacity = fill_opacity
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.stroke_width_auto_scale = True  # Auto-scale stroke width for LineStrings
        self.order = order
        self.reverse_order = reverse_order
        self.axes = None
        self.individual_features = []  # Store individual features for ordered animation

        # Handle basemap parameter
        if basemap is not None and background_image is None:
            import os

            # Check if it's a dynamic basemap request (contextily provider)
            if basemap.startswith("contextily:") or basemap in [
                "CartoDB.Positron", "CartoDB.DarkMatter", "CartoDB.Voyager",
                "OpenStreetMap.Mapnik", "auto"
            ]:
                # Dynamic basemap using contextily - will be fetched after data is loaded
                self._dynamic_basemap_provider = basemap
            else:
                # Static basemap
                # Get package directory
                package_dir = os.path.dirname(os.path.dirname(__file__))
                assets_dir = os.path.join(package_dir, "assets")

                # Map basemap names to files
                basemap_files = {
                    "light": "world_basemap_light.png",
                    "dark": "world_basemap_dark.png",
                    "neutral": "world_basemap_neutral.png",
                }

                if basemap in basemap_files:
                    background_image = os.path.join(assets_dir, basemap_files[basemap])
                    # Default world bounds for built-in basemaps (in Web Mercator meters)
                    if background_bounds is None:
                        background_bounds = (-20037508.34, -19971868.88, 20037508.34, 19971868.88)
                        background_crs = "EPSG:3857"
                    # Built-in basemaps are in Web Mercator projection
                    # Force mercator projection for proper alignment
                    projection = "mercator"

        # Background image parameters
        self.background_image = background_image
        self.background_bounds = background_bounds
        self.background_crs = background_crs
        self.background_opacity = background_opacity

        # Store choropleth metadata for colorbar
        self.choropleth_min = None
        self.choropleth_max = None
        self.choropleth_column = color_by
        self.is_categorical = False
        self.category_colors = {}  # Map category -> color for categorical data

        # Set projection (may be overridden by basemap)
        self.projection = projection
        self.proj_func = get_projection_function(projection)

        # If data is provided, render it
        if data is not None:
            # Fetch dynamic basemap if requested
            if hasattr(self, '_dynamic_basemap_provider'):
                try:
                    from geomanim.utils.basemap import get_basemap_for_data

                    # Parse provider
                    provider = self._dynamic_basemap_provider
                    if provider.startswith("contextily:"):
                        provider = provider.split(":", 1)[1]
                    elif provider == "auto":
                        # Auto-select based on fill color
                        provider = "CartoDB.Positron" if fill_color == WHITE else "CartoDB.DarkMatter"

                    print(f"Fetching dynamic basemap: {provider}")
                    img_path, img_bounds, img_crs = get_basemap_for_data(
                        self.data,
                        source=provider,
                        padding=0.15,  # 15% padding around data
                    )

                    background_image = img_path
                    background_bounds = img_bounds
                    background_crs = img_crs
                    projection = "mercator"  # Force mercator for Web Mercator basemaps

                    # Update instance variables
                    self.background_image = background_image
                    self.background_bounds = background_bounds
                    self.background_crs = background_crs
                    self.projection = projection
                    self.proj_func = get_projection_function(projection)

                except ImportError as e:
                    print(f"Warning: Could not load dynamic basemap: {e}")
                    print("Install with: pip install contextily")

            # Ensure data is in WGS84 (EPSG:4326) unless using Web Mercator basemap
            if self.data.crs and self.data.crs != "EPSG:4326" and not (self.background_image and self.background_crs == "EPSG:3857"):
                print(f"Converting from {self.data.crs} to EPSG:4326 (WGS84)")
                self.data = self.data.to_crs("EPSG:4326")

            # Reproject data to match basemap if using built-in basemap
            if self.background_image and self.background_crs == "EPSG:3857":
                # Clip to valid Web Mercator bounds first (-85 to 85 degrees latitude)
                # Web Mercator can't handle poles, so clip geometries
                from shapely.geometry import box
                clip_box = box(-180, -85, 180, 85)
                self.data = gpd.clip(self.data, clip_box)

                # Reproject data to Web Mercator to match basemap
                self.data = self.data.to_crs("EPSG:3857")
                # Use identity projection since data is already projected
                self.proj_func = lambda lat, lon: (lon, lat)  # Just swap to x, y order

            self._setup_axes()
            self._render_background()  # Render background first
            self._render_data()

    def _setup_axes(self):
        """Set up Manim Axes based on data bounds."""
        if self.data is None or self.data.empty or not self.use_axes:
            return

        # When using basemap, use basemap bounds instead of data bounds for perfect alignment
        if self.background_image and self.background_bounds:
            # Use basemap bounds directly
            min_x, min_y = self.background_bounds[0], self.background_bounds[1]
            max_x, max_y = self.background_bounds[2], self.background_bounds[3]
        else:
            # Get bounds from data
            bounds = self.data.total_bounds  # (minx, miny, maxx, maxy)

            # Check if data is already projected (EPSG:3857)
            if self.data.crs and self.data.crs.to_string() == "EPSG:3857":
                # Data is already in Web Mercator meters, use bounds directly
                min_x, min_y = bounds[0], bounds[1]
                max_x, max_y = bounds[2], bounds[3]
            else:
                # Apply projection to bounds
                min_x, min_y = self.proj_func(bounds[1], bounds[0])  # lat, lon
                max_x, max_y = self.proj_func(bounds[3], bounds[2])

        # Create axes with padding (but no padding if using background image)
        if self.background_image:
            # When using basemap, use exact bounds without padding for perfect alignment
            padding = 0.0
        else:
            # For maps without basemap, add 10% padding for visual breathing room
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

    def _get_scaled_stroke_width(self):
        """
        Calculate stroke width scaled to scene dimensions.
        For LineStrings (roads, paths), just return the stroke_width directly.
        Auto-scaling is disabled by default for better control.
        """
        # Just return stroke_width directly - let user control it
        return self.stroke_width

    def _render_background(self):
        """Render background image if provided, with proper cropping and reprojection."""
        if not self.background_image or not self.background_bounds:
            return

        try:
            from PIL import Image
            import pyproj
            from pyproj import Transformer
            import numpy as np
            from manim import ImageMobject

            # Load image
            img = Image.open(self.background_image)
            img_width, img_height = img.size

            # Background image bounds (in background_crs)
            bg_minx, bg_miny, bg_maxx, bg_maxy = self.background_bounds

            # Get data CRS (assume WGS84 if not specified)
            data_crs = self.data.crs.to_string() if self.data.crs else "EPSG:4326"

            # SIMPLIFIED PATH: If both data and basemap are in EPSG:3857 and axes use basemap bounds,
            # use full basemap without cropping for perfect alignment
            if (self.background_crs == "EPSG:3857" and
                data_crs == "EPSG:3857" and
                self.axes and self.use_axes):

                # Use full basemap image without cropping
                img_array = np.array(img)
                bg_image = ImageMobject(img_array)
                bg_image.set_opacity(self.background_opacity)

                # Position to match full axes bounds (which are set to basemap bounds)
                bl_point = self.axes.coords_to_point(bg_minx, bg_miny)
                tr_point = self.axes.coords_to_point(bg_maxx, bg_maxy)

                width = abs(tr_point[0] - bl_point[0])
                height = abs(tr_point[1] - bl_point[1])
                center_x = (bl_point[0] + tr_point[0]) / 2
                center_y = (bl_point[1] + tr_point[1]) / 2

                # Force both dimensions to match (stretch to fill if needed)
                # Set width first, then stretch height independently
                bg_image.width = width
                bg_image.height = height
                bg_image.move_to([center_x, center_y, 0])

                # Force stretch by directly manipulating the image to match both dimensions
                # This overrides aspect ratio preservation
                bg_image.stretch_to_fit_height(height)
                bg_image.stretch_to_fit_width(width)

                # Store as separate attribute (can't add ImageMobject to VGroup)
                self.background_mobject = bg_image
                return

            # COMPLEX PATH: Different CRS or need cropping
            # Data bounds (in data's CRS, typically EPSG:4326)
            data_bounds = self.data.total_bounds  # (minx, miny, maxx, maxy)
            data_minx, data_miny, data_maxx, data_maxy = data_bounds

            # Check if CRSs match - if so, no transformation needed
            if self.background_crs == data_crs:
                # Same CRS - use bounds directly
                intersect_minx = max(data_minx, bg_minx)
                intersect_miny = max(data_miny, bg_miny)
                intersect_maxx = min(data_maxx, bg_maxx)
                intersect_maxy = min(data_maxy, bg_maxy)

                intersect_minx_bg = intersect_minx
                intersect_miny_bg = intersect_miny
                intersect_maxx_bg = intersect_maxx
                intersect_maxy_bg = intersect_maxy
            else:
                # Different CRS - need transformation
                transformer = Transformer.from_crs(
                    self.background_crs,
                    data_crs,
                    always_xy=True  # lon, lat order
                )

                # Transform background bounds to data CRS
                bg_minx_data, bg_miny_data = transformer.transform(bg_minx, bg_miny)
                bg_maxx_data, bg_maxy_data = transformer.transform(bg_maxx, bg_maxy)

                # Calculate intersection of data bounds and background bounds
                intersect_minx = max(data_minx, bg_minx_data)
                intersect_miny = max(data_miny, bg_miny_data)
                intersect_maxx = min(data_maxx, bg_maxx_data)
                intersect_maxy = min(data_maxy, bg_maxy_data)

                # Transform intersection back to background CRS for cropping
                intersect_minx_bg, intersect_miny_bg = Transformer.from_crs(
                    data_crs, self.background_crs, always_xy=True
                ).transform(intersect_minx, intersect_miny)

                intersect_maxx_bg, intersect_maxy_bg = Transformer.from_crs(
                    data_crs, self.background_crs, always_xy=True
                ).transform(intersect_maxx, intersect_maxy)

            # Check if there's any overlap
            if intersect_minx >= intersect_maxx or intersect_miny >= intersect_maxy:
                print("Warning: Background image doesn't overlap with data bounds")
                return

            # Calculate crop region in pixel coordinates
            # Map intersection bounds back to image pixel space
            x_scale = img_width / (bg_maxx - bg_minx)
            y_scale = img_height / (bg_maxy - bg_miny)

            left = int((intersect_minx_bg - bg_minx) * x_scale)
            right = int((intersect_maxx_bg - bg_minx) * x_scale)
            # Note: Image Y is inverted (0 at top)
            top = int((bg_maxy - intersect_maxy_bg) * y_scale)
            bottom = int((bg_maxy - intersect_miny_bg) * y_scale)

            # Clamp to image bounds
            left = max(0, min(left, img_width))
            right = max(0, min(right, img_width))
            top = max(0, min(top, img_height))
            bottom = max(0, min(bottom, img_height))

            # Crop image
            if left < right and top < bottom:
                cropped = img.crop((left, top, right, bottom))

                # Convert to numpy array for ImageMobject
                import numpy as np
                img_array = np.array(cropped)

                # Create ImageMobject
                from manim import ImageMobject
                bg_image = ImageMobject(img_array)
                bg_image.set_opacity(self.background_opacity)

                # Position and scale using Axes if available
                if self.axes and self.use_axes:
                    # If data is already projected (EPSG:3857), use coordinates directly
                    if data_crs == "EPSG:3857":
                        # Coordinates are already in meters (x, y)
                        bl_point = self.axes.coords_to_point(intersect_minx, intersect_miny)
                        tr_point = self.axes.coords_to_point(intersect_maxx, intersect_maxy)
                    else:
                        # Get corner coordinates in data CRS
                        corners = [
                            (intersect_minx, intersect_miny),  # Bottom-left
                            (intersect_maxx, intersect_maxy),  # Top-right
                        ]

                        # Project to target projection
                        proj_corners = []
                        for lon, lat in corners:
                            x, y = self.proj_func(lat, lon)
                            proj_corners.append((x, y))

                        # Convert to Manim coordinates
                        bl_point = self.axes.coords_to_point(proj_corners[0][0], proj_corners[0][1])
                        tr_point = self.axes.coords_to_point(proj_corners[1][0], proj_corners[1][1])

                    # Calculate size and center
                    width = abs(tr_point[0] - bl_point[0])
                    height = abs(tr_point[1] - bl_point[1])
                    center_x = (bl_point[0] + tr_point[0]) / 2
                    center_y = (bl_point[1] + tr_point[1]) / 2

                    # Scale and position image
                    bg_image.width = width
                    bg_image.height = height
                    bg_image.move_to(np.array([center_x, center_y, -1]))  # z=-1 to render behind

                # Add to scene (as first element, so it's behind everything)
                self.submobjects.insert(0, bg_image)

        except Exception as e:
            print(f"Warning: Could not render background image: {e}")
            import traceback
            traceback.print_exc()

    def _render_data(self):
        """Render the geodata as Manim shapes."""
        if self.data is None or self.data.empty:
            return

        # Sort data by order column if specified
        data_to_render = self.data
        if self.order and self.order in self.data.columns:
            # Sort by the order column
            data_to_render = self.data.sort_values(
                by=self.order,
                ascending=not self.reverse_order  # reverse_order=True means descending
            ).copy()

        # Determine if we're doing choropleth coloring
        if self.color_by and self.color_by in data_to_render.columns:
            # Check if column is categorical (string/object) or numerical
            dtype = data_to_render[self.color_by].dtype

            if dtype == 'object' or dtype.name == 'category' or dtype.name.startswith('str'):
                # CATEGORICAL DATA - group by frequency
                self.is_categorical = True

                # Get top 5 categories by frequency
                value_counts = data_to_render[self.color_by].value_counts()
                top_5 = value_counts.head(5).index.tolist()

                # Assign colors to categories
                from geomanim.utils.colors import get_color_scheme

                # Get base color scheme
                if isinstance(self.color_scheme, str):
                    base_colors = get_color_scheme(self.color_scheme)
                else:
                    base_colors = self.color_scheme

                # We need len(top_5) + 1 colors (top 5 + "Other")
                n_needed = len(top_5) + 1

                # If we need more colors than available, repeat/extend the scheme
                if n_needed > len(base_colors):
                    colors = (base_colors * ((n_needed // len(base_colors)) + 1))[:n_needed]
                else:
                    colors = base_colors[:n_needed]

                for i, cat in enumerate(top_5):
                    self.category_colors[cat] = colors[i]
                self.category_colors['Other'] = colors[-1]  # Last color for "Other"

                # Add "Other" category for non-top-5
                data_to_render['_color_category'] = data_to_render[self.color_by].apply(
                    lambda x: x if x in top_5 else 'Other'
                )

                values = data_to_render['_color_category'].values
                min_val = max_val = None
            else:
                # NUMERICAL DATA - use min/max normalization
                self.is_categorical = False
                values = data_to_render[self.color_by].values
                # Use nanmin/nanmax to ignore NaN values in the data
                min_val, max_val = np.nanmin(values), np.nanmax(values)
                # Store for colorbar
                self.choropleth_min = min_val
                self.choropleth_max = max_val
        else:
            values = None
            min_val = max_val = None

        # Convert each geometry to Manim shapes
        for idx, row in data_to_render.iterrows():
            geom = row.geometry

            # Get color for this feature
            if values is not None:
                if self.is_categorical:
                    # Categorical: lookup color from map
                    category = row['_color_category']
                    color = self.category_colors.get(category, self.fill_color)
                else:
                    # Numerical: interpolate color
                    if not np.isnan(row[self.color_by]):
                        color = value_to_color(
                            row[self.color_by], min_val, max_val, self.color_scheme
                        )
                    else:
                        color = self.fill_color
            else:
                color = self.fill_color

            # Convert geometry to Manim shape
            # Pass color as both fill_color (for Polygons) and stroke_color (for LineStrings)
            shape = self._geometry_to_mobject(
                geom, fill_color=color, stroke_color=color
            )

            if shape is not None:
                self.add(shape)
                # Store individual features for ordered animation
                if self.order:
                    self.individual_features.append(shape)

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

            # Project coordinates - FIX: Data is in EPSG:4326, coords are (lon, lat)
            projected = []
            for lon, lat in coords:
                # For geographic coordinates (EPSG:4326), swap to (lat, lon) for projection
                x, y = self.proj_func(lat, lon)
                projected.append([x, y])

            projected = np.array(projected)

            if len(projected) < 2:
                return None

            # Use axes.plot_line_graph() like the pure Manim example!
            if self.axes and self.use_axes:
                # Use scaled stroke width for LineStrings (roads/paths)
                scaled_width = self._get_scaled_stroke_width()

                line_graph = self.axes.plot_line_graph(
                    projected[:, 0],  # x coordinates
                    projected[:, 1],  # y coordinates
                    add_vertex_dots=False,
                    line_color=stroke_color,
                    stroke_width=scaled_width,
                )

                # FIX: plot_line_graph returns a VDict, extract the actual line
                # The line is stored in the VDict under the key 'line_graph'
                if isinstance(line_graph, dict) or hasattr(line_graph, 'submobjects'):
                    # VDict stores the line in submobjects or as dict entry
                    if hasattr(line_graph, 'submob_dict') and 'line_graph' in line_graph.submob_dict:
                        line = line_graph.submob_dict['line_graph']
                    elif hasattr(line_graph, 'submobjects') and len(line_graph.submobjects) > 0:
                        # Get first submobject which should be the line
                        line = line_graph.submobjects[0]
                    else:
                        line = line_graph
                else:
                    line = line_graph

                return line
            else:
                # Fallback to manual normalization for non-axes mode
                x_norm, y_norm = normalize_coords(
                    projected[:, 0], projected[:, 1], self.width, self.height
                )
                points = [np.array([x, y, 0]) for x, y in zip(x_norm, y_norm)]

                # Create line
                line = VMobject()
                line.set_points_as_corners(points)
                scaled_width = self._get_scaled_stroke_width()
                line.set_stroke(color=stroke_color, width=scaled_width)

                return line

        except Exception as e:
            # Silently skip invalid geometries
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

    def create_colorbar(
        self,
        width: float = 0.5,
        height: float = 3.0,
        position: np.ndarray = None,
        num_labels: int = 5,
        font_size: int = 20,
        label_format: str = "{:.1f}",
        title: Optional[str] = None,
        text_color: str = WHITE,
        border_color: str = None,
    ) -> VGroup:
        """
        Create a colorbar/legend for choropleth maps.

        Args:
            width: Width of the colorbar
            height: Height of the colorbar
            position: Position to place the colorbar (default: right side of scene)
            num_labels: Number of labels on the colorbar
            font_size: Font size for labels
            label_format: Format string for numeric labels
            title: Optional title for the colorbar
            text_color: Color for text labels (default: WHITE)
            border_color: Color for border (default: same as text_color)

        Returns:
            VGroup containing the colorbar and labels
        """
        if self.choropleth_min is None or self.choropleth_max is None:
            # No choropleth data, return empty group
            return VGroup()

        # Default border color to match text
        if border_color is None:
            border_color = text_color

        colorbar_group = VGroup()

        # Default position: right side of scene
        if position is None:
            position = np.array([5.5, 0, 0])

        # Create color gradient using multiple rectangles
        num_segments = 50
        segment_height = height / num_segments

        for i in range(num_segments):
            # Calculate value for this segment
            val = self.choropleth_min + (
                i / num_segments
            ) * (self.choropleth_max - self.choropleth_min)

            # Get color for this value
            color = value_to_color(
                val,
                self.choropleth_min,
                self.choropleth_max,
                self.color_scheme,
            )

            # Create rectangle segment
            segment = Rectangle(
                width=width,
                height=segment_height,
                fill_color=color,
                fill_opacity=1.0,
                stroke_width=0,
            )

            # Position segment
            y_pos = position[1] - height / 2 + i * segment_height + segment_height / 2
            segment.move_to(position + np.array([0, y_pos - position[1], 0]))

            colorbar_group.add(segment)

        # Add border around colorbar
        border = Rectangle(
            width=width,
            height=height,
            stroke_color=border_color,
            stroke_width=2,
            fill_opacity=0,
        )
        border.move_to(position)
        colorbar_group.add(border)

        # Add labels
        for i in range(num_labels):
            # Calculate value for this label
            val = self.choropleth_min + (
                i / (num_labels - 1)
            ) * (self.choropleth_max - self.choropleth_min)

            # Format label text
            label_text = label_format.format(val)
            label = Text(label_text, font_size=font_size, color=text_color)

            # Position label to the right of colorbar
            y_pos = position[1] - height / 2 + (i / (num_labels - 1)) * height
            label.next_to(
                position + np.array([width / 2, y_pos - position[1], 0]),
                RIGHT,
                buff=0.2,
            )

            colorbar_group.add(label)

        # Add title if provided
        if title is None and self.choropleth_column:
            title = self.choropleth_column.replace("_", " ").title()

        if title:
            title_text = Text(title, font_size=font_size + 2, color=text_color)
            title_text.next_to(border, UP, buff=0.3)
            colorbar_group.add(title_text)

        return colorbar_group

    def get_creation_animation(self, run_time: float = 3, lag_ratio: float = 0.05):
        """
        Get the appropriate creation animation based on whether ordered animation is enabled.

        When order parameter is set, features animate sequentially in sorted order.
        Otherwise, all features animate simultaneously.

        Args:
            run_time: Total duration of the animation
            lag_ratio: Delay between features in ordered animation (0.0-1.0)
                      Lower values = more overlap, higher = more sequential

        Returns:
            Animation object (either LaggedStart for ordered, or Create for standard)

        Examples:
            >>> # Standard animation (all at once)
            >>> self.play(geo_map.get_creation_animation())
            >>>
            >>> # Ordered animation (sequential reveal)
            >>> geo_map = GeoMap(data=data, order="gdp", reverse_order=True)
            >>> self.play(geo_map.get_creation_animation(run_time=5, lag_ratio=0.1))
        """
        from manim import Create, LaggedStart

        if self.order and self.individual_features:
            # Use LaggedStart for sequential animation
            return LaggedStart(
                *[Create(feature) for feature in self.individual_features],
                lag_ratio=lag_ratio,
                run_time=run_time
            )
        else:
            # Standard Create animation for all features at once
            return Create(self, run_time=run_time)
