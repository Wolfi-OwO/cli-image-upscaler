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

import pytest

AI_PACKAGES = ["basicsr", "realesrgan", "gfpgan"]

ai_installed = importlib.util.find_spec("torch") is not None
requires_ai = pytest.mark.skipif(
    not ai_installed, reason="[ai] extra not installed"
)


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

    assert numpy.__version__.startswith("1."), (
        f"basicsr requires NumPy 1.x, found {numpy.__version__}"
    )
