import json
import zipfile

import pytest

from lithica_drive_sync.archive import ArchiveError, validate_and_extract


def _write_zip(path, entries):
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in entries.items():
            archive.writestr(name, content)


def test_extracts_valid_lithica_project(tmp_path):
    source = tmp_path / "project.zip"
    _write_zip(
        source,
        {
            "manifest.json": json.dumps(
                {
                    "syncSchema": "lithica.drive.sync.v1",
                    "projectId": "p1",
                    "projectName": "Project One",
                }
            ),
            "observations.gpkg": b"SQLite format 3\x00",
        },
    )

    result = validate_and_extract(source, tmp_path / "out")

    assert result.project_id == "p1"
    assert result.geopackage.name == "observations.gpkg"


def test_rejects_path_traversal(tmp_path):
    source = tmp_path / "project.zip"
    _write_zip(
        source,
        {
            "../escape.txt": b"bad",
            "manifest.json": b"{}",
            "observations.gpkg": b"x",
        },
    )

    with pytest.raises(ArchiveError, match="unsafe"):
        validate_and_extract(source, tmp_path / "out")


def test_rejects_unknown_schema(tmp_path):
    source = tmp_path / "project.zip"
    _write_zip(
        source,
        {
            "manifest.json": json.dumps(
                {
                    "syncSchema": "unknown",
                    "projectId": "p1",
                    "projectName": "Project One",
                }
            ),
            "observations.gpkg": b"x",
        },
    )

    with pytest.raises(ArchiveError, match="schema"):
        validate_and_extract(source, tmp_path / "out")
