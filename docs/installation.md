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
git clone https://github.com/Wolfi-OwO/cli-image-upscaler
cd cli-image-upscaler
pip install -e ".[ai]"     # or ".[dev,ai]" for development
```

## Docker

```bash
# Pull the published image (includes the Real-ESRGAN AI backend)
docker pull ghcr.io/wolfi-owo/cli-image-upscaler:latest

# Run — persist downloaded model weights in a named volume
docker run --rm \
  -v "${PWD}:/work" \
  -v upscaler-weights:/home/app/.cache/image-upscaler/weights \
  ghcr.io/wolfi-owo/cli-image-upscaler:latest run photo.jpg -s 4 --tile 512

# Or build a lean Lanczos-only image (no PyTorch)
docker build --build-arg INSTALL_AI=false -t image-upscaler:lite .
```

## GPU acceleration (NVIDIA)

A CUDA GPU is **10–50× faster** than CPU and the engine uses it automatically
(`torch.cuda.is_available()`), switching to fast fp16. You just need a
CUDA-enabled PyTorch.

### Pick the right CUDA channel

Install the PyTorch build that matches your GPU generation **before** installing
this package — the channel must support your card's compute capability:

| GPU generation | Example cards | PyTorch channel |
| -------------- | ------------- | --------------- |
| Blackwell (RTX 50-series, sm_120) | RTX 5090 / **5080** / 5070 | `cu128` (torch ≥ 2.7) |
| Ada / Ampere (RTX 40/30-series) | RTX 4090, 3080 | `cu124` or `cu121` |
| Turing (RTX 20-series) | RTX 2080 | `cu121` |

> ⚠️ Using an older channel (e.g. `cu121`) on an RTX 50-series card fails at
> runtime with `CUDA error: no kernel image is available for execution on the
> device`. Blackwell needs `cu128`.

### Native install (recommended for GPU)

```bash
# RTX 50-series (e.g. RTX 5080):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
pip install "image-upscaler[ai]"

# Verify the GPU is seen:
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"

upscale run photo.jpg -s 4 --gpu-id 0
```

On Windows this works either natively or inside WSL2 (with a recent NVIDIA
driver — the driver provides CUDA to WSL automatically; do **not** install a
separate CUDA toolkit in WSL).

### Docker with GPU

Requires the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
on the host (already available in Docker Desktop's WSL2 backend with a recent
NVIDIA driver). Build with a CUDA channel and run with `--gpus all`:

```bash
# Build a CUDA image for RTX 50-series
docker build --build-arg INSTALL_AI=true --build-arg TORCH_CHANNEL=cu128 \
  -t image-upscaler:cuda .

# Run on the GPU
docker run --rm --gpus all \
  -v "${PWD}:/work" \
  -v upscaler-weights:/home/app/.cache/image-upscaler/weights \
  image-upscaler:cuda run photo.jpg -s 4 --gpu-id 0 -b realesrgan -v
```

Or via Compose (the `upscaler-gpu` service defaults to `cu128`):

```bash
docker compose run --rm upscaler-gpu run photo.jpg -s 4 --gpu-id 0
```

Sanity-check that the container sees the GPU:

```bash
docker run --rm --gpus all image-upscaler:cuda \
  python -c "import torch; print(torch.cuda.is_available())"   # -> True
```

If you see `No CUDA device detected; using fp32 (CPU mode)` in the logs, the
container isn't getting the GPU — check `--gpus all` and the container toolkit.

### CPU notes

On CPU, the tool automatically uses fp32 (half precision is GPU-only). Expect
higher-resolution jobs to be slow; `--tile 512` keeps memory bounded.

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
