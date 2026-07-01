"""Pytest fixture for loading expected test data from JSON files."""

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

import pytest

JsonType = dict[str, Any] | list[Any] | str | int | float | bool | None
FixtureScope = Literal["function", "class", "module", "package", "session"]


@dataclass
class ExpectedJsonConfig:
    """
    Configuration for the expected_data fixture.

    Attributes:
        assets_dir (Path): Base path of the assets directory.
        fail_if_missing (bool):  When True, raise FileNotFoundError if an asset is
             missing. When False, return an empty JSON object ({}). Defaults to False.

    """

    assets_dir: Path = Path("assets")
    fail_if_missing: bool = False


def create_expected_json_config_fixture(
    config: ExpectedJsonConfig | None = None, *, scope: FixtureScope = "session"
) -> Callable[[], ExpectedJsonConfig]:
    """
    Create a fixture that returns config used by the expected_data fixture.

    Override this fixture in a project to provide custom configuration.
    """

    def fixture() -> ExpectedJsonConfig:
        """Provide configuration consumed by the expected_data fixture."""
        return config or ExpectedJsonConfig()

    decorated_fixture = pytest.fixture(scope=cast(Any, scope))(fixture)
    return cast(Callable[[], ExpectedJsonConfig], decorated_fixture)


expected_json_config = create_expected_json_config_fixture()


@pytest.fixture()
def expected_data(
    request: pytest.FixtureRequest, expected_json_config: ExpectedJsonConfig
) -> JsonType:
    """
    Load the expected data from a JSON file based on the test location and name.

    The fixture automatically constructs a filename from the test module
    and function name. If a parametrized test is used, the parameter
    is appended to the filename.

    File naming convention:
        {module_name}__{test_name}__{original_name}[@{param}].json

    Example:
        For test `test_health.py@test_get_health`, the fixture looks for:
        tests/assets/saved/tests_app__test_health__test_get_health.json

    Args:
        request: Pytest request object containing test information.
        expected_json_config: Fixture-provided configuration for asset lookup
            and fallback behavior.

    Returns:
        Parsed JSON data from the file, or the configured default value
            if file not found.

    """
    config = expected_json_config

    # Build filename from node id path, flattening path segments with "__".
    # Pytest node IDs are typically like:
    # ../tests/test_<module>.py::test_<function>[param-id]
    # Keep only the file path segment before "::".
    node_id_path = request.node.nodeid.split("::", 1)[0]
    if not node_id_path.endswith(".py"):
        return {}

    module_path = node_id_path[:-3]
    path_parts = [part for part in module_path.split("/") if part]
    if path_parts and path_parts[0] == "tests":
        path_parts = path_parts[1:]

    if not path_parts:
        return {}

    test_name = request.node.originalname
    file_name = "__".join([*path_parts, test_name])

    # Add parametrize id if present
    if hasattr(request, "param"):
        file_name += f"@{request.param}"

    # Get the tests directory
    file_path = request.config.rootpath / config.assets_dir / f"{file_name}.json"

    try:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with file_path.open(encoding="utf-8") as f:
            return cast(JsonType, json.load(f))
    except (FileNotFoundError, FileExistsError):
        if expected_json_config.fail_if_missing:
            raise
        return {}
