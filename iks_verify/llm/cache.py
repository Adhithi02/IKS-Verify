import hashlib
from pathlib import Path


class DiskCache:
    def __init__(self, directory: Path) -> None:
        self.directory = directory
        directory.mkdir(parents=True, exist_ok=True)

    def _path(self, prompt: str) -> Path:
        return self.directory / f"{hashlib.sha256(prompt.encode()).hexdigest()}.txt"

    def get(self, prompt: str) -> str | None:
        path = self._path(prompt)
        return path.read_text(encoding="utf-8") if path.exists() else None

    def set(self, prompt: str, result: str) -> None:
        self._path(prompt).write_text(result, encoding="utf-8")
