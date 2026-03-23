import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from ebump.version import VERSION_RE, TagType, Version


@dataclass(frozen=True)
class Config:
    root: Path
    current_version: Version
    re_patterns: dict[Path, list[re.Pattern]]


def _ensure_pyproject_pattern(
    pyproject_path: Path, re_patterns: dict[Path, list[re.Pattern]]
) -> None:
    pyproject_pattern = re.compile(
        r"^version\s*=\s*\"" + VERSION_RE.pattern + r"\"\s*$"
    )
    pyproject_patterns = re_patterns.get(pyproject_path, [])
    pyproject_patterns.append(pyproject_pattern)
    re_patterns[pyproject_path] = pyproject_patterns


def parse_config(root: Path) -> Config:
    pyproject_path = root / "pyproject.toml"
    pyproject_content = pyproject_path.read_text() if pyproject_path.exists() else ""
    if not pyproject_content:
        raise FileNotFoundError(
            f"No pyproject.toml found in project root {root.absolute()!s}"
        )

    pyproject_dict = tomllib.loads(pyproject_content)

    current_version_str = pyproject_dict.get("project", {}).get("version", None)
    if not current_version_str:
        raise ValueError(
            "No version found in pyproject.toml. Please add a version field under [project]"
        )

    try:
        current_version = Version.parse(current_version_str)
    except ValueError as e:
        raise ValueError(
            f"Invalid version string in pyproject.toml: '{e}'. ebump only "
            "supports versions in the format 'MAYOR.MINOR.PATCH[-TAG[NUM]]'"
            f"where TAG can be {set(TagType.__members__)}.\n"
        ) from e

    config_patterns = (
        pyproject_dict.get("tool", {}).get("ebump", {}).get("patterns", {})
    )
    re_patterns: dict[Path, list[re.Pattern]] = {}

    for str_path, patterns in config_patterns.items():
        path = (root / Path(str_path)).absolute()
        if not (root / path).exists():
            raise FileNotFoundError(
                f"File {path} specified in pyproject.toml does not exist in project root {root.absolute()!s}"
            )
        path_re_patterns: list[re.Pattern] = []
        for pattern in patterns:
            if "{version}" not in pattern:
                raise ValueError(
                    f"Pattern '{pattern}' in file {path} does not contain '{{version}}' placeholder"
                )
            re_patt = pattern.replace("{version}", VERSION_RE.pattern)
            path_re_patterns.append(re.compile(re_patt))
        re_patterns[path] = path_re_patterns

    _ensure_pyproject_pattern(pyproject_path, re_patterns)
    return Config(root=root, current_version=current_version, re_patterns=re_patterns)
