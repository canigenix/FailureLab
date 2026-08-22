import sys
from pathlib import Path

import failurelab
import tomllib


ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"


def load_pyproject():
    with PYPROJECT.open(
        "rb"
    ) as file:
        return tomllib.load(
            file
        )


def test_v1_package_name():
    data = load_pyproject()

    assert (
        data["project"]["name"]
        == "failurelab"
    )


def test_v1_python_requirement():
    data = load_pyproject()

    assert (
        data["project"]["requires-python"]
        == ">=3.10"
    )


def test_v1_license_metadata():
    data = load_pyproject()

    assert (
        data["project"]["license"]
        == "Apache-2.0"
    )


def test_v1_cli_entry_point():
    data = load_pyproject()

    assert (
        data["project"]["scripts"]["failurelab"]
        == "failurelab.cli:main"
    )


def test_v1_build_backend():
    data = load_pyproject()

    assert (
        data["build-system"]["build-backend"]
        == "setuptools.build_meta"
    )


def test_v1_core_dependencies():
    data = load_pyproject()

    dependencies = set(
        data["project"]["dependencies"]
    )

    assert "numpy>=1.24" in dependencies
    assert "pillow>=9.0" in dependencies


def test_v1_required_extras_exist():
    data = load_pyproject()

    extras = (
        data["project"]["optional-dependencies"]
    )

    assert "vision" in extras
    assert "visualization" in extras
    assert "dev" in extras


def test_development_version_matches_package():
    data = load_pyproject()

    assert (
        data["project"]["version"]
        == failurelab.__version__
    )


def test_pyproject_exists():
    assert PYPROJECT.exists()


def test_supported_runtime():
    assert sys.version_info >= (
        3,
        10,
    )