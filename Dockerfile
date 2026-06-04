# syntax=docker/dockerfile:1.7
#
# Multi-stage build for image-upscaler.
#
# By default this produces a full image with the Real-ESRGAN AI backend
# (CPU PyTorch). For a lean Lanczos-only image (much smaller, no PyTorch):
#
#   docker build --build-arg INSTALL_AI=false -t image-upscaler:lite .
#
# -----------------------------------------------------------------------------
# Stage 1 — build the wheel
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build
RUN pip install --no-cache-dir build

COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m build --wheel --outdir /dist

# -----------------------------------------------------------------------------
# Stage 2 — runtime
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

ARG INSTALL_AI=true

# OCI image metadata (overridden by CI with real values).
LABEL org.opencontainers.image.title="image-upscaler" \
      org.opencontainers.image.description="Free AI-powered CLI to upscale images up to 16x." \
      org.opencontainers.image.source="https://github.com/koflerphillip/cli-image-upscaler" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    IMAGE_UPSCALER_CACHE=/home/app/.cache/image-upscaler/weights

# Runtime libraries needed by Pillow / OpenCV (used by Real-ESRGAN).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libjpeg62-turbo \
        zlib1g \
        libpng16-16 \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create an unprivileged user.
RUN useradd --create-home --uid 10001 app

COPY --from=builder /dist/*.whl /tmp/

# Resolve the wheel filename first: a glob like `/tmp/*.whl[ai]` is parsed by the
# shell as a character class, so the extras must be appended to the real path.
RUN WHEEL="$(ls /tmp/image_upscaler-*.whl)" \
    && if [ "$INSTALL_AI" = "true" ]; then \
        # Install CPU-only torch/torchvision first so the heavy CUDA wheels from
        # PyPI are never pulled in by the AI extras.
        pip install --no-cache-dir torch torchvision \
            --index-url https://download.pytorch.org/whl/cpu \
        && pip install --no-cache-dir "${WHEEL}[ai]"; \
    else \
        pip install --no-cache-dir "${WHEEL}"; \
    fi \
    && rm -f /tmp/*.whl

USER app
WORKDIR /work

# `/work` is the bind-mount point for the host's images.
VOLUME ["/work"]

ENTRYPOINT ["upscale"]
CMD ["--help"]
