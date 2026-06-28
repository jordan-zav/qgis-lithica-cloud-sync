import io
import json

from lithica_drive_sync.drive_client import DriveClient


class FakeResponse:
    def __init__(self, payload=b"", status=200, headers=None):
        self._payload = payload
        self.status = status
        self.headers = headers or {}

    def read(self, size=-1):
        return self._payload if size == -1 else self._payload[:size]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_lists_only_lithica_zip_files():
    calls = []
    responses = iter(
        [
            FakeResponse(
                json.dumps({"files": [{"id": "folder"}]}).encode()
            ),
            FakeResponse(
                json.dumps(
                    {
                        "files": [
                            {
                                "id": "f1",
                                "name": "lithica-project-p1.zip",
                                "modifiedTime": "2026-06-27T10:00:00Z",
                                "size": "10",
                                "md5Checksum": "abc",
                            }
                        ]
                    }
                ).encode()
            ),
        ]
    )

    def opener(request, timeout):
        calls.append(request.full_url)
        return next(responses)

    files = DriveClient(opener=opener).list_projects("token")

    assert [item.name for item in files] == ["lithica-project-p1.zip"]
    assert all("upload" not in url for url in calls)
