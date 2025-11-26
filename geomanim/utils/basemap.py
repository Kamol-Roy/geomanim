"""Dynamic basemap fetching using contextily."""

import tempfile
from pathlib import Path
from typing import Optional, Tuple
import numpy as np


def fetch_contextily_basemap(
    bounds: Tuple[float, float, float, float],
    crs: str = "EPSG:4326",
    source: str = "CartoDB.Positron",
    zoom: Optional[int] = None,
    zoom_adjust: int = 0,
) -> Tuple[str, Tuple[float, float, float, float], str]:
    """
    Dynamically fetch a basemap using contextily based on data bounds.

    Args:
        bounds: Data bounds (minx, miny, maxx, maxy) in the specified CRS
        crs: Coordinate reference system of the bounds (default: EPSG:4326)
        source: Contextily basemap source name (default: CartoDB.Positron)
            Available: CartoDB.Positron, CartoDB.DarkMatter, CartoDB.Voyager,
                      OpenStreetMap.Mapnik, Stamen.Terrain, Stamen.TonerLite
        zoom: Manual zoom level (if None, auto-calculated)
        zoom_adjust: Adjustment to auto-calculated zoom (-2 to +2 recommended)

    Returns:
        Tuple of (image_path, image_bounds_in_3857, image_crs)
        - image_path: Path to downloaded basemap PNG
        - image_bounds_in_3857: Bounds in EPSG:3857 (minx, miny, maxx, maxy)
        - image_crs: Always "EPSG:3857" (Web Mercator)

    Examples:
        >>> bounds = (-82.5, 27.5, -80.0, 29.0)  # Florida region
        >>> img_path, img_bounds, img_crs = fetch_contextily_basemap(bounds)
        >>> # Use with GeoMap background_image parameter
    """
    try:
        import contextily as ctx
        import matplotlib.pyplot as plt
        import geopandas as gpd
        from shapely.geometry import box
        from pyproj import Transformer
    except ImportError as e:
        raise ImportError(
            f"contextily and dependencies required for dynamic basemaps.\n"
            f"Install with: pip install contextily matplotlib geopandas\n"
            f"Error: {e}"
        )

    # Parse source string to get contextily provider
    provider_map = {
        "CartoDB.Positron": ctx.providers.CartoDB.Positron,
        "CartoDB.DarkMatter": ctx.providers.CartoDB.DarkMatter,
        "CartoDB.Voyager": ctx.providers.CartoDB.Voyager,
        "OpenStreetMap.Mapnik": ctx.providers.OpenStreetMap.Mapnik,
    }

    provider = provider_map.get(source)
    if provider is None:
        # Try to get it directly if it's a full path
        try:
            parts = source.split(".")
            provider = ctx.providers
            for part in parts:
                provider = getattr(provider, part)
        except:
            available = ", ".join(provider_map.keys())
            raise ValueError(f"Unknown basemap source '{source}'. Available: {available}")

    # Create a GeoDataFrame with the bounds as a polygon
    minx, miny, maxx, maxy = bounds
    bbox = box(minx, miny, maxx, maxy)
    gdf = gpd.GeoDataFrame([1], geometry=[bbox], crs=crs)

    # Transform to Web Mercator (EPSG:3857) - required by contextily
    if crs != "EPSG:3857":
        gdf = gdf.to_crs("EPSG:3857")

    # Get bounds in Web Mercator
    bounds_3857 = gdf.total_bounds  # (minx, miny, maxx, maxy)

    # Calculate appropriate figure size based on aspect ratio
    width_m = bounds_3857[2] - bounds_3857[0]
    height_m = bounds_3857[3] - bounds_3857[1]

    # Handle edge cases for aspect ratio
    if height_m == 0 or not np.isfinite(height_m):
        aspect = 1.0  # Default aspect ratio
    else:
        aspect = width_m / height_m

    # Ensure aspect ratio is reasonable
    aspect = np.clip(aspect, 0.1, 10.0)  # Limit to reasonable range

    # Base figure width
    fig_width = 20
    fig_height = fig_width / aspect

    # Create figure
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=150)
    ax.set_xlim(bounds_3857[0], bounds_3857[2])
    ax.set_ylim(bounds_3857[1], bounds_3857[3])

    # Calculate zoom if not provided
    if zoom is None:
        # Auto-calculate zoom based on extent
        # This is a simple heuristic - can be improved
        from math import log, cos, radians

        # Get center latitude (in original CRS)
        center_lat = (miny + maxy) / 2
        if crs != "EPSG:4326":
            # Transform center to lat/lon for zoom calculation
            transformer = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
            _, center_lat = transformer.transform(
                (minx + maxx) / 2, (miny + maxy) / 2
            )

        # Calculate zoom level
        # Based on pixel width and meters
        EARTH_EQUATOR_METERS = 40075016.686
        TILE_SIZE = 256

        meters_per_pixel = width_m / (fig_width * 150)  # DPI = 150
        zoom = log(
            (EARTH_EQUATOR_METERS * cos(radians(center_lat))) /
            (meters_per_pixel * TILE_SIZE)
        ) / log(2)
        zoom = int(zoom) + zoom_adjust

        # Clamp zoom
        zoom = max(1, min(18, zoom))

    print(f"Fetching basemap tiles (zoom={zoom})...")

    # Add contextily basemap
    ctx.add_basemap(
        ax,
        crs="EPSG:3857",
        source=provider,
        zoom=zoom,
        attribution=False,
    )

    ax.axis('off')

    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(
        suffix='.png',
        delete=False,
        prefix='geomanim_basemap_'
    )
    temp_path = temp_file.name
    temp_file.close()

    plt.savefig(
        temp_path,
        bbox_inches='tight',
        pad_inches=0,
        dpi=150,
        facecolor='white' if 'Positron' in str(source) else 'black'
    )
    plt.close()

    print(f"✓ Basemap cached: {Path(temp_path).name}")
    print(f"  Bounds: {bounds_3857}")
    print(f"  Size: {Path(temp_path).stat().st_size / 1024:.1f} KB")

    return temp_path, tuple(bounds_3857), "EPSG:3857"


def get_basemap_for_data(
    data,
    source: str = "CartoDB.Positron",
    padding: float = 0.1,
    zoom_adjust: int = 0,
) -> Tuple[str, Tuple[float, float, float, float], str]:
    """
    Fetch a contextily basemap that fits the given geodata.

    Args:
        data: GeoDataFrame with the data to visualize
        source: Contextily basemap source (default: CartoDB.Positron)
        padding: Padding around data bounds as fraction (0.1 = 10% padding)
        zoom_adjust: Adjustment to auto-calculated zoom level

    Returns:
        Tuple of (image_path, image_bounds, image_crs)
    """
    # Get data bounds
    bounds = data.total_bounds  # (minx, miny, maxx, maxy)
    crs = data.crs.to_string() if data.crs else "EPSG:4326"

    # Add padding
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    pad_x = width * padding
    pad_y = height * padding

    padded_bounds = (
        bounds[0] - pad_x,
        bounds[1] - pad_y,
        bounds[2] + pad_x,
        bounds[3] + pad_y,
    )

    # Clamp bounds to valid ranges to prevent NaN/Inf errors
    # For EPSG:4326 (lat/lon), clamp to Web Mercator limits
    if crs == "EPSG:4326":
        # Clamp longitude to [-180, 180]
        # Clamp latitude to [-85.0511, 85.0511] (Web Mercator limit)
        WEB_MERCATOR_LAT_LIMIT = 85.0511
        padded_bounds = (
            max(-180.0, min(180.0, padded_bounds[0])),  # minx (lon)
            max(-WEB_MERCATOR_LAT_LIMIT, min(WEB_MERCATOR_LAT_LIMIT, padded_bounds[1])),  # miny (lat)
            max(-180.0, min(180.0, padded_bounds[2])),  # maxx (lon)
            max(-WEB_MERCATOR_LAT_LIMIT, min(WEB_MERCATOR_LAT_LIMIT, padded_bounds[3])),  # maxy (lat)
        )

    return fetch_contextily_basemap(
        padded_bounds,
        crs=crs,
        source=source,
        zoom_adjust=zoom_adjust,
    )
