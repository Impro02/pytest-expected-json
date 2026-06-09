# pytest-expected-json

A reusable pytest fixture for loading expected test data from JSON files.

## Features

- 📋 Automatic file path resolution based on test location and name
- 🔧 Configurable assets directory and default return values
- 🎯 Support for parametrized tests
- 📦 Easy integration as a pytest plugin
- ✅ Type hints included

## Installation

### From local directory

```bash
pip install -e /path/to/pytest-expected-json
```

### From another project

Once published, install via:

```bash
pip install pytest-expected-json
```

## Usage

### Basic Setup

The fixture automatically registers as a pytest plugin. Add it to your dependencies in `pyproject.toml`:

```toml
dependencies = [
    "pytest-expected-json>=0.1.0",
]
```

### Using the Fixture

In your test files, use the `expected_data` fixture:

```python
import pytest

def test_get_user(expected_data):
    """Test with expected data."""
    # expected_data will automatically load from:
    # tests/assets/saved/tests_app__test_users__test_get_user.json
    result = get_user(1)
    assert result == expected_data
```

### File Naming Convention

The fixture automatically constructs filenames based on the test location:

```
{module_name}__{test_file}__{test_name}[@{param}].json
```

**Example:**
- Test file: `tests/tests_app/test_users.py`
- Test function: `test_get_user`
- Expected file: `tests/assets/saved/tests_app__test_users__test_get_user.json`

### Parametrized Tests

For parametrized tests, the parameter is appended to the filename:

```python
@pytest.mark.parametrize("expected_data", ["case1", "case2"], indirect=True)
def test_with_params(expected_data):
    # Loads: tests/assets/saved/tests_app__test_users__test_with_params@case1.json
    # Loads: tests/assets/saved/tests_app__test_users__test_with_params@case2.json
    pass
```

### Configuration

You can configure the fixture behavior in your test conftest:

```python
from pytest_expected_data.fixture import set_assets_dir, set_default_return

# Change the assets directory (default: "tests/assets/saved")
set_assets_dir("fixtures/expected_data")

# Change default return value when file not found (default: {})
set_default_return([])
```

Or in `pytest.ini`:

```ini
[pytest]
# Configuration via environment or conftest
```

## Directory Structure

Create your test expected data files:

```
tests/
├── assets/
│   └── saved/
│       ├── tests_app__test_users__test_get_user.json
│       ├── tests_app__test_users__test_list_users.json
│       └── tests_health__test_health__test_health_check.json
├── tests_app/
│   └── test_users.py
├── tests_health/
│   └── test_health.py
└── conftest.py
```

## Development

### Setup Development Environment

```bash
cd pytest-expected-json
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=src/pytest_expected_data --cov-report=html
```

### Code Quality

```bash
# Format code
black src tests

# Lint code
ruff check src tests
```

## API Reference

### `expected_data(request: pytest.FixtureRequest) -> JsonType`

Pytest fixture that loads expected test data from a JSON file.

**Parameters:**
- `request`: Pytest fixture request object

**Returns:**
- Parsed JSON data (dict, list, str, int, float, bool, or None)
- Default empty dict `{}` if file not found (configurable)

**Raises:**
- `FileNotFoundError`: If JSON file doesn't exist (caught and returns default)
- `json.JSONDecodeError`: If JSON is invalid (caught and returns default)

### `set_assets_dir(assets_dir: str) -> None`

Configure the directory where expected data JSON files are stored.

**Parameters:**
- `assets_dir`: Relative path from the tests directory (default: `"tests/assets/saved"`)

### `set_default_return(default_value: JsonType) -> None`

Configure the default return value when expected data file is not found.

**Parameters:**
- `default_value`: Any JSON-serializable value (default: `{}`)

## License

MIT
