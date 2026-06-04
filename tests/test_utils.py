"""Tests for filesystem and image I/O helpers."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from image_upscaler.utils import (
    default_output_path,
    is_supported_image,
    iter_input_images,
    load_image,
    save_image,
)


def test_is_supported_image() -> None:
    assert is_supported_image(Path("a.PNG"))
    assert is_supported_image(Path("a.jpeg"))
    assert not is_supported_image(Path("a.txt"))
    assert not is_supported_image(Path("a.gif"))


def test_iter_input_images_dir_and_dedup(tmp_path: Path) -> None:
    (tmp_path / "a.png").write_bytes(b"")
    (tmp_path / "b.jpg").write_bytes(b"")
    (tmp_path / "note.txt").write_text("ignore me")
    Image.new("RGB", (2, 2)).save(tmp_path / "a.png")
    Image.new("RGB", (2, 2)).save(tmp_path / "b.jpg")

    found = list(iter_input_images([tmp_path, tmp_path / "a.png"]))
    names = sorted(p.name for p in found)
    assert names == ["a.png", "b.jpg"]


def test_iter_input_images_recursive(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    Image.new("RGB", (2, 2)).save(nested / "deep.png")
    assert list(iter_input_images([tmp_path], recursive=False)) == []
    assert [p.name for p in iter_input_images([tmp_path], recursive=True)] == ["deep.png"]


def test_default_output_path_default_suffix() -> None:
    out = default_output_path(Path("/x/photo.jpg"), scale=4)
    assert out.name == "photo_upscaled_4x.jpg"


def test_default_output_path_custom_format_and_dir(tmp_path: Path) -> None:
    out = default_output_path(Path("photo.jpg"), scale=8, output_dir=tmp_path, output_format="png")
    assert out == tmp_path / "photo_upscaled_8x.png"


def test_load_and_save_jpeg_drops_alpha(tmp_path: Path) -> None:
    src = tmp_path / "rgba.png"
    Image.new("RGBA", (4, 4), (1, 2, 3, 4)).save(src)
    image = load_image(src)
    dest = tmp_path / "out.jpg"
    save_image(image, dest)
    with Image.open(dest) as result:
        assert result.mode == "RGB"
