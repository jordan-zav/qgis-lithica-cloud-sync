import json

import pytest

from lithica_drive_sync.config import ConfigError, load_oauth_config


def test_loads_desktop_oauth_client(tmp_path):
    path = tmp_path / "oauth_client.json"
    path.write_text(
        json.dumps(
            {
                "installed": {
                    "client_id": "client.apps.googleusercontent.com",
                    "project_id": "lithica-dev",
                    "client_secret": "desktop-secret",
                }
            }
        ),
        encoding="utf-8",
    )

    config = load_oauth_config(path)

    assert config.client_id == "client.apps.googleusercontent.com"
    assert config.project_id == "lithica-dev"
    assert config.client_secret == "desktop-secret"


def test_rejects_service_account_config(tmp_path):
    path = tmp_path / "oauth_client.json"
    path.write_text(
        json.dumps({"type": "service_account", "private_key": "secret"}),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="service account"):
        load_oauth_config(path)
