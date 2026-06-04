# Security Policy

## Supported versions

The latest released minor version receives security updates.

| Version | Supported |
| ------- | --------- |
| 0.1.x   | ✅        |

## Reporting a vulnerability

Please **do not** open a public issue for security vulnerabilities.

Instead, report privately via GitHub's
[private vulnerability reporting](https://github.com/koflerphillip/cli-image-upscaler/security/advisories/new),
or email **koflerphillip@gmail.com** with:

- a description of the issue and its impact,
- steps to reproduce or a proof of concept,
- any suggested remediation.

You can expect an acknowledgement within **72 hours** and a status update within
**7 days**. Please give us a reasonable window to address the issue before any
public disclosure.

## Automated scanning

This project runs automated security tooling on every push and pull request, and
on a weekly schedule:

- **Trivy** — filesystem and container image vulnerability scanning (results in the
  GitHub Security tab).
- **CodeQL** — static analysis of the Python source.
- **Dependabot** — automated dependency and GitHub Actions updates.

## Hardening notes

- Model weights are downloaded over HTTPS from the official upstream release pages.
- The Docker image runs as an unprivileged user and contains no build toolchain.
- Use `--no-download` in locked-down environments to forbid network access at runtime.
