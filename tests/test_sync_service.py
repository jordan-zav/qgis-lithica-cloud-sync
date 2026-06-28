import hashlib
import json
import zipfile
from datetime import datetime, timezone

from lithica_drive_sync.cache import ProjectCache
from lithica_drive_sync.models import ProjectFile
from lithica_drive_sync.sync_service import SyncService


class FakeDrive:
    def __init__(self, source):
        self.source = source

    def download(self, token, project, target):
        target.write_bytes(self.source.read_bytes())
        return target


def test_download_validate_and_promote(tmp_path):
    source = tmp_path / "remote.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr(
            "manifest.json",
            json.dumps(
                {
                    "syncSchema": "lithica.drive.sync.v1",
                    "projectId": "p1",
                    "projectName": "Project One",
                }
            ),
        )
        archive.writestr("observations.gpkg", b"SQLite format 3\x00")
    checksum = hashlib.md5(source.read_bytes()).hexdigest()
    remote = ProjectFile(
        id="file1",
        name="lithica-project-p1.zip",
        modified_time=datetime(2026, 6, 27, tzinfo=timezone.utc),
        size=source.stat().st_size,
        md5_checksum=checksum,
    )
    service = SyncService(FakeDrive(source), ProjectCache(tmp_path / "cache"))

    local = service.download_project("token", remote)

    assert local.project_id == "p1"
    assert local.geopackage.exists()
    assert local.geopackage.parent.name == "current"
