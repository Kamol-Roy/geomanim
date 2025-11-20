# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-19

### Added
- Initial release of GeoManim
- `GeoMap` class for 2D map visualization
- Support for multiple map projections:
  - Mercator
  - Equirectangular (Plate Carrée)
  - Robinson
- Data loading utilities:
  - GeoJSON support via `load_geojson()`
  - Shapefile support via `load_shapefile()`
  - CSV support with lat/lon columns via `load_csv()`
  - Auto-detection with `load_data()`
  - Built-in world boundaries via `get_world_boundaries()`
- Choropleth map support with `color_by` parameter
- Point plotting with `plot_points()` method
- Path animation with `plot_path()` method
- Color schemes and utilities:
  - Predefined color schemes (blues, reds, greens, viridis, plasma, etc.)
  - Color interpolation functions
  - Color legend creation
- Coordinate transformation utilities
- Comprehensive examples:
  - Basic world map
  - Different projections
  - Plotting cities
  - Choropleth maps
  - Animated flight paths
  - Region highlighting
  - Custom styling
- Full documentation:
  - README with quick start guide
  - API documentation
  - Example gallery
  - Contributing guidelines
- Unit and integration tests
- MIT License

### Documentation
- README.md with installation and usage instructions
- Examples directory with 6 comprehensive examples
- CONTRIBUTING.md with development guidelines
- Full API documentation with docstrings

### Infrastructure
- Package configuration with pyproject.toml
- Git ignore file
- Manifest for including assets
- Test infrastructure with pytest

## [Unreleased]

### Planned for v0.2.0
- 3D Earth globe visualization
- Advanced camera movements and animations
- More map projections
- Interactive map generation
- Animated legends and color bars
- Performance optimizations
- Video tutorials
- Enhanced documentation

---

## Version History

- **0.1.0** - Initial release (2025-11-19)

[0.1.0]: https://github.com/kamolroy/geomanim/releases/tag/v0.1.0
[Unreleased]: https://github.com/kamolroy/geomanim/compare/v0.1.0...HEAD
