"""Tests for fixture configuration primitives."""

import importlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

import pytest_expected_json
import pytest_expected_json.fixture as fixture_module
import pytest_expected_json.plugin as plugin_module
from pytest_expected_json.fixture import (
    ExpectedJsonConfig,
    create_expected_json_config_fixture,
    expected_data,
)


def test_expected_json_config_default_values() -> None:
    """ExpectedJsonConfig should expose package defaults."""
    config = ExpectedJsonConfig()
    assert config.assets_dir == Path("assets")


def test_expected_json_config_custom_assets_dir() -> None:
    """ExpectedJsonConfig should allow custom assets directory."""
    config = ExpectedJsonConfig(assets_dir=Path("assets") / "custom")
    assert config.assets_dir == Path("assets") / "custom"


def test_create_expected_json_config_fixture_returns_fixture_callable() -> None:
    """Fixture factory should return a callable pytest fixture object."""
    fixture_obj = create_expected_json_config_fixture(
        ExpectedJsonConfig(assets_dir=Path("assets") / "other")
    )
    assert callable(fixture_obj)


def test_create_expected_json_config_fixture_returns_config() -> None:
    """The wrapped fixture should return the provided config."""
    config = ExpectedJsonConfig(assets_dir=Path("assets") / "custom")
    fixture_obj = create_expected_json_config_fixture(config)

    assert cast(Any, fixture_obj).__wrapped__() is config


def test_fixture_module_reload_executes_import_time_setup() -> None:
    """Reloading the module should re-run its import-time configuration."""
    reloaded_module = importlib.reload(fixture_module)

    assert cast(
        Any, reloaded_module.expected_json_config
    ).__wrapped__().assets_dir == Path("assets")


def test_package_and_plugin_modules_reload_expose_public_api() -> None:
    """Reloading the package shims should exercise their import-time re-exports."""
    reloaded_package = importlib.reload(pytest_expected_json)
    reloaded_plugin = importlib.reload(plugin_module)

    assert reloaded_package.__all__ == [
        "ExpectedJsonConfig",
        "create_expected_json_config_fixture",
        "expected_data",
        "expected_json_config",
    ]
    assert reloaded_plugin.__all__ == ["expected_data", "expected_json_config"]


def test_expected_data_returns_empty_dict_for_non_matching_nodeid() -> None:
    """Expected data falls back to an empty mapping when the node ID does not match."""
    request = SimpleNamespace(
        node=SimpleNamespace(
            nodeid="package/module.py::test_example",
            originalname="test_example",
        ),
        config=SimpleNamespace(rootpath="."),
    )

    assert cast(Any, expected_data).__wrapped__(request, ExpectedJsonConfig()) == {}


def test_expected_data_returns_empty_dict_for_non_python_nodeid() -> None:
    """Node IDs without a Python file suffix should return an empty mapping."""
    request = SimpleNamespace(
        node=SimpleNamespace(
            nodeid="tests/tests_app/test_users.txt::test_get_user",
            originalname="test_get_user",
        ),
        config=SimpleNamespace(rootpath="."),
    )

    assert cast(Any, expected_data).__wrapped__(request, ExpectedJsonConfig()) == {}


def test_expected_data_returns_empty_dict_when_path_is_only_tests_prefix() -> None:
    """A tests-only path should be trimmed to empty and return an empty mapping."""
    request = SimpleNamespace(
        node=SimpleNamespace(
            nodeid="tests.py::test_example",
            originalname="test_example",
        ),
        config=SimpleNamespace(rootpath="."),
    )

    assert cast(Any, expected_data).__wrapped__(request, ExpectedJsonConfig()) == {}


def test_expected_data_loads_json_and_supports_parametrized_names(
    tmp_path: Path,
) -> None:
    """Expected data loads the JSON file matching the test and param IDs."""
    rootpath = tmp_path
    assets_dir = rootpath / "assets"
    assets_dir.mkdir(parents=True)

    payload = {"name": "alice", "active": True}
    file_path = assets_dir / "tests_app__test_users__test_get_user@case1.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    request = SimpleNamespace(
        node=SimpleNamespace(
            nodeid="tests/tests_app/test_users.py::test_get_user",
            originalname="test_get_user",
        ),
        config=SimpleNamespace(rootpath=rootpath),
        param="case1",
    )

    assert (
        cast(Any, expected_data).__wrapped__(request, ExpectedJsonConfig()) == payload
    )


def test_expected_data_returns_empty_dict_when_file_is_missing_and_failure_disabled(
    tmp_path: Path,
) -> None:
    """Expected data should fall back to an empty mapping when the file is missing."""
    request = SimpleNamespace(
        node=SimpleNamespace(
            nodeid="tests/tests_app/test_users.py::test_get_user",
            originalname="test_get_user",
        ),
        config=SimpleNamespace(rootpath=tmp_path),
    )

    assert (
        cast(Any, expected_data).__wrapped__(
            request, ExpectedJsonConfig(fail_if_missing=False)
        )
        == {}
    )


def test_expected_data_raises_when_file_is_missing_and_failure_enabled(
    tmp_path: Path,
) -> None:
    """Expected data should fail when the file is missing if failure mode enabled."""
    request = SimpleNamespace(
        node=SimpleNamespace(
            nodeid="tests/tests_app/test_users.py::test_get_user",
            originalname="test_get_user",
        ),
        config=SimpleNamespace(rootpath=tmp_path),
    )

    with pytest.raises(FileNotFoundError):
        cast(Any, expected_data).__wrapped__(
            request, ExpectedJsonConfig(fail_if_missing=True)
        )


def test_expected_data_loads_json_for_file_only_nodeid(tmp_path: Path) -> None:
    """File-only node IDs should use file name without a module prefix."""
    payload = {"status": "ok"}
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir(parents=True)
    (assets_dir / "test_users__test_get_user.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    request = SimpleNamespace(
        node=SimpleNamespace(
            nodeid="test_users.py::test_get_user",
            originalname="test_get_user",
        ),
        config=SimpleNamespace(rootpath=tmp_path),
    )

    assert (
        cast(Any, expected_data).__wrapped__(request, ExpectedJsonConfig()) == payload
    )


def test_expected_data_loads_json_for_nested_module_path(tmp_path: Path) -> None:
    """Nested module paths should be flattened into the filename prefix."""
    payload = {"count": 2}
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir(parents=True)
    (assets_dir / "api__v1__test_users__test_get_user.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    request = SimpleNamespace(
        node=SimpleNamespace(
            nodeid="tests/api/v1/test_users.py::test_get_user",
            originalname="test_get_user",
        ),
        config=SimpleNamespace(rootpath=tmp_path),
    )

    assert (
        cast(Any, expected_data).__wrapped__(request, ExpectedJsonConfig()) == payload
    )


def test_plugin_module_reexports_expected_symbols() -> None:
    """The plugin module should expose the expected public symbols."""
    assert plugin_module.__all__ == [
        "expected_data",
        "expected_json_config",
    ]
