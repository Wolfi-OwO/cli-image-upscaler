"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image


@pytest.fixture()
def sample_image(tmp_path: Path) -> Path:
    """A small RGB PNG written to a temp directory."""
    path = tmp_path / "sample.png"
    Image.new("RGB", (16, 12), color=(120, 80, 200)).save(path)
    return path


@pytest.fixture()
def sample_rgba_image(tmp_path: Path) -> Path:
    """A small RGBA PNG with an alpha channel."""
    path = tmp_path / "sample_rgba.png"
    Image.new("RGBA", (10, 10), color=(10, 20, 30, 128)).save(path)
    return path
