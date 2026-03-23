"""
ebump - Easy version bumping CLI tool
"""

import argparse
import logging
import os
import sys
from pathlib import Path

import bumpver
import bumpver.config
import bumpver.v1version
import bumpver.v2version
import click
import click.testing
from bumpver.cli import cli

logger = logging.getLogger(__name__)


ROOT_IDENTIFIERS = ["pyproject.toml", ".git"]

MAIN_PARTS = {"patch", "minor", "major"}
PART_OPTS = MAIN_PARTS.union({"tag"})
TAG_OPTS = {"alpha", "beta", "dev", "rc", "post", "final"}


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
    cfg: bumpver.config.Config,
    action: str | None,
    tag: str | None,
    dry: bool = False,
) -> None:
    """
    Write the new version to your version file/config
    """
    raw_pattern = cfg.version_pattern
    current_version = cfg.current_version
    vinfo_func = (
        bumpver.v2version.parse_version_info
        if cfg.is_new_pattern
        else bumpver.v1version.parse_version_info
    )
    vinfo = vinfo_func(current_version, raw_pattern)

    cmd = ["update"]
    if action in MAIN_PARTS:
        cmd += ["--" + action, "--tag", tag or "final"]
    elif action == "tag":
        if not vinfo.tag:
            sys.stderr.write("No tag found to bump.\n")
            sys.exit(1)
        cmd += ["--tag-num", "-n"]
    elif action in TAG_OPTS:
        if action == "final" and (not vinfo.tag or vinfo.tag == "final"):
            sys.stdout.write("Already at final version. All good.\n")
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
Usage examples:

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

Bad examples:

> ebump minor alpha beta    # Error: You can only specify one part to bump and/or one tag
> ebump patch minor         # Error: You can only specify one part to bump
> ebump alpha beta          # Error: You can only specify one tag to bump

# If current version has no tag
> ebump tag                 # Error: No tag found to bump
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "bump",
        nargs="*",
        default=None,
        choices=list(PART_OPTS) + list(TAG_OPTS),
        help=f"Version part to bump {PART_OPTS}, and/or specific pre-release tag {TAG_OPTS}",
    )

    parser.add_argument(
        "--dry-run",
        default=False,
        action="store_true",
        help="Perform a dry run without modifying any files",
    )

    args = parser.parse_args()

    os.chdir(project_root())

    _, cfg = bumpver.config.init(project_path=".")
    if cfg is None:
        logger.error(
            "No valid configuration found. Please ensure you have a supported version file and configuration."
        )
        exit(1)

    if not args.bump:
        current_version = cfg.current_version
        sys.stdout.write(f"{current_version}\n")
        sys.exit(0)

    if len(args.bump) > 2:
        logger.error("You can only specify one part to bump and/or one tag.")
        sys.exit(1)

    cmd_bump_set = set(args.bump)
    part_to_bump: set[str] = cmd_bump_set.intersection(PART_OPTS)
    if len(part_to_bump) > 1:
        logger.error("You can only specify one part to bump %s.", str(PART_OPTS))
        sys.exit(1)

    tag_to_bump: set[str] = cmd_bump_set.intersection(TAG_OPTS)
    if len(tag_to_bump) > 1:
        logger.error("You can only specify one tag to bump %s.", str(TAG_OPTS))
        sys.exit(1)

    action = part_to_bump.pop() if part_to_bump else tag_to_bump.pop()
    tag = tag_to_bump.pop() if tag_to_bump else None

    # `ebump tag [TAG]` has the same behavior as `ebump [TAG]`
    if action == "tag" and tag is not None:
        action = tag
        tag = None

    run(cfg, action, tag, args.dry_run)


if __name__ == "__main__":
    main()
