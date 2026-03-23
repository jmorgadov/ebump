from pathlib import Path

ROOT_IDENTIFIERS = ["pyproject.toml", ".git"]


def project_root() -> Path:
    """Get the project root directory"""

    current_dir = Path.cwd()
    while current_dir != current_dir.parent:
        if any((current_dir / identifier).exists() for identifier in ROOT_IDENTIFIERS):
            return current_dir
        current_dir = current_dir.parent
    return Path.cwd()
