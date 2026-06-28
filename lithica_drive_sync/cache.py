import json
import shutil
from pathlib import Path


class CacheError(ValueError):
    pass


class ProjectCache:
    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def project_root(self, project_id: str) -> Path:
        safe = "".join(c for c in project_id if c.isalnum() or c in "._-")
        if not safe:
            raise CacheError("Invalid project id")
        return self.root / safe

    def prepare_pending(self, project_id: str) -> Path:
        pending = self.project_root(project_id) / "pending"
        if pending.exists():
            shutil.rmtree(pending)
        pending.mkdir(parents=True)
        return pending

    def promote(self, project_id: str) -> Path:
        project = self.project_root(project_id)
        pending, current = project / "pending", project / "current"
        if not pending.is_dir():
            raise CacheError("Pending project does not exist")
        previous = project / "previous"
        if previous.exists():
            shutil.rmtree(previous)
        if current.exists():
            current.rename(previous)
        try:
            pending.rename(current)
        except OSError:
            if previous.exists() and not current.exists():
                previous.rename(current)
            raise
        if previous.exists():
            shutil.rmtree(previous)
        return current

    def save_state(self, project_id: str, state: dict) -> None:
        path = self.project_root(project_id) / "state.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(state, indent=2), encoding="utf-8")
        temp.replace(path)

    def clear_path(self, path: Path) -> None:
        resolved = Path(path).resolve()
        if resolved != self.root and self.root not in resolved.parents:
            raise CacheError("Refusing to clear a path outside cache")
        if resolved.exists():
            shutil.rmtree(resolved, ignore_errors=True)
