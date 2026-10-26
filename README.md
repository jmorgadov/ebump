<div align="center">

<img src="assets/logo.svg" alt="" width="96">

# ebump

**Easy version bumping**

[![QA](https://github.com/jmorgadov/ebump/actions/workflows/qa.yml/badge.svg)](https://github.com/jmorgadov/ebump/actions/workflows/qa.yml)
[![Release](https://img.shields.io/github/v/release/jmorgadov/ebump?label=release)](https://github.com/jmorgadov/ebump/releases/latest)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/ebump)](https://pypi.org/project/ebump/)
<br>
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

<!-- Badges to move into the rows above once they apply:
[![Docker image](https://img.shields.io/badge/docker-ghcr.io-2496ED?logo=docker&logoColor=white)](https://github.com/jmorgadov/ebump/pkgs/container/ebump)
[![Docs](https://readthedocs.org/projects/ebump/badge/?version=latest)](https://ebump.readthedocs.io)
-->

[Quick start](#quick-start) · [Usage](#usage) · [Configuration](#configuration) · [Development](#development)

</div>

---

Easy version bumping CLI tool for python projects.

## Features

- Simple and intuitive CLI for version bumping.
- Automatic detection of version field in `pyproject.toml`.
- Pattern-based configuration that allows to change version in multiple files at once.

> [!NOTE]
> This is an **opinionated** tool, it assumes a specific versioning scheme:
> `MAJOR.MINOR.PATCH[-TAG[NUMBER]]`, e.g., `1.2.3`, `1.2.3-beta0`,
> `1.2.3-alpha5`, `1.2.3-rc2`. Supported tags are `alpha`, `beta`, `dev`, `rc`
> (release candidate), and `final`. The `final` tag is implicit when no tag is
> present.

## Quick start

You can use `ebump` directly via `uvx` (recommended):

```bash
uvx ebump [PARAMS ...]
```

Or install it via `pip`:

```bash
pip install ebump
```

## Usage

```bash
> ebump             # 1.0.0                         Shows current version (same as `uv version --short`)
> ebump patch       # 1.0.0 -> 1.0.1                Bump patch
> ebump minor       # 1.0.1 -> 1.1.0                Bump minor
> ebump major       # 1.5.4 -> 2.0.0                Bump major
> ebump minor beta  # 1.0.0 -> 1.1.0-beta0          Bump minor and add beta tag
> ebump tag         # 1.0.0-beta0 -> 1.0.0-beta1    Bump current tag number
> ebump alpha       # 1.0.0-alpha4 -> 1.0.0-alpha5  Bump tag number if already at tag
> ebump beta        # 1.0.0-alpha5 -> 1.0.0-beta0   Bump to tag if not already at that tag
> ebump tag beta    # 1.0.0-alpha5 -> 1.0.0-beta0   Same as 'ebump beta'
> ebump tag beta    # 1.0.0-beta0 -> 1.0.0-beta1    Same as 'ebump beta'
> ebump final       # 1.0.0-rc2 -> 1.0.0            Bump to final
> ebump final       # 1.0.0 -> 1.0.0                If already at final do nothing (ensures final release)
```

Setting specific versions

```bash
> ebump --set 1.2.3         # 1.0.0 -> 1.2.3        Set specific version
> ebump --set 1.2.3 --force # 5.0.0 -> 1.2.3        Force set specific version (even if it's a downgrade). Use with caution!
```

Bad examples:

```bash
> ebump minor alpha beta    # Error: You can only specify one part to bump and/or one tag
> ebump patch minor         # Error: You can only specify one part to bump
> ebump alpha beta          # Error: You can only specify one tag to bump

# If current version has no tag
> ebump tag                 # Error: No tag found to bump
```

Any combination that violates the bumping rules will throw an error. E.g.,
trying to bump alpha while being at beta.

You can also use the `--dry-run` to see what the new version would be without actually changing it:

```bash
> ebump minor --dry-run  # 1.0.0 -> 1.1.0 (no change to version)
```

## Configuration

If you only maintain a simple project with the version only in `pyproject.toml`, you can
use `ebump` without any configuration. It will automatically detect the version field
and update it accordingly.

However, heavily inspired by [bumpver](https://github.com/mbarkhau/bumpver),
`ebump` supports pattern-based configuration via `pyproject.toml` under the
`[tool.ebump.patterns]` section. This allows you to specify different
versioning files and patterns for different parts of your project.

```toml
[tool.ebump.patterns]
"path/to/__init__.py" = ['^__version__ = "{version}"$']
```

## Why `ebump`?

Design differences with `bumpver` CLI:

- Bumping `final` tag doesn't throw errors if the version is already final.

  > Useful for CI/CD pipelines where you want to ensure the version is final without worrying about its current state.

- Bumping one of the main version parts (`patch`, `minor`, `major`)
  automatically resets any pre-release tag to `final` unless you explicitly
  specify a new tag in the same command.

  > If you bump the `minor` version from `1.0.0-beta2`, it will become `1.1.0` instead of `1.1.0-beta0`.
    You can still set a pre-release tag in the same command (e.g., `ebump minor beta` to get `1.1.0-beta0`).

- Simplified CLI with fewer options, focusing on the most common use cases.
- Can be executed in any directory of the project, root is automatically detected.

## What `ebump` is NOT

- It is not a replacement for `bumpver` library. You can still use `bumpver`
  library directly for more complex use cases if necessary.
- It does not aim to cover all use cases. It focuses on simplicity and ease of use.

## Development

Setup, QA, docs and releases: [DEVELOPMENT.md](DEVELOPMENT.md).

## Contributing

Issues and pull requests are welcome; `make qa` must pass.

## Acknowledgements

This project is heavily inspired by [bumpver](https://github.com/mbarkhau/bumpver).

## License

MIT: see [LICENSE](LICENSE).

---

<sub>🚀 Project starter provided by [Cookie Pyrate v1.0.1](https://github.com/gvieralopez/cookie-pyrate/tree/v1.0.1)</sub>
