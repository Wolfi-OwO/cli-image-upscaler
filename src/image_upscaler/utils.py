"""Filesystem and image I/O helpers."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

from PIL import Image

from .exceptions import UnsupportedFormatError

# Formats Pillow can reliably read and write for this tool.
SUPPORTED_INPUT_SUFFIXES: frozenset[str] = frozenset(
    {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
)

# Map an input suffix to a sensible default output format/suffix.
_LOSSLESS_OUTPUT = ".png"


def is_supported_image(path: Path) -> bool:
    """Return ``True`` if ``path`` looks like a supported image file."""
    return path.suffix.lower() in SUPPORTED_INPUT_SUFFIXES


def iter_input_images(inputs: Iterable[Path], *, recursive: bool = False) -> Iterator[Path]:
    """Expand a list of files, directories and globs into image paths.

    Directories are scanned (recursively when ``recursive`` is set). Duplicate
    paths are removed while preserving discovery order.
    """
    seen: set[Path] = set()
    for raw in inputs:
        candidates: Iterable[Path]
        if raw.is_dir():
            pattern = "**/*" if recursive else "*"
            candidates = sorted(raw.glob(pattern))
        else:
            candidates = [raw]
        for candidate in candidates:
            if candidate.is_file() and is_supported_image(candidate):
                resolved = candidate.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    yield candidate


def load_image(path: Path) -> Image.Image:
    """Open an image, preserving alpha where present."""
    try:
        image = Image.open(path)
        image.load()
    except Exception as exc:  # noqa: BLE001
        raise UnsupportedFormatError(f"Cannot read image '{path}': {exc}") from exc
    if image.mode not in ("RGB", "RGBA", "L", "LA"):
        image = image.convert("RGBA" if "A" in image.mode else "RGB")
    return image


def default_output_path(
    source: Path,
    *,
    scale: int,
    output_dir: Path | None = None,
    suffix: str | None = None,
    output_format: str | None = None,
) -> Path:
    """Compute an output path for an upscaled image.

    By default writes ``name_upscaled_4x.png`` next to the source.
    """
    stem_suffix = suffix if suffix is not None else f"_upscaled_{scale}x"
    extension = (
        f".{output_format.lower().lstrip('.')}"
        if output_format
        else source.suffix or _LOSSLESS_OUTPUT
    )
    target_dir = output_dir if output_dir is not None else source.parent
    return target_dir / f"{source.stem}{stem_suffix}{extension}"


def save_image(image: Image.Image, path: Path, *, quality: int = 95) -> None:
    """Save ``image`` to ``path``, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    params: dict[str, Any] = {}
    if suffix in (".jpg", ".jpeg"):
        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGB")
        params.update(quality=quality, optimize=True)
    elif suffix == ".webp":
        params.update(quality=quality, method=6)
    elif suffix == ".png":
        params.update(optimize=True)
    image.save(path, **params)
