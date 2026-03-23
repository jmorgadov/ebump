"""
Tests for ebump CLI.

The core challenge: ebump calls `os.chdir(project_root())` and reads a real
pyproject.toml on disk. So every test gets a fresh temporary directory that
looks like a real Python project with bumpver configured.
"""

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_pyproject(version: str, tmp_path: Path) -> None:
    """Write a minimal pyproject.toml with bumpver configured."""
    content = textwrap.dedent(f"""\
        [project]
        name = "mypackage"
        version = "{version}"
 
        [tool.bumpver]
        current_version = "{version}"
        version_pattern = "MAJOR.MINOR.PATCH[-TAGNUM]"
 
        [tool.bumpver.file_patterns]
        "pyproject.toml" = [
            '^version = "{{version}}"',
            '^current_version = "{{version}}"',
        ]
    """)
    (tmp_path / "pyproject.toml").write_text(content)


def read_version(tmp_path: Path) -> str:
    """Read the current_version field from pyproject.toml."""
    for line in (tmp_path / "pyproject.toml").read_text().splitlines():
        if line.startswith("version = "):
            return line.split('"')[1]
    raise ValueError("current_version not found")


def run_ebump(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """Run ebump as a subprocess so os.chdir() side effects are isolated."""
    project_root = Path(__file__).parent.parent
    data_file = str((project_root / ".coverage").absolute())
    return subprocess.run(  # noqa: S603
        [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "--parallel-mode",
            f"--data-file={data_file}",
            "-m",
            "ebump.main",
            *args,
        ],
        capture_output=True,
        text=True,
        cwd=str(cwd),
    )


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def project(tmp_path_factory: pytest.TempPathFactory):
    """
    A temporary directory that mimics a real Python project.
    Starts at version 1.0.0 by default.
    Returns the path; tests can call make_pyproject() again to change version.
    """

    tmp_path = tmp_path_factory.mktemp("mock-python-project")
    make_pyproject("1.0.0", tmp_path)
    return tmp_path


# ---------------------------------------------------------------------------
# Showing the current version
# ---------------------------------------------------------------------------


class TestShowVersion:
    def test_shows_current_version(self, project):
        result = run_ebump([], project)
        assert result.returncode == 0
        assert "1.0.0" in result.stdout

    def test_shows_pre_release_version(self, project):
        make_pyproject("2.3.0-beta1", project)
        result = run_ebump([], project)
        assert result.returncode == 0
        assert "2.3.0-beta1" in result.stdout


# ---------------------------------------------------------------------------
# Bumping main parts
# ---------------------------------------------------------------------------


class TestBumpPatch:
    def test_patch_increments_patch(self, project):
        run_ebump(["patch"], project)
        assert read_version(project) == "1.0.1"

    def test_patch_resets_prerelease_tag(self, project):
        make_pyproject("1.0.0-beta2", project)
        run_ebump(["patch"], project)
        assert read_version(project) == "1.0.1"

    def test_patch_dry_run_does_not_change(self, project):
        run_ebump(["patch", "--dry-run"], project)
        assert read_version(project) == "1.0.0"


class TestBumpMinor:
    def test_minor_increments_minor_resets_patch(self, project):
        make_pyproject("1.2.3", project)
        run_ebump(["minor"], project)
        assert read_version(project) == "1.3.0"

    def test_minor_with_beta_tag(self, project):
        run_ebump(["minor", "beta"], project)
        assert read_version(project) == "1.1.0-beta0"

    def test_minor_dry_run(self, project):
        run_ebump(["minor", "--dry-run"], project)
        assert read_version(project) == "1.0.0"


class TestBumpMajor:
    def test_major_increments_major_resets_rest(self, project):
        make_pyproject("1.5.4", project)
        run_ebump(["major"], project)
        assert read_version(project) == "2.0.0"

    def test_major_with_alpha_tag(self, project):
        run_ebump(["major", "alpha"], project)
        assert read_version(project) == "2.0.0-alpha0"


# ---------------------------------------------------------------------------
# Bumping pre-release tags
# ---------------------------------------------------------------------------


class TestBumpTag:
    def test_tag_increments_existing_tag_number(self, project):
        make_pyproject("1.0.0-beta1", project)
        run_ebump(["tag"], project)
        assert read_version(project) == "1.0.0-beta2"

    def test_tag_with_no_tag_exits_error(self, project):
        assert read_version(project) == "1.0.0"
        result = run_ebump(["tag"], project)
        assert result.returncode != 0
        assert "No tag found to bump" in result.stderr

    def test_tag_beta_when_at_alpha_promotes_to_beta(self, project):
        make_pyproject("1.0.0-alpha3", project)
        run_ebump(["tag", "beta"], project)
        assert read_version(project) == "1.0.0-beta0"

    def test_tag_beta_when_at_beta_increments(self, project):
        make_pyproject("1.0.0-beta0", project)
        run_ebump(["tag", "beta"], project)
        assert read_version(project) == "1.0.0-beta1"


class TestTagShorthand:
    def test_alpha_when_already_alpha_increments(self, project):
        make_pyproject("1.0.0-alpha4", project)
        run_ebump(["alpha"], project)
        assert read_version(project) == "1.0.0-alpha5"

    def test_beta_when_at_alpha_promotes(self, project):
        make_pyproject("1.0.0-alpha5", project)
        run_ebump(["beta"], project)
        assert read_version(project) == "1.0.0-beta0"

    def test_final_from_rc_removes_tag(self, project):
        make_pyproject("1.0.0-rc2", project)
        run_ebump(["final"], project)
        assert read_version(project) == "1.0.0"

    def test_final_when_already_final_is_noop(self, project):
        result = run_ebump(["final"], project)
        assert result.returncode == 0
        assert read_version(project) == "1.0.0"
        assert "Already at final" in result.stdout


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


class TestErrorCases:
    def test_two_parts_is_an_error(self, project):
        result = run_ebump(["patch", "minor"], project)
        assert result.returncode != 0

    def test_two_tags_is_an_error(self, project):
        result = run_ebump(["alpha", "beta"], project)
        assert result.returncode != 0

    def test_three_args_is_an_error(self, project):
        result = run_ebump(["minor", "alpha", "beta"], project)
        assert result.returncode != 0

    def test_missing_config_exits_with_error(self, tmp_path):
        # A directory with no pyproject.toml at all
        result = run_ebump([], tmp_path)
        assert result.returncode != 0

    def test_invalid_bumping_exits_with_error(self, project):
        make_pyproject("1.0.0-beta2", project)
        result = run_ebump(["alpha"], project)
        assert result.returncode != 0
