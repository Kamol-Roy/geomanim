## Contributing to GeoManim

Thank you for your interest in contributing to GeoManim! This document provides guidelines and instructions for contributing.

## How Can I Contribute?

### Reporting Bugs

If you find a bug, please open an issue on GitHub with:
- A clear, descriptive title
- Steps to reproduce the problem
- Expected vs actual behavior
- Your environment (OS, Python version, Manim version)
- Any error messages or logs

### Suggesting Features

Feature suggestions are welcome! Please open an issue with:
- A clear description of the feature
- Use cases and examples
- Why this feature would be useful
- Any implementation ideas (optional)

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** if you're adding functionality
4. **Update documentation** if you're changing behavior
5. **Ensure tests pass** by running `pytest`
6. **Submit a pull request**

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/kamolroy/geomanim.git
cd geomanim
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install package in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### 4. Install Pre-commit Hooks (Optional)

```bash
pre-commit install
```

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use meaningful variable and function names
- Add docstrings to all public functions and classes

### Docstring Format

Use Google-style docstrings:

```python
def my_function(arg1: str, arg2: int) -> bool:
    """
    Brief description of the function.

    More detailed description if needed.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: When this happens
    """
    pass
```

### Code Organization

- Keep functions focused and single-purpose
- Limit line length to 88 characters (Black default)
- Use type hints where possible
- Write self-documenting code with clear names

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=geomanim

# Run specific test file
pytest tests/test_map2d/test_map.py
```

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names: `test_function_name_expected_behavior`
- Include edge cases and error conditions
- Mock external dependencies (Manim rendering, file I/O)

Example test:

```python
def test_geomap_creates_with_valid_data():
    """Test that GeoMap initializes correctly with valid data."""
    world = get_world_boundaries()
    geo_map = GeoMap(data=world)
    assert geo_map is not None
    assert len(geo_map.submobjects) > 0
```

## Documentation

### API Documentation

- Add docstrings to all public APIs
- Include usage examples in docstrings
- Update README.md if adding major features

### Examples

- Add examples for significant new features
- Place examples in `examples/` directory
- Include comments explaining the code
- Follow the naming convention: `##_descriptive_name.py`

## Commit Messages

Write clear, descriptive commit messages:

- Use present tense ("Add feature" not "Added feature")
- First line: brief summary (50 chars or less)
- Add detailed description if needed after blank line
- Reference issue numbers when applicable

Good examples:
```
Add Robinson projection support

Implement Robinson projection transformation for 2D maps.
Includes tests and example usage.

Fixes #42
```

## Release Process

Maintainers will handle releases, but here's the process:

1. Update version in `geomanim/__version__.py`
2. Update `CHANGELOG.md`
3. Create a git tag: `git tag v0.1.0`
4. Build package: `python -m build`
5. Upload to PyPI: `twine upload dist/*`

## Getting Help

- Open an issue for questions
- Check existing issues and PRs
- Read the documentation

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

Thank you for contributing to GeoManim!
