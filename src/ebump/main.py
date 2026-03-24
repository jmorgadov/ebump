"""
ebump - Easy version bumping CLI tool
"""

import argparse
import logging
import os
import sys

from ebump.bump import bump
from ebump.config import Config, parse_config
from ebump.rewrite import perform_rewrites, rewrite_files
from ebump.utils import project_root
from ebump.version import PartType, TagType, Version

logger = logging.getLogger(__name__)


MAIN_PARTS = {"patch", "minor", "major"}
PART_OPTS = MAIN_PARTS.union({"tag"})
TAG_OPTS = {"alpha", "beta", "dev", "rc", "post", "final"}


def _show_diff(old_lines: list[str], new_lines: list[str]) -> None:
    for old_line, new_line in zip(old_lines, new_lines, strict=False):
        if old_line != new_line:
            sys.stdout.write(f"- {old_line}")
            sys.stdout.write(f"+ {new_line}")


def set_version(cfg: Config, new_version: Version, dry_run: bool) -> None:
    rewrite_data_list = rewrite_files(cfg, str(new_version))
    current_version = cfg.current_version

    if dry_run:
        sys.stdout.write("Dry run - no files will be modified. Showing diffs:\n")
        for rewrite_data in rewrite_data_list:
            sys.stdout.write(f"\n{rewrite_data.path.relative_to(cfg.root)}:\n")
            _show_diff(rewrite_data.old_lines, rewrite_data.new_lines)
    elif new_version != current_version:
        perform_rewrites(rewrite_data_list)
        sys.stdout.write(f"Version set: {new_version}\n")
    else:
        sys.stdout.write(f"Version is already at {current_version}, no changes made.\n")


def cli() -> None:
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

    parser.add_argument(
        "--set",
        default=None,
        help="Set the version to a specific value instead of bumping. This overrides the 'bump' argument.",
    )

    parser.add_argument(
        "--force",
        default=False,
        action="store_true",
        help="Force the version set (when used with --set) even if the new version is not greater than the current version. Use with caution.",
    )

    args = parser.parse_args()
    bump_args = args.bump
    dry_run = args.dry_run

    root = project_root()
    os.chdir(root)

    cfg = parse_config(root)
    current_version = cfg.current_version

    if args.set is not None:
        new_version = Version.parse(args.set)
        if not args.force and new_version <= current_version:
            raise ValueError(
                f"New version {new_version} must be greater than current "
                f"version {current_version}. Use --force to override this check."
            )
        set_version(cfg, new_version, dry_run)
        sys.exit(0)

    if not bump_args:
        sys.stdout.write(f"{current_version}\n")
        sys.exit(0)

    if len(bump_args) > 2:
        raise ValueError(
            "Too many arguments provided. You can only specify one part to bump"
            " and/or one tag"
        )

    part_opts = set(map(str.lower, PartType.__members__))
    tag_opts = set(map(str.lower, TagType.__members__))

    cmd_bump_set = set(bump_args)

    part_to_bump: set[str] = cmd_bump_set.intersection(part_opts)
    if len(part_to_bump) > 1:
        raise ValueError("You can only specify one part to bump")

    tag_to_bump: set[str] = cmd_bump_set.intersection(tag_opts)
    if len(tag_to_bump) > 1:
        raise ValueError("You can only specify one tag to bump")

    part_str = part_to_bump.pop() if part_to_bump else "tag"
    tag_str = tag_to_bump.pop() if tag_to_bump else None

    part = PartType(part_str)
    tag = TagType(tag_str) if tag_str else None

    new_version = bump(current_version, part, tag)
    set_version(cfg, new_version, dry_run)


def main() -> None:
    try:
        cli()
    except Exception as e:
        logger.error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
