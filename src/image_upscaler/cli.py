"""Command-line interface for image-upscaler."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from . import __version__
from .exceptions import ImageUpscalerError
from .models import ModelName, resolve_model
from .upscaler import (
    SUPPORTED_SCALES,
    Backend,
    UpscaleConfig,
    Upscaler,
    realesrgan_available,
)
from .utils import default_output_path, iter_input_images

console = Console()
error_console = Console(stderr=True)

app = typer.Typer(
    name="upscale",
    help=(
        "Free, AI-powered image upscaling (up to 16x) using open-source "
        "Real-ESRGAN super-resolution models."
    ),
    add_completion=True,
    no_args_is_help=True,
    rich_markup_mode="rich",
)


def _configure_logging(verbose: bool, quiet: bool) -> None:
    level = logging.WARNING
    if verbose:
        level = logging.DEBUG
    elif quiet:
        level = logging.ERROR
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=error_console, show_path=False, rich_tracebacks=True)],
    )


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"image-upscaler [bold cyan]{__version__}[/]")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=_version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
) -> None:
    """image-upscaler — make your images up to 16x larger and sharper."""


@app.command()
def run(
    inputs: list[Path] = typer.Argument(
        ...,
        metavar="INPUT...",
        help="Image files or directories to upscale.",
        show_default=False,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file (single input) or directory (multiple inputs).",
    ),
    scale: int = typer.Option(
        4,
        "--scale",
        "-s",
        help=f"Upscale factor. One of: {', '.join(map(str, SUPPORTED_SCALES))}.",
    ),
    model: ModelName = typer.Option(
        ModelName.GENERAL,
        "--model",
        "-m",
        help="Model to use.",
        case_sensitive=False,
    ),
    backend: Backend = typer.Option(
        Backend.AUTO,
        "--backend",
        "-b",
        help="Upscaling backend. 'auto' prefers Real-ESRGAN, falls back to Lanczos.",
        case_sensitive=False,
    ),
    suffix: Optional[str] = typer.Option(
        None,
        "--suffix",
        help="Filename suffix for outputs (default: '_upscaled_<scale>x').",
    ),
    output_format: Optional[str] = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format/extension, e.g. png, jpg, webp (default: keep source).",
    ),
    quality: int = typer.Option(
        95, "--quality", "-q", min=1, max=100, help="Quality for lossy formats (1-100)."
    ),
    tile: int = typer.Option(
        512,
        "--tile",
        help="Tile size (px) to bound memory. 0 disables tiling (fastest/seamless "
        "but can exhaust RAM/VRAM on large images).",
    ),
    face_enhance: bool = typer.Option(
        False, "--face-enhance", help="Restore faces with GFPGAN (requires AI extras)."
    ),
    sharpen: float = typer.Option(
        0.0,
        "--sharpen",
        min=0.0,
        max=5.0,
        help="Unsharp-mask strength for a crisper finish (0 = off, ~1.0 subtle, ~2.0 strong).",
    ),
    dpi: Optional[int] = typer.Option(
        None,
        "--dpi",
        help="Write DPI metadata into the output (print size only; does not add detail).",
    ),
    fp32: bool = typer.Option(
        False, "--fp32", help="Use full fp32 precision (slower, needed on most CPUs)."
    ),
    gpu_id: Optional[int] = typer.Option(
        None, "--gpu-id", help="GPU device index to use (default: auto)."
    ),
    recursive: bool = typer.Option(
        False, "--recursive", "-r", help="Recurse into input directories."
    ),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing output files."),
    no_download: bool = typer.Option(
        False, "--no-download", help="Never download model weights; fail if missing."
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging."),
    quiet: bool = typer.Option(False, "--quiet", help="Only log errors."),
) -> None:
    """Upscale one or more images.

    [bold]Examples[/]

      upscale run photo.jpg -s 4
      upscale run ./album -o ./out -s 8 --recursive
      upscale run art.png -m anime -s 16 -f png
    """
    _configure_logging(verbose, quiet)

    try:
        config = UpscaleConfig(
            scale=scale,
            model=model,
            backend=backend,
            tile=tile,
            face_enhance=face_enhance,
            sharpen=sharpen,
            dpi=dpi,
            fp32=fp32,
            gpu_id=gpu_id,
            download=not no_download,
        )
    except ImageUpscalerError as exc:
        error_console.print(f"[bold red]error:[/] {exc}")
        raise typer.Exit(code=2) from exc

    images = list(iter_input_images(inputs, recursive=recursive))
    if not images:
        error_console.print("[bold red]error:[/] no supported images found in input.")
        raise typer.Exit(code=1)

    output_is_dir = output is not None and (
        output.is_dir() or len(images) > 1 or output.suffix == ""
    )
    if output is not None and output_is_dir:
        output.mkdir(parents=True, exist_ok=True)

    upscaler = Upscaler(config)
    chosen = upscaler.backend
    if not quiet:
        console.print(
            f"Upscaling [bold]{len(images)}[/] image(s) "
            f"[cyan]{scale}x[/] with backend [magenta]{chosen}[/] "
            f"(model: [green]{model.value}[/])."
        )

    failures = 0
    for index, source in enumerate(images, start=1):
        if output is None:
            destination = default_output_path(
                source, scale=scale, suffix=suffix, output_format=output_format
            )
        elif output_is_dir:
            destination = default_output_path(
                source,
                scale=scale,
                output_dir=output,
                suffix=suffix,
                output_format=output_format,
            )
        else:
            destination = output

        if destination.exists() and not overwrite:
            error_console.print(f"[yellow]skip[/] {destination} already exists (use --overwrite).")
            continue

        try:
            with console.status(
                f"[{index}/{len(images)}] {source.name} -> {destination.name}",
                spinner="dots",
            ):
                upscaler.upscale_file(source, destination, quality=quality)
        except ImageUpscalerError as exc:
            failures += 1
            error_console.print(f"[bold red]failed[/] {source}: {exc}")
            continue
        if not quiet:
            console.print(f"[green]ok[/] {source.name} -> {destination}")

    if failures:
        error_console.print(f"[bold red]{failures} image(s) failed.[/]")
        raise typer.Exit(code=1)


@app.command("models")
def list_models() -> None:
    """List available models and the active backend."""
    table = Table(title="Available models", show_lines=False)
    table.add_column("Name", style="bold cyan")
    table.add_column("Weights")
    table.add_column("Description")
    for name in ModelName:
        spec = resolve_model(name)
        table.add_row(name.value, spec.filename, spec.description)
    console.print(table)

    available = realesrgan_available()
    status = "[green]available[/]" if available else "[yellow]not installed[/]"
    console.print(f"\nReal-ESRGAN backend: {status}")
    if not available:
        console.print(
            "Install AI extras for super-resolution: " "[bold]pip install 'image-upscaler[ai]'[/]"
        )


def app_main() -> None:  # pragma: no cover - console-script entry point
    app()


if __name__ == "__main__":  # pragma: no cover
    app()
