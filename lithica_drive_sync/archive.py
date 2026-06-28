import json
import shutil
import zipfile
from pathlib import Path, PurePosixPath

from .models import ExtractedProject

EXPECTED_SCHEMA = "lithica.drive.sync.v1"


class ArchiveError(ValueError):
    pass


def validate_and_extract(
    source: Path,
    destination: Path,
    max_compressed: int = 2 * 1024**3,
    max_extracted: int = 5 * 1024**3,
    max_entries: int = 20_000,
) -> ExtractedProject:
    source, destination = Path(source), Path(destination)
    if source.stat().st_size > max_compressed:
        raise ArchiveError("Archive exceeds compressed size limit")
    try:
        archive = zipfile.ZipFile(source)
    except (OSError, zipfile.BadZipFile) as error:
        raise ArchiveError(f"Invalid ZIP archive: {error}") from error
    with archive:
        entries = archive.infolist()
        if len(entries) > max_entries:
            raise ArchiveError("Archive has too many entries")
        names = set()
        total = 0
        for entry in entries:
            normalized = entry.filename.replace("\\", "/")
            path = PurePosixPath(normalized)
            if (
                path.is_absolute()
                or ".." in path.parts
                or not normalized
                or normalized in names
                or _is_symlink(entry)
            ):
                raise ArchiveError(f"Archive contains unsafe entry: {entry.filename}")
            names.add(normalized)
            total += entry.file_size
            if total > max_extracted:
                raise ArchiveError("Archive exceeds extracted size limit")
        required = {"manifest.json", "observations.gpkg"}
        if not required.issubset(names):
            raise ArchiveError("Archive lacks manifest.json or observations.gpkg")
        try:
            manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
        except (KeyError, UnicodeError, ValueError) as error:
            raise ArchiveError(f"Invalid manifest: {error}") from error
        if manifest.get("syncSchema") != EXPECTED_SCHEMA:
            raise ArchiveError("Unsupported synchronization schema")
        project_id = str(manifest.get("projectId", "")).strip()
        project_name = str(manifest.get("projectName", "")).strip()
        if not project_id or not project_name:
            raise ArchiveError("Manifest lacks project identity")
        if destination.exists():
            shutil.rmtree(destination)
        destination.mkdir(parents=True)
        archive.extractall(destination)
    return ExtractedProject(
        project_id=project_id,
        project_name=project_name,
        root=destination,
        geopackage=destination / "observations.gpkg",
    )


def _is_symlink(entry: zipfile.ZipInfo) -> bool:
    return ((entry.external_attr >> 16) & 0o170000) == 0o120000
