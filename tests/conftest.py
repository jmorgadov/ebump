import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent


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
