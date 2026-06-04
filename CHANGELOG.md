# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Docker images now build with the Real-ESRGAN **AI backend by default**. Build
  with `--build-arg INSTALL_AI=false` for a lean Lanczos-only image.

### Fixed

- Docker `[ai]` build failure caused by the shell parsing `*.whl[ai]` as a glob.
- Real-ESRGAN backend silently falling back to Lanczos on modern torchvision
  (added a `functional_tensor` compatibility shim for `basicsr`).
- Half-precision crash on CPU (`not implemented for Half`) — fp32 is now selected
  automatically when no CUDA device is present.
- Added `torchvision` to the `ai` extra and pinned `numpy<2` for `basicsr`.
- `Permission denied` writing model weights when a named volume is mounted at the
  Docker cache path: the weights cache is now pre-created and owned by the `app`
  user so a fresh volume inherits writable ownership.

## [0.1.0] - 2026-06-04

### Added

- Initial release of `image-upscaler`.
- CLI (`upscale`) with `run` and `models` commands.
- Real-ESRGAN backend with `general`, `photo`, and `anime` models.
- 2×, 4×, 8×, and 16× upscaling via network chaining.
- Optional GFPGAN face restoration (`--face-enhance`).
- High-quality Lanczos fallback backend.
- Batch / recursive directory processing.
- Multi-stage Dockerfile and `docker-compose.yml`.
- GitHub Actions: CI (lint, type-check, test matrix, build), Docker build &
  push to GHCR, Trivy + CodeQL security scanning, and PyPI release.
- Full documentation under `docs/`.

[Unreleased]: https://github.com/Wolfi-OwO/cli-image-upscaler/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Wolfi-OwO/cli-image-upscaler/releases/tag/v0.1.0
