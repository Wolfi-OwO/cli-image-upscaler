"""Exception hierarchy for image-upscaler."""

from __future__ import annotations


class ImageUpscalerError(Exception):
    """Base class for all image-upscaler errors."""


class UpscaleError(ImageUpscalerError):
    """Raised when an image cannot be upscaled."""


class UnsupportedScaleError(ImageUpscalerError):
    """Raised when an unsupported scale factor is requested."""


class ModelDownloadError(ImageUpscalerError):
    """Raised when model weights cannot be downloaded or located."""


class UnsupportedFormatError(ImageUpscalerError):
    """Raised when an input or output image format is not supported."""
