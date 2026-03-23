"""
Tests for ebump CLI.
"""

from conftest import make_pyproject, read_version, run_ebump

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
        assert "Cannot bump tag number on a final version" in result.stderr

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
        assert "Version is already at" in result.stdout


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


class TestErrorCases:
    def test_bump_to_tag_on_final_is_error(self, project):
        make_pyproject("1.0.0", project)
        result = run_ebump(["beta"], project)
        assert result.returncode != 0
        assert "Cannot bump to tag beta on a final version" in result.stderr

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


class TestRewritePatterns:
    def test_pattern_rewrite_same_line_endings(self, project):
        make_pyproject(
            "1.0.0",
            project,
            custom_pyproject_content='[project]\r\nname = "test_project"\r\nversion = "1.0.0"\r\n',
        )
        run_ebump(["patch"], project)
        assert (project / "pyproject.toml").read_text(
            newline=""
        ) == '[project]\r\nname = "test_project"\r\nversion = "1.0.1"\r\n'

        make_pyproject(
            "1.0.0",
            project,
            custom_pyproject_content='[project]\rname = "test_project"\rversion = "1.0.0"\r',
        )
        run_ebump(["patch"], project)
        assert (project / "pyproject.toml").read_text(
            newline=""
        ) == '[project]\rname = "test_project"\rversion = "1.0.1"\r'


class TestVersionSet:
    def test_version_set(self, project):
        make_pyproject("1.0.0", project)
        result = run_ebump(["--set", "1.0.1-alpha1"], project)
        assert result.returncode == 0
        assert read_version(project) == "1.0.1-alpha1"

    def test_version_set_dry_run(self, project):
        make_pyproject("1.0.0", project)
        result = run_ebump(["--set", "1.0.1-alpha1", "--dry-run"], project)
        assert result.returncode == 0
        assert read_version(project) == "1.0.0"

    def test_version_set_invalid_version(self, project):
        make_pyproject("1.0.0", project)
        result = run_ebump(["--set", "not_a_version"], project)
        assert result.returncode != 0
        assert "Invalid version string: not_a_version" in result.stderr

    def test_version_set_forcedly_overwrite(self, project):
        make_pyproject("3.0.0", project)
        result = run_ebump(["--set", "2.0.0", "--force"], project)
        assert result.returncode == 0
        assert read_version(project) == "2.0.0"

    def test_versino_set_invalid_no_force(self, project):
        make_pyproject("3.0.0", project)
        result = run_ebump(["--set", "2.0.0"], project)
        assert result.returncode != 0
        assert (
            "New version 2.0.0 must be greater than current version 3.0.0"
            in result.stderr
        )
