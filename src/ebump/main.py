"""
ebump - Easy version bumping CLI tool
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any

import bumpver
import bumpver.config
import bumpver.v1patterns
import bumpver.v1version
import bumpver.v2version
import click
import click.testing
from bumpver.cli import cli

logger = logging.getLogger(__name__)


ROOT_IDENTIFIERS = ["pyproject.toml", ".git"]


def project_root() -> Path:
    """
    Get the project root directory
    """

    current_dir = Path.cwd()
    while current_dir != current_dir.parent:
        if any((current_dir / identifier).exists() for identifier in ROOT_IDENTIFIERS):
            return current_dir
        current_dir = current_dir.parent
    return Path.cwd()


def run(
    vinfo: Any,
    cfg: bumpver.config.Config,
    action: str,
    tag: str | None,
    dry: bool = False,
) -> None:
    """
    Write the new version to your version file/config
    """
    cmd = ["update"]
    if action in {"patch", "minor", "major"}:
        cmd += ["--" + action, "--tag", tag or "final"]
    elif action == "tag":
        if not cfg.tag:
            sys.stderr.write("No pre-release tag found to bump.\n")
            sys.exit(1)
        cmd += ["--tag-num", "-n"]
    elif action in {"alpha", "beta", "dev", "rc", "post", "final"}:
        if action == "final" and not vinfo.tag:
            sys.stdout.write("Already at final version.\n")
            return
        if action == vinfo.tag:
            cmd += ["--tag-num", "-n"]
        else:
            cmd += ["--tag", action]

    if dry:
        cmd.append("--dry")
    runner = click.testing.CliRunner(catch_exceptions=False)
    result = runner.invoke(cli, cmd, color=True, catch_exceptions=False)

    sys.stdout.write(result.output)
    if result.exit_code != 0:
        sys.exit(1)


def main() -> None:
    """
    Main entry point for the ebump CLI tool
    """
    parser = argparse.ArgumentParser(
        prog="ebump",
        description="Easy version bumping tool",
        epilog="""
Basic:

> ebump show           # Show current version
> ebump --help         # Show help message

Bump version parts:

> ebump patch          # 1.0.0 -> 1.0.1
> ebump minor          # 1.0.1 -> 1.1.0
> ebump major          # 1.5.4 -> 2.0.0

Bump part with tag:

> ebump minor beta     # 1.0.0 -> 1.1.0-beta0

Bump tags:

> ebump alpha          # 1.0.0-alpha4 -> 1.0.0-alpha5
> ebump beta           # 1.0.0-alpha5 -> 1.0.0-beta0

Bump current tag number:

> ebump tag            # 1.0.0-beta0 -> 1.0.0-beta1

Make/ensure final release (no pre-release tag):

> ebump final          # 1.0.0-rc2 -> 1.0.0
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "action",
        nargs="?",
        default=None,
        help="Version part to bump (patch/minor/major/tag), or specific pre-release tag (alpha/beta/dev/rc/final)",
    )

    parser.add_argument(
        "tag",
        nargs="?",
        default=None,
        help="Optional pre-release tag when bumping version parts",
    )

    parser.add_argument(
        "--dry",
        default=False,
        action="store_true",
        help="Perform a dry run without modifying any files",
    )

    args = parser.parse_args()
    os.chdir(project_root())

    _, cfg = bumpver.config.init(project_path=".")
    raw_pattern = cfg.version_pattern
    v1_parts = list(bumpver.v1patterns.PART_PATTERNS) + list(
        bumpver.v1patterns.FULL_PART_FORMATS
    )
    has_v1_part = any("{" + part + "}" in raw_pattern for part in v1_parts)
    vinfo: bumpver.v1version.VersionInfo | bumpver.v2version.VersionInfo
    current_version = cfg.current_version
    if has_v1_part:
        vinfo = bumpver.v1version.parse_version_info(current_version, raw_pattern)
    else:
        vinfo = bumpver.v2version.parse_version_info(current_version, raw_pattern)

    if not args.action:
        parser.print_help()
        sys.exit(1)

    if args.action.lower() == "show":
        sys.stdout.write(f"{current_version}\n")
        return

    action = args.action.lower()
    tag = args.tag.lower() if args.tag else None
    dry = args.dry

    run(vinfo, cfg, action, tag, dry)


if __name__ == "__main__":
    main()
