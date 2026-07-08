# Usage

```text
upscale [--version] COMMAND [ARGS]

Commands:
  run      Upscale one or more images.
  models   List available models and the active backend.
```

## `upscale run`

```text
upscale run INPUT... [OPTIONS]
```

`INPUT...` may be one or more image files **and/or** directories. Directories are
scanned for supported images (`--recursive` to descend into subfolders).

### Options

| Option | Default | Description |
| ------ | ------- | ----------- |
| `-o, --output PATH` | next to source | Output file (single input) or directory (many inputs). |
| `-s, --scale INTEGER` | `4` | Upscale factor: `2`, `4`, `8`, or `16`. |
| `-m, --model NAME` | `general` | `general`, `photo`, or `anime`. |
| `-b, --backend NAME` | `auto` | `auto`, `realesrgan`, or `lanczos`. |
| `-f, --format TEXT` | keep source | Output extension, e.g. `png`, `jpg`, `webp`. |
| `-q, --quality INTEGER` | `95` | Quality for lossy formats (1–100). |
| `--suffix TEXT` | `_upscaled_<scale>x` | Filename suffix for generated outputs. |
| `--tile INTEGER` | `512` | Tile size (px) to bound memory. `0` disables tiling (fastest/seamless, but can exhaust RAM/VRAM on large images). |
| `--face-enhance` | off | Restore faces with GFPGAN. |
| `--sharpen FLOAT` | `0.0` | Unsharp-mask strength for a crisper finish (0 = off, ~1.0 subtle, ~2.0 strong). |
| `--dpi INTEGER` | none | Write DPI metadata into the output. Affects print size only — **does not add pixels or visible detail**. |
| `--fp32` | off | Full precision (required on most CPUs). |
| `--gpu-id INTEGER` | auto | GPU device index. |
| `-r, --recursive` | off | Recurse into input directories. |
| `--overwrite` | off | Overwrite existing output files. |
| `--no-download` | off | Never download weights; fail if missing. |
| `-v, --verbose` | off | Verbose (debug) logging. |
| `--quiet` | off | Only log errors. |

### Output naming

- **Single input, no `-o`** → written beside the source as
  `name_upscaled_4x.ext`.
- **Single input, `-o file.png`** → written exactly to `file.png`.
- **Multiple inputs or a directory `-o`** → each result is written into the output
  directory using the default naming.

## Recipes

Upscale a photo 4× (AI, auto backend):

```bash
upscale run photo.jpg -s 4
```

Maximum 16× enlargement, force the AI backend, save as PNG:

```bash
upscale run photo.jpg -s 16 -b realesrgan -f png
```

Batch-process a folder recursively into `./out` at 8×:

```bash
upscale run ./photos -o ./out -s 8 --recursive --overwrite
```

Anime / illustration art with face restoration:

```bash
upscale run drawing.png -m anime -s 4 --face-enhance
```

CPU-only machine (no GPU):

```bash
upscale run photo.jpg -s 4 --fp32
```

Low-memory GPU (tile the image):

```bash
upscale run huge.png -s 4 --tile 256 --gpu-id 0
```

Offline / locked-down (pre-seeded weights, no network):

```bash
IMAGE_UPSCALER_CACHE=/opt/weights upscale run photo.jpg -s 4 --no-download
```

## Exit codes

| Code | Meaning |
| ---- | ------- |
| `0` | Success. |
| `1` | No images found, or one or more images failed. |
| `2` | Invalid options (e.g. unsupported scale). |

## `upscale models`

Prints the model table and reports whether the Real-ESRGAN backend is importable:

```bash
upscale models
```
