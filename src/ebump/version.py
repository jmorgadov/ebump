from __future__ import annotations

import enum
import re
from typing import NamedTuple, cast


class PartType(enum.Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    TAG = "tag"


class TagType(enum.Enum):
    ALPHA = "alpha"
    BETA = "beta"
    DEV = "dev"
    RC = "rc"
    FINAL = "final"


TAGS_ORDER = {tag: i for i, tag in enumerate(TagType)}

VERSION_RE = re.compile(r"(\d+\.\d+\.\d+(?:-(alpha|beta|dev|rc|post)\d*)?)")
VERSION_GROUPS_RE = re.compile(
    r"(?P<major>\d+)"
    r"\."
    r"(?P<minor>\d+)"
    r"\."
    r"(?P<patch>\d+)"
    r"(?:-(?P<tag>alpha|beta|dev|rc|post)(?P<tag_num>\d*))?"
)


class Version(NamedTuple):
    """Represents a version with major, minor, patch, tag and tag number components."""

    major: int
    minor: int
    patch: int
    tag: TagType
    tag_num: int

    def __str__(self) -> str:
        tag_sufix = (
            "" if self.tag == TagType.FINAL else f"-{self.tag._value_}{self.tag_num}"
        )
        return f"{self.major}.{self.minor}.{self.patch}{tag_sufix}"

    @staticmethod
    def parse(version_str: str) -> Version:
        match = VERSION_GROUPS_RE.fullmatch(version_str)
        if not match:
            raise ValueError(f"Invalid version string: {version_str}")
        major = int(match.group("major"))
        minor = int(match.group("minor"))
        patch = int(match.group("patch"))
        tag = TagType(match.group("tag") or "final")
        tag_num = int(match.group("tag_num") or 0)

        return Version(major, minor, patch, cast(TagType, tag), tag_num)

    def __eq__(self, other: object) -> bool:
        return self._compare(other) == 0

    def __lt__(self, other: object) -> bool:
        return self._compare(other) == -1

    def __le__(self, other: object) -> bool:
        return self._compare(other) in (-1, 0)

    def __gt__(self, other: object) -> bool:
        return self._compare(other) == 1

    def __ge__(self, other: object) -> bool:
        return self._compare(other) in (0, 1)

    def _compare(self, other: object) -> int:
        """
        Compare this version with another version.

        Returns:
            -1 if this version is less than the other version
             0 if this version is equal to the other version
             1 if this version is greater than the other version
        """
        if not isinstance(other, (Version, str)):
            raise TypeError(f"Cannot compare Version with {type(other)}")
        if isinstance(other, str):
            try:
                other = Version.parse(other)
            except ValueError as e:
                raise ValueError(
                    f"Cannot compare Version with invalid version string: {other}"
                ) from e
        if self.major != other.major:
            return -1 if self.major < other.major else 1
        if self.minor != other.minor:
            return -1 if self.minor < other.minor else 1
        if self.patch != other.patch:
            return -1 if self.patch < other.patch else 1
        if self.tag != other.tag:
            return -1 if TAGS_ORDER[self.tag] < TAGS_ORDER[other.tag] else 1
        if self.tag_num != other.tag_num:
            return -1 if self.tag_num < other.tag_num else 1
        return 0
