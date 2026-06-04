"""Enable ``python -m image_upscaler``."""

from __future__ import annotations

from .cli import app


def main() -> None:
    app()


if __name__ == "__main__":
    main()
