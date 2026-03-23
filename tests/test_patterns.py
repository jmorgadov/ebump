from conftest import make_pyproject, run_ebump


class TestPatterns:
    def test_pattern_simple(self, project):
        make_pyproject(
            "1.0.0",
            project,
            patterns=[r'"custom_file.md" = ["^version = {version}$"]'],
            custom_files=[("custom_file.md", "version = 1.0.0")],
        )
        run_ebump(["patch"], project)
        assert (project / "custom_file.md").read_text() == "version = 1.0.1"

    def test_pattern_multiple_on_same_line(self, project):
        make_pyproject(
            "1.0.0",
            project,
            patterns=[r'"custom_file.md" = ["^version = {version} and {version}$"]'],
            custom_files=[("custom_file.md", "version = 1.0.0 and 1.0.0")],
        )
        run_ebump(["patch"], project)
        assert (project / "custom_file.md").read_text() == "version = 1.0.1 and 1.0.1"

    def test_multiple_but_only_change_one(self, project):
        make_pyproject(
            "1.0.0",
            project,
            patterns=[r'"custom_file.md" = ["^version = {version}.*"]'],
            custom_files=[("custom_file.md", "version = 1.0.0 version = 1.0.0")],
        )
        run_ebump(["patch"], project)
        assert (
            project / "custom_file.md"
        ).read_text() == "version = 1.0.1 version = 1.0.0"

    def test_pattern_not_found(self, project):
        make_pyproject(
            "1.0.0",
            project,
            patterns=[r'"custom_file.md" = ["^version = {version}$"]'],
            custom_files=[("custom_file.md", "version: 1.0.0")],
        )
        result = run_ebump(["patch"], project)
        assert result.returncode != 0
        assert "Some patterns were not found" in result.stderr

    def test_pattern_does_not_contain_placeholder(self, project):
        make_pyproject(
            "1.0.0",
            project,
            patterns=[r'"custom_file.md" = ["^version = 1.0.0$"]'],
            custom_files=[("custom_file.md", "version = 1.0.0")],
        )
        result = run_ebump(["patch"], project)
        assert result.returncode != 0
        assert "does not contain '{version}' placeholder" in result.stderr
