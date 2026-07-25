"""Import guard for the [ai] extra.

`pip install` succeeding tells us nothing about whether the AI backend works:
basicsr, realesrgan and gfpgan all import torchvision.transforms.functional_tensor,
which torchvision removed in 0.17. image_upscaler.upscaler installs a runtime
compat shim (_install_basicsr_compat) before importing realesrgan to cover this,
so pyproject.toml/Dockerfile/ci.yml deliberately do NOT cap torchvision below
0.17 — a <0.17 cap would make cu128 (RTX 50-series / Blackwell) impossible,
since cu128 only ships torchvision>=0.22.

These tests import the packages for real (through the shim, not around it), and
they skip when the extra isn't installed (the default dev environment), running
instead in CI's dedicated ai-extras job.
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
    """The module basicsr imports. torchvision>=0.17 removed it, so we install a
    runtime shim before importing realesrgan; go through that real entry point
    (not a raw import) so this test still means something once torchvision>=0.17
    is the common case, rather than only passing by accident on an old pin.
    """
    from image_upscaler.upscaler import _install_basicsr_compat

    _install_basicsr_compat()
    import torchvision.transforms.functional_tensor  # noqa: F401


@requires_ai
def test_numpy_is_v1() -> None:
    """basicsr relies on aliases NumPy 2.x removed."""
    import numpy

    assert numpy.__version__.startswith(
        "1."
    ), f"basicsr requires NumPy 1.x, found {numpy.__version__}"


_OTHER_PIN_LOCATIONS = [
    ROOT / "Dockerfile",
    ROOT / ".github" / "workflows" / "ci.yml",
]


@pytest.mark.parametrize("package", ["torch", "torchvision"])
@pytest.mark.parametrize("other_path", _OTHER_PIN_LOCATIONS, ids=lambda p: p.name)
def test_torch_pin_matches_pyproject(package: str, other_path: Path) -> None:
    """The Dockerfile and ci.yml each hardcode their own torch/torchvision bounds
    (to force installing from a specific wheel index before the [ai] extra would
    otherwise re-resolve them from plain PyPI). Those duplicate copies have
    already drifted from pyproject.toml *twice*: dependabot bumped pyproject's
    torch upper bound (<2.2 -> <2.14) without the Dockerfile/ci.yml copies
    following, and `docker build --build-arg TORCH_CHANNEL=cu128` then failed
    outright because cu128 only ships torch>=2.7 (nothing satisfies a stale
    "<2.2" ceiling).

    This needs no [ai] install, so it runs in the default suite (and therefore
    on dependabot PRs), not only in CI's gated ai-extras job.
    """
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    other = other_path.read_text(encoding="utf-8")
    assert _spec(other, package) == _spec(
        pyproject, package
    ), f"{other_path.name}'s {package} pin has drifted from pyproject.toml"
