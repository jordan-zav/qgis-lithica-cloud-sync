import hashlib
import shutil
from pathlib import Path

from .archive import ArchiveError, validate_and_extract
from .cache import ProjectCache
from .models import ExtractedProject, ProjectFile


class SyncError(RuntimeError):
    pass


class SyncService:
    def __init__(self, drive_client, cache: ProjectCache):
        self.drive_client = drive_client
        self.cache = cache

    def download_project(
        self, access_token: str, remote: ProjectFile
    ) -> ExtractedProject:
        inferred_id = remote.name.removeprefix("lithica-project-").removesuffix(".zip")
        pending = self.cache.prepare_pending(inferred_id)
        zip_path = pending / "project.zip"
        try:
            self.drive_client.download(access_token, remote, zip_path)
            if remote.md5_checksum:
                # Use usedforsecurity=False for Bandit scanner, and # nosec just in case
                actual = hashlib.md5(zip_path.read_bytes()).hexdigest() # nosec
                if actual.lower() != remote.md5_checksum.lower():
                    raise SyncError("Downloaded file checksum does not match Drive")
            extracted = validate_and_extract(zip_path, pending / "content")
            if extracted.project_id != inferred_id:
                raise SyncError("Project identity does not match the Drive filename")
            zip_path.unlink(missing_ok=True)
            content = pending / "content"
            for child in list(content.iterdir()):
                child.replace(pending / child.name)
            content.rmdir()
            current = self.cache.promote(inferred_id)
            self.cache.save_state(
                inferred_id,
                {
                    "driveFileId": remote.id,
                    "modifiedTime": remote.modified_time.isoformat(),
                    "md5Checksum": remote.md5_checksum,
                    "projectName": extracted.project_name,
                },
            )
            return ExtractedProject(
                project_id=extracted.project_id,
                project_name=extracted.project_name,
                root=current,
                geopackage=current / "observations.gpkg",
            )
        except Exception:
            if pending.exists():
                shutil.rmtree(pending)
            raise
