"""Tests for the core upscaling engine (Lanczos backend / pure-python paths)."""

from __future__ import annotations

import pytest
from PIL import Image

from image_upscaler.exceptions import UnsupportedScaleError
from image_upscaler.upscaler import (
    SUPPORTED_SCALES,
    Backend,
    UpscaleConfig,
    Upscaler,
    _passes_for_scale,
)


@pytest.mark.parametrize("scale", SUPPORTED_SCALES)
def test_lanczos_upscales_to_exact_target(scale: int) -> None:
    cfg = UpscaleConfig(scale=scale, backend=Backend.LANCZOS)
    upscaler = Upscaler(cfg)
    src = Image.new("RGB", (8, 6), color=(10, 20, 30))
    out = upscaler.upscale_image(src)
    assert out.size == (8 * scale, 6 * scale)


def test_lanczos_preserves_mode_for_rgba() -> None:
    cfg = UpscaleConfig(scale=2, backend=Backend.LANCZOS)
    src = Image.new("RGBA", (5, 5), color=(1, 2, 3, 4))
    out = Upscaler(cfg).upscale_image(src)
    assert out.size == (10, 10)
    assert out.mode == "RGBA"


def test_unsupported_scale_raises() -> None:
    with pytest.raises(UnsupportedScaleError):
        UpscaleConfig(scale=3)


@pytest.mark.parametrize(
    ("scale", "expected"),
    [(2, 1), (4, 1), (8, 2), (16, 2)],
)
def test_passes_for_scale(scale: int, expected: int) -> None:
    assert _passes_for_scale(scale) == expected


def test_explicit_lanczos_backend_selected() -> None:
    upscaler = Upscaler(UpscaleConfig(backend=Backend.LANCZOS))
    assert upscaler.backend is Backend.LANCZOS


def test_upscale_file_roundtrip(sample_image, tmp_path) -> None:
    dest = tmp_path / "out.png"
    upscaler = Upscaler(UpscaleConfig(scale=2, backend=Backend.LANCZOS))
    result = upscaler.upscale_file(sample_image, dest)
    assert result == dest
    assert dest.exists()
    with Image.open(dest) as img:
        assert img.size == (32, 24)


def test_config_accepts_string_enums() -> None:
    cfg = UpscaleConfig(scale=4, model="anime", backend="lanczos")
    assert cfg.backend is Backend.LANCZOS
    assert cfg.model.value == "anime"
