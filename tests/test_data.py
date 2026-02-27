"""
Config and project-path sanity tests.

Validates that essential project paths and configuration
resolve correctly — catches broken imports and missing dirs.
"""

from ncr_property_price_estimation.config import (
    DATA_DIR,
    MODELS_DIR,
    PROJ_ROOT,
)


def test_project_root_exists():
    assert PROJ_ROOT.exists(), f"PROJ_ROOT does not exist: {PROJ_ROOT}"


def test_required_dirs_exist():
    for d in [DATA_DIR, MODELS_DIR]:
        assert d.exists(), f"Required directory missing: {d}"


def test_requirements_file_exists():
    req = PROJ_ROOT / "requirements_production.txt"
    assert req.exists(), "requirements_production.txt not found"
