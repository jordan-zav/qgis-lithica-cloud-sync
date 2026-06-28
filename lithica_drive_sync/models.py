from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class ProjectFile:
    id: str
    name: str
    modified_time: datetime
    size: int
    md5_checksum: str | None = None


@dataclass(frozen=True)
class ExtractedProject:
    project_id: str
    project_name: str
    root: Path
    geopackage: Path
