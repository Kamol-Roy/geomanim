"""
Script to prepare bundled assets for geomanim package.

This script downloads and prepares the basic world boundaries GeoJSON
that will be bundled with the package.
"""

import geopandas as gpd
from pathlib import Path
import json


def prepare_world_boundaries():
    """Download and save simplified world boundaries."""
    print("Preparing world boundaries asset...")

    # Get the assets directory
    assets_dir = Path(__file__).parent.parent / "geomanim" / "assets" / "data"
    assets_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Load Natural Earth low resolution data
        world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

        # Simplify geometries to reduce file size
        world["geometry"] = world["geometry"].simplify(tolerance=0.1)

        # Save as GeoJSON
        output_path = assets_dir / "world_boundaries.geojson"
        world.to_file(output_path, driver="GeoJSON")

        print(f"✓ World boundaries saved to: {output_path}")
        print(f"  - {len(world)} countries")
        print(f"  - File size: {output_path.stat().st_size / 1024:.1f} KB")

        # Create a metadata file
        metadata = {
            "source": "Natural Earth",
            "resolution": "110m (low resolution)",
            "features": len(world),
            "columns": list(world.columns),
        }

        metadata_path = assets_dir / "world_boundaries_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"✓ Metadata saved to: {metadata_path}")

    except Exception as e:
        print(f"✗ Error preparing assets: {e}")
        print("  Note: This asset is optional. Users can provide their own data.")


if __name__ == "__main__":
    prepare_world_boundaries()
