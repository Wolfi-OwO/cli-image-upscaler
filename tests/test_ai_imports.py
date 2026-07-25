"""Import guard for the [ai] extra.

`pip install` succeeding tells us nothing about whether the AI backend works:
basicsr, realesrgan and gfpgan all import torchvision.transforms.functional_tensor,
which torchvision removed in 0.17. Installation still exits 0, so a bad resolution
ships a green build and an image that fails the first time a user runs it.

These tests import the packages for real. They skip when the extra isn't installed
(the default dev environment), and run in CI's dedicated ai-extras job.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

AI_PACKAGES = ["basicsr", "realesrgan", "gfpgan"]

ai_installed = importlib.util.find_spec("torch") is not None
requires_ai = pytest.mark.skipif(not ai_installed, reason="[ai] extra not installed")

ROOT = Path(__file__).resolve().parent.parent


def _spec(text: str, package: str) -> str:
    match = re.search(rf'"({package}>=[^"]+)"', text)
    assert match, f"{package} dependency spec not found"
    return match.group(1)


@requires_ai
@pytest.mark.parametrize("package", AI_PACKAGES)
def test_ai_package_imports(package: str) -> None:
    """Each AI package must actually import, not merely be installed."""
    __import__(package)


@requires_ai
def test_torchvision_has_functional_tensor() -> None:
    """The specific module the AI stack depends on, pinned via torchvision<0.17."""
    import torchvision.transforms.functional_tensor  # noqa: F401


@requires_ai
def test_numpy_is_v1() -> None:
    """basicsr relies on aliases NumPy 2.x removed."""
    import numpy

    assert numpy.__version__.startswith(
        "1."
    ), f"basicsr requires NumPy 1.x, found {numpy.__version__}"


@pytest.mark.parametrize("package", ["torch", "torchvision"])
def test_dockerfile_torch_pin_matches_pyproject(package: str) -> None:
    """The Dockerfile hardcodes its own torch/torchvision bounds (to force
    installing from the CUDA/CPU wheel index before the [ai] extra would
    otherwise re-resolve them from plain PyPI). That duplicate copy has already
    drifted from pyproject.toml once: dependabot bumped pyproject.toml's upper
    bound from <2.2 to <2.14, the Dockerfile's copy was not updated, and
    `docker build --build-arg TORCH_CHANNEL=cu128` then failed outright because
    cu128 only ships torch>=2.7 (nothing satisfies a stale "<2.2" ceiling).

    This needs no [ai] install, so it runs in the default suite (and therefore
    on dependabot PRs), not only in CI's gated ai-extras job.
    """
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert _spec(dockerfile, package) == _spec(pyproject, package)
