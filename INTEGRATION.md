# Integration Guide

This guide explains how to integrate the `pytest-expected-json` fixture into other projects.

## Step 1: Install the Package

In your project's `pyproject.toml`, add the dependency:

```toml
dependencies = [
    "pytest>=7.0",
    # ... other dependencies
]

[project.optional-dependencies]
dev = [
    "pytest-expected-json @ file:///path/to/pytest-expected-json",  # for local development
    # or after publishing to PyPI:
    # "pytest-expected-json>=0.1.0",
]
```

Then install it:

```bash
pip install -e ".[dev]"
```

## Step 2: Update Test Configuration

Remove the custom `expected_data` fixture from your `tests/conftest.py` (if present) since it's now provided by the plugin.

Your conftest.py can be simplified to:

```python
"""Pytest configuration file."""

# The expected_data fixture is now automatically available via the plugin
# You can import configuration functions if needed:
from pytest_expected_json.fixture import set_assets_dir, set_default_return

# Optional: Configure the fixture
# set_assets_dir("tests/assets/saved")  # default is "tests/assets/saved"
# set_default_return({})  # default is {}
```

## Step 3: Use the Fixture

In your tests, use the fixture as before:

```python
def test_health(expected_data):
    """Test health endpoint."""
    response = client.get("/health")
    assert response.json() == expected_data
```

## Step 4: Update JSON File Paths

Ensure your expected data files follow the naming convention:

```
tests/
├── assets/
│   └── saved/
│       ├── tests_app__test_health__test_get_health.json
│       └── tests_app__test_workflow__test_create_workflow.json
├── tests_app/
│   ├── test_health.py
│   └── test_workflow.py
└── conftest.py
```

## Example: scenario-designer-api Integration

For the `scenario-designer-api` project:

1. **Add to `pyproject.toml`:**

```toml
[project.optional-dependencies]
dev = [
    "pytest-expected-json @ file:///home/E110898/GIT/pytest-expected-json",
    # ... other dev dependencies
]
```

2. **Simplify `tests/conftest.py`:**

Remove the current `expected_data` fixture definition since it's now provided by the plugin.

3. **Your existing tests work unchanged:**

```python
# tests/tests_app/test_health.py
def test_get_health(expected_data):
    """Fixture loads from tests/assets/saved/tests_app__test_health__test_get_health.json"""
    response = client.get("/health")
    assert response.json() == expected_data
```

## Troubleshooting

### Fixture not found

Ensure:

- The plugin is installed: `pip list | grep pytest-expected-json`
- The package entry point is registered: `python -m pytest --co` should list the fixture

### Files not loading

Check:

- File path follows the naming convention
- File is in `tests/assets/saved/` directory
- File contains valid JSON

### Customizing the behavior

In any conftest.py file:

```python
from pytest_expected_data.fixture import set_assets_dir, set_default_return

# Use different directory
set_assets_dir("fixtures/expected_data")

# Return None instead of {} when file not found
set_default_return(None)
```
