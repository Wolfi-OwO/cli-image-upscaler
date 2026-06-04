# How it works

## The pipeline

```
load image ──▶ choose backend ──▶ upscale ──▶ resize to exact target ──▶ save
                    │
          ┌─────────┴──────────┐
          ▼                    ▼
   Real-ESRGAN (AI)      Lanczos (fallback)
```

1. **Load** the image with Pillow, preserving an alpha channel if present.
2. **Select a backend**. In `auto` mode the tool uses Real-ESRGAN when `torch` and
   `realesrgan` are importable, otherwise it falls back to Lanczos resampling.
3. **Upscale** (see below).
4. **Resize to the exact target** with Lanczos for any non-power-of-four factor.
5. **Save**, converting modes as needed for the chosen format (e.g. dropping alpha
   for JPEG).

## Reaching 2×, 4×, 8×, and 16×

Real-ESRGAN's networks upscale **4× natively**. The tool computes how many 4×
passes are required to reach (or exceed) the requested factor, then trims to the
exact size:

| Target | 4× passes | Final resize |
| ------ | --------- | ------------ |
| 2×     | 1 (→4×)   | ↓ to 2×      |
| 4×     | 1 (→4×)   | none         |
| 8×     | 2 (→16×)  | ↓ to 8×      |
| 16×    | 2 (→16×)  | none         |

Chaining the network (rather than asking it for an arbitrary scale in one shot)
lets each pass restore detail at its own resolution, which generally produces a
crisper result at 8× and 16× — at the cost of more compute.

```python
def _passes_for_scale(scale: int) -> int:
    return max(1, math.ceil(math.log(scale, 4)))
```

## Models

| Model | Network | Best for |
| ----- | ------- | -------- |
| `general` / `photo` | `RealESRGAN_x4plus` (23 RRDB blocks) | photographs, mixed real-world content |
| `anime` | `RealESRGAN_x4plus_anime_6B` (6 blocks) | anime, illustrations, line art |

With `--face-enhance`, faces are additionally restored by **GFPGAN**, which uses
the chosen Real-ESRGAN model as its background upsampler.

## Honest expectations

Super-resolution **reconstructs** plausible detail learned from training data; it
cannot recover information that was never present in the source. "16×" refers to a
16× increase in **pixel dimensions** (256×256 → 4096×4096) with AI-restored
sharpness — not a 16× increase in true optical fidelity. Heavily compressed,
blurry, or tiny inputs will improve, but won't become indistinguishable from a
native high-resolution capture.

## Why a Lanczos fallback?

The base package installs without PyTorch so it is small and quick to set up. The
Lanczos backend still gives high-quality classical resampling and guarantees the
CLI works everywhere — including CI — while AI super-resolution remains an opt-in
extra.
