import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent


def make_pyproject(
    version: str,
    tmp_path: Path,
    patterns: None | list[str] = None,
    custom_files: None | list[tuple[str, str]] = None,
    custom_pyproject_content: None | str = None,
) -> None:
    """Write a minimal pyproject.toml with bumpver configured."""
    content = custom_pyproject_content or textwrap.dedent(
        f"""\
        [project]
        name = "mypackage"
        version = "{version}"
    """
    )
    if patterns is not None:
        content += "\n\n[tool.ebump.patterns]\n"
        for pattern in patterns:
            content += f"{pattern}\n"

    (tmp_path / "pyproject.toml").write_text(content, newline="")

    if custom_files is not None:
        for filename, file_content in custom_files:
            (tmp_path / filename).write_text(file_content, newline="")


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


@pytest.fixture(scope="session", autouse=True)
def combine_coverage():
    """
    Combine coverage data files after all tests have run, and clean up the
    individual files.
    """
    yield
    subprocess.run(  # noqa: S603
        [  # noqa: S607
            "coverage",
            "combine",
            "--data-file",
            str((PROJECT_ROOT / ".coverage").absolute()),
        ],
        cwd=str(PROJECT_ROOT),
        check=False,
    )
    for f in PROJECT_ROOT.glob(".coverage.*"):
        f.unlink()


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
