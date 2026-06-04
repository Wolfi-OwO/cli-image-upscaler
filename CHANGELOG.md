# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/koflerphillip/cli-image-upscaler/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/koflerphillip/cli-image-upscaler/releases/tag/v0.1.0
