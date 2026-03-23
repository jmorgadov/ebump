# ebump

Easy version bumping CLI for python projects.

`ebump` is a simple (opinionated) wrapper around the
[`bumpver`](https://github.com/mbarkhau/bumpver) library that provides an
easy-to-use CLI for version bumping in Python projects. It focuses on simplicity
and ease of use, making it ideal for developers, CI/CD pipelines, and scriptsr

## Quick showcase

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

- Bumping one of the main version parts (`patch`, `minor`, `major`)
  automatically resets any pre-release tag to `final` unless you explicitly
  specify a new tag in the same command.

  > If you bump the `minor` version from `1.0.0-beta2`, it will become `1.1.0` instead of `1.1.0-final`.
    You can still set a pre-release tag in the same command (e.g., `ebump minor beta` to get `1.1.0-beta0`).

- Simplified CLI with fewer options, focusing on the most common use cases.
- Can be executed in any directory of the project, root is automatically detected.

## What `ebump` is NOT

- It is not a replacement for `bumpver` library. It is a wrapper around it.
  You can still use `bumpver` library directly for more complex use cases.
- It does not aim to cover all use cases. It focuses on simplicity and ease of use.

## 🤝 Contributing

Contributions are welcome!
Please ensure all QA checks and tests pass before opening a pull request.

---

<sub>🚀 Project starter provided by [Cookie Pyrate](https://github.com/gvieralopez/cookie-pyrate)</sub>
