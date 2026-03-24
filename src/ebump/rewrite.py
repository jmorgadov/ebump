import re
from pathlib import Path
from typing import NamedTuple

from ebump.config import Config
from ebump.version import VERSION_RE

RewriteData = NamedTuple(
    "RewriteData",
    [
        ("path", Path),
        ("old_lines", list[str]),
        ("new_lines", list[str]),
    ],
)


def rewrite_lines(
    old_lines: list[str], new_version: str, patterns: list[re.Pattern]
) -> list[str]:
    used_patterns = set()
    new_lines = old_lines[:]
    for i, line in enumerate(old_lines):
        stripped = line.rstrip("\r\n")
        ending = line[len(stripped) :]
        new_line = line
        for patt_idx, pattern in enumerate(patterns):
            match = pattern.match(stripped)
            if match is None:
                continue

            used_patterns.add(patt_idx)
            new_line = ""
            last_idx = 0
            for group_idx in range(len(match.groups()) // 2):
                # group indices are 1-based and we want to
                # skip the tag group for each version group
                group_idx = group_idx * 2 + 1
                start_idx = match.start(group_idx)
                end_idx = match.end(group_idx)
                if last_idx < start_idx:
                    new_line += stripped[last_idx:start_idx]

                new_line += new_version
                last_idx = end_idx

            if last_idx < len(stripped):
                new_line += stripped[last_idx:]
            new_line += ending
            break

        new_lines[i] = new_line
    if len(used_patterns) < len(patterns):
        unused_patterns = set(range(len(patterns))) - used_patterns
        raise ValueError(
            "Some patterns were not found\n"
            + "\n".join(
                f"- {patterns[i].pattern.replace(VERSION_RE.pattern, '{version}')}"
                for i in unused_patterns
            )
        )
    return new_lines


def rewrite_file(
    path: Path, new_version: str, patterns: list[re.Pattern]
) -> RewriteData:
    content = path.read_text(newline="")
    old_lines = content.splitlines(keepends=True)
    new_lines = rewrite_lines(old_lines, new_version, patterns)
    return RewriteData(path=path, old_lines=old_lines, new_lines=new_lines)


def rewrite_files(config: Config, new_version: str) -> list[RewriteData]:
    return [
        rewrite_file(path, new_version, patterns)
        for path, patterns in config.re_patterns.items()
    ]


def perform_rewrites(rewrite_data_list: list[RewriteData]) -> None:
    for rewrite_data in rewrite_data_list:
        new_content = "".join(rewrite_data.new_lines)
        rewrite_data.path.write_text(new_content, newline="")
