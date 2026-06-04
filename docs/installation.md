# Installation

## Requirements

- Python **3.9+**
- ~2 GB free disk for the AI backend (PyTorch + model weights)
- Optional: an NVIDIA GPU with CUDA for much faster processing

## PyPI

The recommended install includes the Real-ESRGAN AI backend:

```bash
pip install "image-upscaler[ai]"
```

A lighter install ships only the Lanczos backend (no PyTorch):

```bash
pip install image-upscaler
```

Verify:

```bash
upscale --version
upscale models      # shows whether the AI backend is active
```

## From source

```bash
git clone https://github.com/koflerphillip/cli-image-upscaler
cd cli-image-upscaler
pip install -e ".[ai]"     # or ".[dev,ai]" for development
```

## Docker

```bash
# Pull the published image (includes the Real-ESRGAN AI backend)
docker pull ghcr.io/koflerphillip/cli-image-upscaler:latest

# Run — persist downloaded model weights in a named volume
docker run --rm \
  -v "${PWD}:/work" \
  -v upscaler-weights:/home/app/.cache/image-upscaler/weights \
  ghcr.io/koflerphillip/cli-image-upscaler:latest run photo.jpg -s 4 --tile 512

# Or build a lean Lanczos-only image (no PyTorch)
docker build --build-arg INSTALL_AI=false -t image-upscaler:lite .
```

## GPU acceleration

The AI extras install the default PyTorch build. For an NVIDIA GPU, install a
CUDA-enabled PyTorch matching your driver **before** installing this package:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install "image-upscaler[ai]"
```

Then pass `--gpu-id 0`. On CPU, add `--fp32` (half precision is GPU-only) and
expect higher-resolution jobs to take noticeably longer; `--tile 512` helps when
memory is tight.

## Model weights

On first AI use, weights are downloaded from the official Real-ESRGAN/GFPGAN
releases into:

- `~/.cache/image-upscaler/weights/` (default), or
- the directory set in the `IMAGE_UPSCALER_CACHE` environment variable.

| File | Size | Used by |
| ---- | ---- | ------- |
| `RealESRGAN_x4plus.pth` | ~64 MB | `general`, `photo` |
| `RealESRGAN_x4plus_anime_6B.pth` | ~18 MB | `anime` |
| `GFPGANv1.3.pth` | ~333 MB | `--face-enhance` |

Use `--no-download` to forbid downloads (fails if weights are missing) — useful in
air-gapped or CI environments where you pre-seed the cache.

## Troubleshooting

- **`Backend 'realesrgan' requested but torch/realesrgan are not installed`** —
  install the AI extras: `pip install "image-upscaler[ai]"`.
- **`basicsr` import error mentioning `functional_tensor`** — a known
  incompatibility with newer `torchvision`. Pin `torchvision<0.17` or apply the
  upstream BasicSR patch. See [FAQ](faq.md).
- **Out-of-memory on GPU** — lower `--tile` (e.g. `--tile 256`) or use a smaller scale.
