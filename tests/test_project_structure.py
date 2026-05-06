from pathlib import Path

REQUIRED_PATHS = [
    "backend",
    "frontend",
    "src",
    "tests",
    "requirements.txt",
    "pyproject.toml",
]

FORBIDDEN_IN_BACKEND = [
    "train.py",
    "pipeline.py",
    "notebook.ipynb",
]


def test_required_paths_exist():
    root = Path(".")
    missing = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    assert not missing, f"Elements manquants dans le projet: {missing}"


def test_backend_does_not_contain_training_code():
    backend = Path("backend")
    if not backend.exists():
        return
    backend_files = [path.name for path in backend.rglob("*") if path.is_file()]
    forbidden = [name for name in FORBIDDEN_IN_BACKEND if name in backend_files]
    assert not forbidden, f"Code de training detecte dans backend: {forbidden}"
