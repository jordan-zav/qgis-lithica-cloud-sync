import json
from dataclasses import dataclass
from pathlib import Path

DRIVE_FILE_SCOPE = "https://www.googleapis.com/auth/drive.file"
FOLDER_NAME = "Lithica Explorer"
PROJECT_PREFIX = "lithica-project-"


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class OAuthConfig:
    client_id: str
    project_id: str
    client_secret: str = ""


def load_oauth_config(path: Path) -> OAuthConfig:
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ConfigError(f"OAuth configuration is unavailable: {error}") from error
    if raw.get("type") == "service_account" or "private_key" in raw:
        raise ConfigError("A service account configuration is not allowed")
    installed = raw.get("installed")
    if not isinstance(installed, dict):
        raise ConfigError("An installed desktop OAuth client is required")
    client_id = str(installed.get("client_id", "")).strip()
    project_id = str(installed.get("project_id", "")).strip()
    client_secret = str(installed.get("client_secret", "")).strip()
    if not client_id or not project_id:
        raise ConfigError("client_id and project_id are required")
    return OAuthConfig(
        client_id=client_id,
        project_id=project_id,
        client_secret=client_secret,
    )
