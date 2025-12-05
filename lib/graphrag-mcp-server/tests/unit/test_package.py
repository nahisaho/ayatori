"""Tests for package initialization and version."""

import pytest


def test_package_import():
    """Test that the package can be imported."""
    import graphrag_mcp_server

    assert graphrag_mcp_server is not None


def test_version_exists():
    """Test that version is defined."""
    from graphrag_mcp_server import __version__

    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_version_format():
    """Test that version follows semver format."""
    from graphrag_mcp_server import __version__

    parts = __version__.split(".")
    assert len(parts) >= 2  # At least major.minor
    assert all(part.isdigit() for part in parts[:2])
