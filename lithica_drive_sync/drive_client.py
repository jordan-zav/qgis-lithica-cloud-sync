import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

from .config import FOLDER_NAME, PROJECT_PREFIX
from .models import ProjectFile


class DriveError(RuntimeError):
    pass


class DriveClient:
    def __init__(self, opener=None, timeout=60):
        self._opener = opener or urllib.request.urlopen
        self._timeout = timeout

    def list_projects(self, access_token: str) -> list[ProjectFile]:
        folder_query = (
            "mimeType='application/vnd.google-apps.folder' "
            f"and name='{FOLDER_NAME}' and trashed=false"
        )
        folders = self._list(access_token, folder_query, "files(id)")
        if not folders:
            return []
        folder_id = folders[0]["id"]
        query = (
            f"'{folder_id}' in parents and trashed=false "
            "and mimeType='application/zip'"
        )
        rows = self._list(
            access_token,
            query,
            "nextPageToken,files(id,name,modifiedTime,size,md5Checksum)",
        )
        result = []
        for row in rows:
            name = str(row.get("name", ""))
            if not name.startswith(PROJECT_PREFIX) or not name.endswith(".zip"):
                continue
            result.append(
                ProjectFile(
                    id=str(row["id"]),
                    name=name,
                    modified_time=datetime.fromisoformat(
                        str(row["modifiedTime"]).replace("Z", "+00:00")
                    ),
                    size=int(row.get("size", 0)),
                    md5_checksum=row.get("md5Checksum"),
                )
            )
        return sorted(result, key=lambda item: item.modified_time, reverse=True)

    def download(self, access_token: str, file: ProjectFile, target: Path) -> Path:
        url = f"https://www.googleapis.com/drive/v3/files/{file.id}?alt=media"
        request = urllib.request.Request(
            url, headers={"Authorization": f"Bearer {access_token}"}, method="GET"
        )
        target = Path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self._opener(request, timeout=self._timeout) as response:
                with target.open("wb") as output:
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        output.write(chunk)
        except (OSError, urllib.error.HTTPError) as error:
            target.unlink(missing_ok=True)
            raise DriveError(f"Drive download failed: {error}") from error
        return target

    def _list(self, token: str, query: str, fields: str) -> list[dict]:
        rows = []
        page_token = None
        while True:
            params = {"q": query, "spaces": "drive", "fields": fields, "pageSize": 100}
            if page_token:
                params["pageToken"] = page_token
            url = "https://www.googleapis.com/drive/v3/files?" + urllib.parse.urlencode(
                params
            )
            request = urllib.request.Request(
                url, headers={"Authorization": f"Bearer {token}"}, method="GET"
            )
            try:
                with self._opener(request, timeout=self._timeout) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            except (OSError, ValueError, urllib.error.HTTPError) as error:
                raise DriveError(f"Drive request failed: {error}") from error
            rows.extend(payload.get("files", []))
            page_token = payload.get("nextPageToken")
            if not page_token:
                return rows
