# ebump

Easy version bumping CLI for python projects.

`ebump` is a simple (opinionated) wrapper around the
[`bumpver`](https://github.com/mbarkhau/bumpver) library that provides an
easy-to-use CLI for version bumping in Python projects. It focuses on simplicity
and ease of use, making it ideal for developers and CI/CD pipelines and scripts.

## Quick showcase

```bash
# Bump patch/minor/major versions
ebump patch   # Example: 1.0.0 -> 1.0.1
ebump minor   # Example: 1.0.1 -> 1.1.0
ebump major   # Example: 1.5.4 -> 2.0.0

# Bumping (major/minor/patch) resets pre-release tag to final
ebump minor   # Example: 1.0.0-beta2 -> 1.1.0

# Bump pre-release tags
ebump alpha   # Example: 1.0.0-alpha4 -> 1.0.0-alpha5
ebump beta    # Example: 1.0.0-alpha5 -> 1.0.0-beta0
ebump rc      # Example: 1.0.0-beta3 -> 1.0.0-rc2

# Combined bump
ebump minor beta  # Example: 1.0.0 -> 1.1.0-beta0

# Bump the current pre-release tag number
ebump tag    # Example: 1.0.0-beta0 -> 1.0.0-beta1

# Make/ensure final version
ebump final  # Example: 1.0.0-rc2 -> 1.0.0

# Running in dry mode (no file changes)
ebump patch --dry
```

## Instalation / Usage

You can use `ebump` directly via `uvx` (recommended):

```bash
uvx ebump [PARAMS ...]
```

Or install it via `pip`:

```bash
pip install ebump
```

## Why `ebump`?

Design differences with `bumpver` CLI:

- Bumping `final` tag doesn't throw errors if the version is already final.

  > Useful for CI/CD pipelines where you want to ensure the version is final without worrying about its current state.

- Bumping one of the main version parts (`patch`, `minor`, `major`) automatically resets any pre-release tag to `final`.

  > If you bump the `minor` version from `1.0.0-beta2`, it will become `1.1.0` instead of `1.1.0-final`.
    You can still set a pre-release tag in the same command (e.g., `ebump minor beta` to get `1.1.0-beta0`).

- `show` action to print the raw current version without any other text (useful for scripts).
- Simplified CLI with fewer options, focusing on the most common use cases.

## What `ebump` is NOT

- It is not a replacement for `bumpver` library. It is a wrapper around it.
  You can still use `bumpver` library directly for more complex use cases.
- It does not aim to cover all use cases. It focuses on simplicity and ease of use.

## 🤝 Contributing

Contributions are welcome!
Please ensure all QA checks and tests pass before opening a pull request.

---

<sub>🚀 Project starter provided by [Cookie Pyrate](https://github.com/gvieralopez/cookie-pyrate)</sub>
