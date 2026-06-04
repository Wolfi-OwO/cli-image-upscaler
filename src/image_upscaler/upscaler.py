"""Core upscaling engine with Real-ESRGAN and Lanczos backends."""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from pathlib import Path
from typing import Any

from PIL import Image

from .exceptions import UnsupportedScaleError, UpscaleError
from .models import (
    ModelName,
    ModelSpec,
    ensure_gfpgan,
    ensure_weights,
    resolve_model,
)
from .utils import load_image, save_image

logger = logging.getLogger(__name__)

#: Scale factors the CLI accepts.
SUPPORTED_SCALES: tuple[int, ...] = (2, 4, 8, 16)

#: Native scale of the Real-ESRGAN x4 networks.
NATIVE_SCALE = 4


class Backend(str, Enum):
    """Available upscaling backends.

    ``AUTO`` prefers Real-ESRGAN and falls back to Lanczos when the optional
    ML stack (``torch`` + ``realesrgan``) is not importable.
    """

    AUTO = "auto"
    REALESRGAN = "realesrgan"
    LANCZOS = "lanczos"

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return self.value


@dataclass
class UpscaleConfig:
    """Configuration for an :class:`Upscaler` run."""

    scale: int = 4
    model: ModelName = ModelName.GENERAL
    backend: Backend = Backend.AUTO
    tile: int = 0
    tile_pad: int = 10
    pre_pad: int = 0
    face_enhance: bool = False
    fp32: bool = False
    gpu_id: int | None = None
    download: bool = True

    def __post_init__(self) -> None:
        if self.scale not in SUPPORTED_SCALES:
            allowed = ", ".join(str(s) for s in SUPPORTED_SCALES)
            raise UnsupportedScaleError(
                f"Scale {self.scale}x is not supported. Choose one of: {allowed}."
            )
        if isinstance(self.model, str):
            self.model = ModelName(self.model)
        if isinstance(self.backend, str):
            self.backend = Backend(self.backend)


def realesrgan_available() -> bool:
    """Return ``True`` when the Real-ESRGAN backend can be imported."""
    try:  # pragma: no cover - depends on optional deps being installed
        import torch  # noqa: F401
        from realesrgan import RealESRGANer  # noqa: F401

        return True
    except Exception:  # noqa: BLE001
        return False


def _passes_for_scale(scale: int) -> int:
    """Number of native 4x passes needed to reach at least ``scale``."""
    return max(1, math.ceil(math.log(scale, NATIVE_SCALE)))


class Upscaler:
    """Upscale images using the configured backend.

    The same instance can process many images; heavy model initialisation is
    performed lazily and cached on first use.
    """

    def __init__(self, config: UpscaleConfig | None = None) -> None:
        self.config = config or UpscaleConfig()
        self._spec: ModelSpec = resolve_model(self.config.model)

    # -- backend selection -------------------------------------------------
    @cached_property
    def backend(self) -> Backend:
        """The concrete backend that will actually be used."""
        if self.config.backend is Backend.LANCZOS:
            return Backend.LANCZOS
        if self.config.backend is Backend.REALESRGAN:
            if not realesrgan_available():
                raise UpscaleError(
                    "Backend 'realesrgan' requested but torch/realesrgan are not "
                    "installed. Install extras with: pip install 'image-upscaler[ai]'."
                )
            return Backend.REALESRGAN
        # AUTO
        if realesrgan_available():
            return Backend.REALESRGAN
        logger.warning(
            "Real-ESRGAN backend unavailable; falling back to Lanczos resampling. "
            "Install 'image-upscaler[ai]' for AI super-resolution."
        )
        return Backend.LANCZOS

    # -- public API --------------------------------------------------------
    def upscale_image(self, image: Image.Image) -> Image.Image:
        """Return an upscaled copy of ``image``."""
        if self.backend is Backend.REALESRGAN:
            return self._upscale_realesrgan(image)
        return self._upscale_lanczos(image)

    def upscale_file(self, source: Path, destination: Path, *, quality: int = 95) -> Path:
        """Upscale ``source`` and write the result to ``destination``."""
        image = load_image(source)
        result = self.upscale_image(image)
        save_image(result, destination, quality=quality)
        return destination

    # -- Lanczos backend ---------------------------------------------------
    def _upscale_lanczos(self, image: Image.Image) -> Image.Image:
        target = (image.width * self.config.scale, image.height * self.config.scale)
        return image.resize(target, Image.LANCZOS)

    # -- Real-ESRGAN backend ----------------------------------------------
    def _upscale_realesrgan(self, image: Image.Image) -> Image.Image:  # pragma: no cover
        import numpy as np

        upsampler = self._upsampler
        has_alpha = image.mode in ("RGBA", "LA")
        rgb = image.convert("RGBA" if has_alpha else "RGB")

        # Real-ESRGAN (cv2 convention) operates on BGR(A) ordering. The swap is
        # its own inverse, so the same helper converts to and from BGR.
        def swap_rb(a):
            return a[:, :, [2, 1, 0, 3]] if has_alpha else a[:, :, ::-1]

        arr = swap_rb(np.array(rgb))
        passes = _passes_for_scale(self.config.scale)
        try:
            if self.config.face_enhance:
                arr = self._enhance_faces(arr)
                passes -= 1  # face enhancer already applies one 4x pass
            for _ in range(max(passes, 0)):
                arr, _mode = upsampler.enhance(arr, outscale=NATIVE_SCALE)
        except Exception as exc:  # noqa: BLE001
            raise UpscaleError(f"Real-ESRGAN failed: {exc}") from exc

        result = Image.fromarray(swap_rb(arr))

        target = (image.width * self.config.scale, image.height * self.config.scale)
        if result.size != target:
            result = result.resize(target, Image.LANCZOS)
        return result

    @cached_property
    def _upsampler(self) -> Any:  # pragma: no cover - requires optional deps
        from basicsr.archs.rrdbnet_arch import RRDBNet
        from realesrgan import RealESRGANer

        spec = self._spec
        model = RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=spec.num_feat,
            num_block=spec.num_block,
            num_grow_ch=spec.num_grow_ch,
            scale=spec.scale,
        )
        weights = ensure_weights(spec, download=self.config.download)
        return RealESRGANer(
            scale=spec.scale,
            model_path=str(weights),
            model=model,
            tile=self.config.tile,
            tile_pad=self.config.tile_pad,
            pre_pad=self.config.pre_pad,
            half=not self.config.fp32,
            gpu_id=self.config.gpu_id,
        )

    def _enhance_faces(self, arr: Any) -> Any:  # pragma: no cover - optional deps
        from gfpgan import GFPGANer

        weights = ensure_gfpgan(download=self.config.download)
        restorer = GFPGANer(
            model_path=str(weights),
            upscale=NATIVE_SCALE,
            arch="clean",
            channel_multiplier=2,
            bg_upsampler=self._upsampler,
        )
        _, _, output = restorer.enhance(
            arr, has_aligned=False, only_center_face=False, paste_back=True
        )
        return output
