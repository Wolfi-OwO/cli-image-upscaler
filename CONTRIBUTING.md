# Contributing to image-upscaler

Thanks for your interest in improving image-upscaler! Contributions of all kinds
are welcome — bug reports, documentation, tests, and code.

## Getting set up

```bash
git clone https://github.com/Wolfi-OwO/cli-image-upscaler
cd cli-image-upscaler
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
make install          # editable install with dev tools
pre-commit install    # enable git hooks
```

To work on the AI backend, also install the heavy extras:

```bash
make install-ai
```

## Development workflow

1. Create a branch: `git checkout -b feature/my-change`.
2. Make your change and add tests.
3. Run the full check suite locally:

   ```bash
   make check        # ruff + black + mypy + pytest
   ```

4. Update `CHANGELOG.md` under **Unreleased**.
5. Open a pull request against `main` and fill in the template.

## Code style

- Formatting is handled by **black** and **ruff** (line length 100).
- Run `make format` to auto-fix.
- Public functions should have type hints and concise docstrings.
- Keep the Lanczos path dependency-free so the base package installs without torch.

## Tests

- Tests live in `tests/` and run with `pytest`.
- The default suite must pass **without** the AI extras installed (it exercises the
  Lanczos backend, utils, models registry, and CLI). Guard AI-only tests so they
  skip when `torch`/`realesrgan` are missing.
- Aim to keep coverage steady or improving.

## Commit messages

Use clear, imperative commit messages (e.g. `Add --tile option for low-memory GPUs`).
[Conventional Commits](https://www.conventionalcommits.org/) are appreciated but not
required.

## Release process

Releases are cut manually by pushing a version tag — there's no auto-release on
every merge, so `main` can carry multiple merged changes before a release goes
out.

1. Bump `version` in `pyproject.toml` (semantic versioning).
2. Move the `CHANGELOG.md` **Unreleased** entries under a new `## [X.Y.Z]`
   heading (dated).
3. Commit, then tag and push: `git tag vX.Y.Z && git push origin vX.Y.Z`.
4. Pushing the tag fans out automatically to every distribution channel:
   - **GitHub Release** with the built wheel/sdist attached and generated
     release notes ([release.yml](.github/workflows/release.yml)).
   - **PyPI** publish via Trusted Publishing ([release.yml](.github/workflows/release.yml)).
   - **GHCR** (`ghcr.io/wolfi-owo/cli-image-upscaler`) and **Docker Hub**
     (`docker.io/wolfiowo/cli-image-upscaler`) image push, tagged with the
     version and `latest` ([docker.yml](.github/workflows/docker.yml)).

## Reporting bugs / requesting features

Use the [issue templates](https://github.com/Wolfi-OwO/cli-image-upscaler/issues/new/choose).
For security issues, **do not** open a public issue — see [SECURITY.md](SECURITY.md).

By contributing you agree that your contributions are licensed under the
project's [MIT License](LICENSE) and that you abide by our
[Code of Conduct](CODE_OF_CONDUCT.md).
