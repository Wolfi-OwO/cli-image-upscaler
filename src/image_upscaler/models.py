"""Model registry and weight management for Real-ESRGAN backends."""

from __future__ import annotations

import logging
import os
import urllib.request
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .exceptions import ModelDownloadError

logger = logging.getLogger(__name__)


class ModelName(str, Enum):
    """Selectable upscaling models."""

    GENERAL = "general"
    PHOTO = "photo"
    ANIME = "anime"

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return self.value


@dataclass(frozen=True)
class ModelSpec:
    """Metadata describing a Real-ESRGAN model and its weights."""

    name: str
    filename: str
    url: str
    scale: int
    num_block: int
    description: str
    # RRDBNet architecture parameters.
    num_feat: int = 64
    num_grow_ch: int = 32


# Official Real-ESRGAN release weights (xinntao/Real-ESRGAN).
MODEL_REGISTRY: dict[ModelName, ModelSpec] = {
    ModelName.GENERAL: ModelSpec(
        name="RealESRGAN_x4plus",
        filename="RealESRGAN_x4plus.pth",
        url=(
            "https://github.com/xinntao/Real-ESRGAN/releases/download/"
            "v0.1.0/RealESRGAN_x4plus.pth"
        ),
        scale=4,
        num_block=23,
        description="General-purpose 4x model. Best default for photos and mixed content.",
    ),
    # "photo" is an ergonomic alias for the general model.
    ModelName.PHOTO: ModelSpec(
        name="RealESRGAN_x4plus",
        filename="RealESRGAN_x4plus.pth",
        url=(
            "https://github.com/xinntao/Real-ESRGAN/releases/download/"
            "v0.1.0/RealESRGAN_x4plus.pth"
        ),
        scale=4,
        num_block=23,
        description="Alias of 'general', tuned naming for real-world photography.",
    ),
    ModelName.ANIME: ModelSpec(
        name="RealESRGAN_x4plus_anime_6B",
        filename="RealESRGAN_x4plus_anime_6B.pth",
        url=(
            "https://github.com/xinntao/Real-ESRGAN/releases/download/"
            "v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth"
        ),
        scale=4,
        num_block=6,
        description="Compact 6-block model optimised for anime / illustration art.",
    ),
}

GFPGAN_URL = "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth"
GFPGAN_FILENAME = "GFPGANv1.3.pth"


def resolve_model(model: ModelName | str) -> ModelSpec:
    """Return the :class:`ModelSpec` for a model name."""
    if isinstance(model, str):
        try:
            model = ModelName(model)
        except ValueError as exc:
            valid = ", ".join(m.value for m in ModelName)
            raise ModelDownloadError(f"Unknown model '{model}'. Choose one of: {valid}.") from exc
    return MODEL_REGISTRY[model]


def cache_dir() -> Path:
    """Directory used to store downloaded model weights.

    Override with the ``IMAGE_UPSCALER_CACHE`` environment variable.
    """
    override = os.environ.get("IMAGE_UPSCALER_CACHE")
    if override:
        path = Path(override).expanduser()
    else:
        path = Path.home() / ".cache" / "image-upscaler" / "weights"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _download(url: str, destination: Path) -> Path:
    """Download ``url`` to ``destination`` atomically."""
    logger.info("Downloading model weights from %s", url)
    tmp = destination.with_suffix(destination.suffix + ".part")
    try:
        with urllib.request.urlopen(url) as response, tmp.open("wb") as handle:  # noqa: S310
            while chunk := response.read(1 << 20):
                handle.write(chunk)
        tmp.replace(destination)
    except Exception as exc:  # noqa: BLE001 - re-raised as domain error
        tmp.unlink(missing_ok=True)
        raise ModelDownloadError(f"Failed to download weights from {url}: {exc}") from exc
    return destination


def ensure_weights(spec: ModelSpec, *, download: bool = True) -> Path:
    """Return a local path to the weights for ``spec``, downloading if needed."""
    target = cache_dir() / spec.filename
    if target.exists():
        return target
    if not download:
        raise ModelDownloadError(
            f"Weights '{spec.filename}' not found in cache and downloads are disabled."
        )
    return _download(spec.url, target)


def ensure_gfpgan(*, download: bool = True) -> Path:
    """Return a local path to GFPGAN face-restoration weights."""
    target = cache_dir() / GFPGAN_FILENAME
    if target.exists():
        return target
    if not download:
        raise ModelDownloadError("GFPGAN weights not found and downloads are disabled.")
    return _download(GFPGAN_URL, target)
