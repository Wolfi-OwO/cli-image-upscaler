# image-upscaler documentation

Free, AI-powered command-line image upscaling — up to 16× larger and sharper.

## Contents

- [Installation](installation.md) — install on PyPI, Docker, or from source; GPU setup.
- [Usage](usage.md) — full command reference, options, and recipes.
- [How it works](how-it-works.md) — the upscaling pipeline and the 16× chaining trick.
- [FAQ](faq.md) — common questions and troubleshooting.

## What is this?

`image-upscaler` enlarges images using the open-source
[Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) super-resolution networks.
Unlike a plain resize, it reconstructs plausible high-frequency detail — sharper
edges, cleaner text, smoother gradients — at 2×, 4×, 8×, or 16× the original
resolution.

It runs entirely on your machine. Nothing is uploaded, there are no watermarks,
no sign-up, and no usage limits.

## At a glance

```bash
pip install "image-upscaler[ai]"
upscale run photo.jpg -s 4
```

| | |
| --- | --- |
| **Scales** | 2×, 4×, 8×, 16× |
| **Models** | general, photo, anime |
| **Backends** | Real-ESRGAN (AI), Lanczos (fallback) |
| **Formats** | PNG, JPEG, WebP, BMP, TIFF |
| **Hardware** | CPU or NVIDIA GPU (CUDA) |
| **License** | MIT |
