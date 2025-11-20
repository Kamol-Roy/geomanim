# Building and Publishing GeoManim

This document provides instructions for building and publishing the geomanim package to PyPI.

## Prerequisites

### 1. Install Build Tools

```bash
pip install --upgrade pip
pip install build twine
```

### 2. Create PyPI Account

- Create an account at [https://pypi.org/](https://pypi.org/)
- Create an account at [https://test.pypi.org/](https://test.pypi.org/) (for testing)

### 3. Generate API Token

- Go to Account Settings on PyPI
- Scroll to API tokens section
- Create a new API token
- Save the token securely (you'll need it for uploading)

## Building the Package

### 1. Clean Previous Builds

```bash
rm -rf build/ dist/ *.egg-info
```

### 2. Update Version

Edit `geomanim/__version__.py`:

```python
__version__ = "0.1.0"  # Update this version
```

Update `CHANGELOG.md` with the new version details.

### 3. Build the Package

```bash
python -m build
```

This will create:
- `dist/geomanim-0.1.0.tar.gz` (source distribution)
- `dist/geomanim-0.1.0-py3-none-any.whl` (wheel distribution)

### 4. Verify the Build

Check that the distributions were created:

```bash
ls -lh dist/
```

Inspect the contents:

```bash
tar -tzf dist/geomanim-0.1.0.tar.gz
```

## Testing the Package

### 1. Create a Virtual Environment

```bash
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate
```

### 2. Install from Local Build

```bash
pip install dist/geomanim-0.1.0-py3-none-any.whl
```

### 3. Test the Installation

```python
python -c "import geomanim; print(geomanim.__version__)"
```

### 4. Test Basic Functionality

```python
python -c "from geomanim import GeoMap; print('Import successful')"
```

### 5. Deactivate and Remove Test Environment

```bash
deactivate
rm -rf test_env
```

## Publishing to TestPyPI (Recommended First)

Test the upload process on TestPyPI before publishing to the real PyPI.

### 1. Upload to TestPyPI

```bash
twine upload --repository testpypi dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your TestPyPI API token

### 2. Test Installation from TestPyPI

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ geomanim
```

(The `--extra-index-url` is needed to install dependencies from the real PyPI)

## Publishing to PyPI

Once you've tested on TestPyPI and everything works:

### 1. Upload to PyPI

```bash
twine upload dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your PyPI API token

### 2. Verify the Upload

Visit [https://pypi.org/project/geomanim/](https://pypi.org/project/geomanim/)

### 3. Test Installation

```bash
pip install geomanim
```

## Post-Publication

### 1. Tag the Release on Git

```bash
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```

### 2. Create GitHub Release

- Go to your GitHub repository
- Click "Releases" → "Create a new release"
- Select the tag you just created
- Add release notes from CHANGELOG.md
- Publish the release

### 3. Update Documentation

- Ensure Read the Docs is updated (if configured)
- Update any external documentation links

## Troubleshooting

### Build Fails

- Check that `pyproject.toml` is valid
- Ensure all required files are present
- Check that `MANIFEST.in` includes all necessary files

### Upload Fails

- Verify API token is correct
- Check internet connection
- Ensure version number hasn't been used before

### Installation Fails

- Check that all dependencies are specified correctly
- Verify Python version compatibility
- Check for missing package data files

## Quick Reference

```bash
# Complete build and publish workflow
rm -rf build/ dist/ *.egg-info
python -m build
twine check dist/*
twine upload --repository testpypi dist/*
# Test installation
twine upload dist/*
# Tag release
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```

## Using .pypirc (Optional)

Create `~/.pypirc` to store repository URLs:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
```

Then upload with:

```bash
twine upload --repository testpypi dist/*  # For TestPyPI
twine upload dist/*                         # For PyPI
```

## Security Notes

- **Never commit API tokens** to version control
- Store tokens in password manager
- Rotate tokens periodically
- Use separate tokens for different projects
- Consider using GitHub Actions for automated publishing

## Automated Publishing with GitHub Actions

Consider setting up GitHub Actions for automated publishing when creating a new release tag. See `.github/workflows/publish.yml` (if configured).
