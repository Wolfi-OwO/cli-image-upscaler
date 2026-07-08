<div align="center">

# image-upscaler

**Free, AI-powered command-line image upscaling — up to 16× larger and sharper.**

[![CI](https://github.com/Wolfi-OwO/cli-image-upscaler/actions/workflows/ci.yml/badge.svg)](https://github.com/Wolfi-OwO/cli-image-upscaler/actions/workflows/ci.yml)
[![Security](https://github.com/Wolfi-OwO/cli-image-upscaler/actions/workflows/security.yml/badge.svg)](https://github.com/Wolfi-OwO/cli-image-upscaler/actions/workflows/security.yml)
[![Docker](https://github.com/Wolfi-OwO/cli-image-upscaler/actions/workflows/docker.yml/badge.svg)](https://github.com/Wolfi-OwO/cli-image-upscaler/actions/workflows/docker.yml)
[![Docker Hub](https://img.shields.io/docker/v/wolfiowo/cli-image-upscaler?sort=semver&label=docker%20hub)](https://hub.docker.com/r/wolfiowo/cli-image-upscaler)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)

</div>

`image-upscaler` is a fast, scriptable CLI that enlarges images **2×, 4×, 8×, or 16×**
while recovering detail using the open-source [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)
super-resolution networks. It is 100% free, runs locally (no cloud, no upload, no
watermark), and falls back to high-quality Lanczos resampling when the AI stack
isn't installed.

---

## Features

- **Up to 16× upscaling** by chaining Real-ESRGAN's native 4× networks.
- **AI super-resolution** with general-purpose and anime/illustration models.
- **Optional face restoration** via GFPGAN (`--face-enhance`).
- **Batch mode** — point it at a folder and upscale everything (with `--recursive`).
- **Graceful fallback** — works out of the box with Lanczos if PyTorch isn't present.
- **Runs anywhere** — Linux, macOS, Windows; CPU or NVIDIA GPU.
- **Docker image** and **GitHub Actions** for reproducible, scanned builds.
- **Privacy-first** — your images never leave your machine.

## Quick start

```bash
# Install with the AI backend (recommended)
pip install "image-upscaler[ai]"

# Upscale a single photo 4×
upscale run photo.jpg -s 4

# Upscale a whole folder 8× into ./out
upscale run ./album -o ./out -s 8 --recursive

# 16× upscale of line art using the anime model
upscale run art.png -m anime -s 16 -f png
```

> 💡 The first AI run downloads the model weights (~64 MB) into
> `~/.cache/image-upscaler/` and reuses them afterwards.

Don't want to install the heavy ML stack? The base package still works:

```bash
pip install image-upscaler          # Lanczos backend only
upscale run photo.jpg -s 4 -b lanczos
```

## Installation

| Method      | Command                                                | Backend                                       |
| ----------- | ------------------------------------------------------ | --------------------------------------------- |
| PyPI (full) | `pip install "image-upscaler[ai]"`                     | Real-ESRGAN + Lanczos                         |
| PyPI (lite) | `pip install image-upscaler`                           | Lanczos only                                  |
| Docker      | `docker pull wolfiowo/cli-image-upscaler` (or `ghcr.io/wolfi-owo/cli-image-upscaler`) | Real-ESRGAN + Lanczos (`INSTALL_AI=false` → lean) |
| From source | `git clone … && pip install -e ".[ai]"`                | Real-ESRGAN + Lanczos                         |

See [docs/installation.md](docs/installation.md) for GPU setup and troubleshooting.

## Docker

```bash
# Build the image (includes the Real-ESRGAN AI backend by default)
docker build -t image-upscaler .

# ...or a lean Lanczos-only image (no PyTorch, much smaller)
docker build --build-arg INSTALL_AI=false -t image-upscaler:lite .

# Run — mount the current dir as /work, persist model weights in a volume
docker run --rm \
  -v "${PWD}:/work" \
  -v upscaler-weights:/home/app/.cache/image-upscaler/weights \
  image-upscaler run photo.jpg -s 4 --tile 512
```

Or with Compose:

```bash
docker compose run --rm upscaler run photo.jpg -s 4 --tile 512
```

## GPU (NVIDIA)

A CUDA GPU is **10–50× faster** and is used automatically (fp16). Install a
PyTorch build matching your card, then pass `--gpu-id 0`:

```bash
# RTX 50-series (Blackwell, e.g. RTX 5080) needs the cu128 channel:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
pip install "image-upscaler[ai]"
upscale run photo.jpg -s 4 --gpu-id 0
```

Docker on GPU (needs the NVIDIA Container Toolkit + `--gpus all`):

```bash
docker build --build-arg TORCH_CHANNEL=cu128 -t image-upscaler:cuda .
docker run --rm --gpus all -v "${PWD}:/work" \
  image-upscaler:cuda run photo.jpg -s 4 --gpu-id 0
```

> RTX 50-series requires `cu128` (CUDA 12.8); older `cu121`/`cu124` builds fail
> with "no kernel image available". See [docs/installation.md](docs/installation.md#gpu-acceleration-nvidia)
> for the full GPU/WSL2 guide and the per-generation channel table.

## Usage

```text
upscale run INPUT... [OPTIONS]

  -o, --output PATH      Output file (single input) or directory (many).
  -s, --scale INTEGER    Upscale factor: 2, 4, 8 or 16  [default: 4]
  -m, --model NAME       general | photo | anime        [default: general]
  -b, --backend NAME     auto | realesrgan | lanczos    [default: auto]
  -f, --format TEXT      Output format: png, jpg, webp…  (default: keep source)
  -q, --quality INTEGER  Quality for lossy formats (1-100)  [default: 95]
      --tile INTEGER     Tile size in px to bound memory  [default: 512; 0 = off]
      --face-enhance     Restore faces with GFPGAN
      --sharpen FLOAT    Unsharp-mask strength for a crisper finish (0 = off)
      --dpi INTEGER      Write DPI metadata (print size only; adds no detail)
      --fp32             Full precision (needed on most CPUs)
      --gpu-id INTEGER   GPU device index
  -r, --recursive        Recurse into input directories
      --overwrite        Overwrite existing outputs
      --no-download      Never download weights; fail if missing
  -v, --verbose          Verbose logging
      --quiet            Errors only
```

List models and check whether the AI backend is active:

```bash
upscale models
```

Full reference: [docs/usage.md](docs/usage.md).

## How does 16× work?

Real-ESRGAN's networks upscale **4× natively**. To reach higher factors the image
is passed through the network multiple times (4× → 16×) and resized to the exact
target with Lanczos for any in-between factor. This recovers far more detail than a
single naïve resize. Read more in [docs/how-it-works.md](docs/how-it-works.md).

> **A note on "16× better quality":** upscaling *reconstructs* plausible detail —
> it cannot invent information that was never captured. 16× means **16× the
> resolution** (pixel dimensions) with AI-restored sharpness, not 16× the optical
> fidelity of the original scene.

## Development

```bash
git clone https://github.com/Wolfi-OwO/cli-image-upscaler
cd cli-image-upscaler
make install        # editable install with dev tools
make check          # lint + type-check + tests
make test           # tests with coverage
make scan           # Trivy filesystem vulnerability scan
```

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

Dependencies and the Docker image are scanned with **Trivy** and **CodeQL** on every
push, PR, and weekly schedule. To report a vulnerability, see [SECURITY.md](SECURITY.md).

## Acknowledgements

- [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) by Xintao Wang et al.
- [GFPGAN](https://github.com/TencentARC/GFPGAN) for face restoration.
- [BasicSR](https://github.com/XPixelGroup/BasicSR), [Pillow](https://python-pillow.org/),
  [Typer](https://typer.tiangolo.com/) and [Rich](https://github.com/Textualize/rich).

## License

[MIT](LICENSE) © Phillip Kofler. The bundled model weights are downloaded at
runtime from their original authors and are governed by their respective licenses
(Real-ESRGAN & GFPGAN: BSD-3-Clause).
