import textwrap

import pytest
from conftest import make_pyproject

from ebump.config import parse_config
from ebump.version import VERSION_RE


class TestConfig:
    def test_config_no_patterns(self, project):
        make_pyproject("1.0.0", project)
        cfg = parse_config(project)
        assert cfg.current_version == "1.0.0"

    def test_config_with_patterns(self, project):
        make_pyproject(
            "2.3.0-beta1",
            project,
            patterns=[r'"custom_file.md" = ["^version = {version}$"]'],
            custom_files=[("custom_file.md", "version = 2.3.0-beta1")],
        )
        cfg = parse_config(project)
        assert cfg.current_version == "2.3.0-beta1"
        assert len(cfg.re_patterns) == 2  # pyproject.toml + custom_file.md
        assert project / "custom_file.md" in cfg.re_patterns
        patterns = cfg.re_patterns[project / "custom_file.md"]
        assert len(patterns) == 1
        assert patterns[0].pattern == r"^version = " + VERSION_RE.pattern + "$"

    def test_config_no_pyproject_version(self, project):
        make_pyproject(
            "",
            project,
            custom_pyproject_content=textwrap.dedent("""
            [project]
            name = "test_project"
            """),
        )
        with pytest.raises(ValueError, match=r"No version found in pyproject.toml.*"):
            parse_config(project)

    def test_config_invalid_pyproject_version(self, project):
        make_pyproject(
            "not_a_version",
            project,
            custom_pyproject_content=textwrap.dedent("""
            [project]
            name = "test_project"
            version = "not_a_version"
            """),
        )
        with pytest.raises(
            ValueError, match=r"Invalid version string in pyproject.toml.*"
        ):
            parse_config(project)

    def test_config_pattern_invalid_file(self, project):
        make_pyproject(
            "1.0.0",
            project,
            patterns=[r'"nonexistent_file.md" = ["^version = {version}$"]'],
        )
        with pytest.raises(FileNotFoundError, match=r"File .* does not exist.*"):
            parse_config(project)
