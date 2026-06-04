"""End-to-end tests for the Typer CLI (Lanczos backend)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from typer.testing import CliRunner

from image_upscaler import __version__
from image_upscaler.cli import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_models_command() -> None:
    result = runner.invoke(app, ["models"])
    assert result.exit_code == 0
    assert "general" in result.stdout
    assert "anime" in result.stdout


def test_run_single_image(sample_image: Path, tmp_path: Path) -> None:
    out = tmp_path / "result.png"
    result = runner.invoke(
        app,
        ["run", str(sample_image), "-o", str(out), "-s", "2", "-b", "lanczos"],
    )
    assert result.exit_code == 0, result.stdout
    assert out.exists()
    with Image.open(out) as img:
        assert img.size == (32, 24)


def test_run_directory_to_output_dir(tmp_path: Path) -> None:
    src_dir = tmp_path / "in"
    src_dir.mkdir()
    Image.new("RGB", (4, 4)).save(src_dir / "one.png")
    Image.new("RGB", (4, 4)).save(src_dir / "two.png")
    out_dir = tmp_path / "out"

    result = runner.invoke(
        app,
        ["run", str(src_dir), "-o", str(out_dir), "-s", "4", "-b", "lanczos"],
    )
    assert result.exit_code == 0, result.stdout
    produced = sorted(p.name for p in out_dir.glob("*.png"))
    assert produced == ["one_upscaled_4x.png", "two_upscaled_4x.png"]


def test_run_rejects_unsupported_scale(sample_image: Path) -> None:
    result = runner.invoke(app, ["run", str(sample_image), "-s", "3", "-b", "lanczos"])
    assert result.exit_code == 2


def test_run_no_images_found(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    result = runner.invoke(app, ["run", str(empty), "-b", "lanczos"])
    assert result.exit_code == 1


def test_run_skips_existing_without_overwrite(sample_image: Path, tmp_path: Path) -> None:
    out = tmp_path / "exists.png"
    out.write_bytes(b"x")
    result = runner.invoke(app, ["run", str(sample_image), "-o", str(out), "-b", "lanczos"])
    assert result.exit_code == 0
    # File left untouched because it already existed.
    assert out.read_bytes() == b"x"
