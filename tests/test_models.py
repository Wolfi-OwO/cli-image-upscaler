"""Tests for the model registry and weight cache."""

from __future__ import annotations

from pathlib import Path

import pytest

from image_upscaler.exceptions import ModelDownloadError
from image_upscaler.models import (
    MODEL_REGISTRY,
    ModelName,
    cache_dir,
    ensure_weights,
    resolve_model,
)


def test_every_model_has_a_spec() -> None:
    for name in ModelName:
        spec = resolve_model(name)
        assert spec.filename.endswith(".pth")
        assert spec.url.startswith("https://")
        assert spec.scale == 4


def test_resolve_model_from_string() -> None:
    assert resolve_model("anime") is MODEL_REGISTRY[ModelName.ANIME]


def test_resolve_unknown_model_raises() -> None:
    with pytest.raises(ModelDownloadError):
        resolve_model("does-not-exist")


def test_cache_dir_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IMAGE_UPSCALER_CACHE", str(tmp_path / "weights"))
    assert cache_dir() == tmp_path / "weights"
    assert cache_dir().exists()


def test_ensure_weights_no_download_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IMAGE_UPSCALER_CACHE", str(tmp_path))
    with pytest.raises(ModelDownloadError):
        ensure_weights(resolve_model(ModelName.GENERAL), download=False)


def test_ensure_weights_returns_cached_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("IMAGE_UPSCALER_CACHE", str(tmp_path))
    spec = resolve_model(ModelName.GENERAL)
    (tmp_path / spec.filename).write_bytes(b"fake-weights")
    assert ensure_weights(spec, download=False) == tmp_path / spec.filename
