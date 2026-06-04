"""image-upscaler — free, AI-powered command-line image upscaling.

Upscale images up to 16x using open-source Real-ESRGAN super-resolution models,
with a high-quality Lanczos fallback when ML dependencies are unavailable.
"""

from __future__ import annotations

from .exceptions import (
    ImageUpscalerError,
    ModelDownloadError,
    UnsupportedScaleError,
    UpscaleError,
)
from .models import MODEL_REGISTRY, ModelName
from .upscaler import Backend, UpscaleConfig, Upscaler

__all__ = [
    "Backend",
    "ImageUpscalerError",
    "MODEL_REGISTRY",
    "ModelDownloadError",
    "ModelName",
    "UnsupportedScaleError",
    "UpscaleConfig",
    "UpscaleError",
    "Upscaler",
    "__version__",
]

__version__ = "0.1.0"
