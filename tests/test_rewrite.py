from conftest import make_pyproject, run_ebump


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

    def test_mixed_line_endings_preserved(self, project):
        content = '[project]\r\nname = "test_project"\nversion = "1.0.0"\r\n'
        make_pyproject("1.0.0", project, custom_pyproject_content=content)

        run_ebump(["patch"], project)

        assert (project / "pyproject.toml").read_text(newline="") == (
            '[project]\r\nname = "test_project"\nversion = "1.0.1"\r\n'
        )

    def test_no_trailing_newline(self, project):
        content = '[project]\nname = "test_project"\nversion = "1.0.0"'
        make_pyproject("1.0.0", project, custom_pyproject_content=content)

        run_ebump(["patch"], project)

        # should NOT add a newline
        assert (project / "pyproject.toml").read_text(newline="") == (
            '[project]\nname = "test_project"\nversion = "1.0.1"'
        )

    def test_preserve_multiple_trailing_newlines(self, project):
        content = '[project]\nname = "test_project"\nversion = "1.0.0"\n\n'
        make_pyproject("1.0.0", project, custom_pyproject_content=content)

        run_ebump(["patch"], project)

        assert (project / "pyproject.toml").read_text(newline="") == (
            '[project]\nname = "test_project"\nversion = "1.0.1"\n\n'
        )

    def test_preserve_blank_lines_between(self, project):
        content = '[project]\n\nname = "test_project"\n\nversion = "1.0.0"\n'
        make_pyproject("1.0.0", project, custom_pyproject_content=content)

        run_ebump(["patch"], project)

        assert (project / "pyproject.toml").read_text(newline="") == (
            '[project]\n\nname = "test_project"\n\nversion = "1.0.1"\n'
        )

    def test_crlf_not_doubled(self, project):
        # regression test for Windows double-spacing bug
        content = '[project]\r\nname = "test_project"\r\nversion = "1.0.0"\r\n'
        make_pyproject("1.0.0", project, custom_pyproject_content=content)

        run_ebump(["patch"], project)

        result = (project / "pyproject.toml").read_text(newline="")

        # ensure no accidental \r\r\n sequences
        assert "\r\r\n" not in result
        assert result == '[project]\r\nname = "test_project"\r\nversion = "1.0.1"\r\n'

    def test_multiple_version_occurrences_same_line(self, project):
        content = '[project]\nversion = "1.0.0"\n# here 1.0.0 also 1.0.0 here\n\n[tool.ebump.patterns]\n"pyproject.toml" = ["^# here {version} also {version} here$"]\n'
        make_pyproject("1.0.0", project, custom_pyproject_content=content)

        result = run_ebump(["patch"], project)

        assert result.returncode == 0, (
            "ebump failed with output:\n" + result.stdout + "\n" + result.stderr
        )
        assert (project / "pyproject.toml").read_text(newline="") == (
            '[project]\nversion = "1.0.1"\n# here 1.0.1 also 1.0.1 here\n\n[tool.ebump.patterns]\n"pyproject.toml" = ["^# here {version} also {version} here$"]\n'
        )
