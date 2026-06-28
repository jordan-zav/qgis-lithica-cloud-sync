import json
from abc import ABC, abstractmethod
from datetime import datetime

from .oauth import TokenSet


class CredentialStore(ABC):
    @abstractmethod
    def load(self) -> TokenSet | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, token: TokenSet) -> None:
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        raise NotImplementedError


class MemoryCredentialStore(CredentialStore):
    def __init__(self):
        self._token = None

    def load(self) -> TokenSet | None:
        return self._token

    def save(self, token: TokenSet) -> None:
        self._token = token

    def clear(self) -> None:
        self._token = None


class QgisCredentialStore(CredentialStore):
    SETTINGS_KEY = "lithica_drive_sync/auth_config_id"

    def __init__(self):
        from qgis.core import QgsApplication, QgsAuthMethodConfig, QgsSettings

        self._manager = QgsApplication.authManager()
        self._config_type = QgsAuthMethodConfig
        self._settings = QgsSettings()
        self._memory = MemoryCredentialStore()

    def load(self) -> TokenSet | None:
        config_id = self._settings.value(self.SETTINGS_KEY, "", type=str)
        if not config_id:
            return self._memory.load()
        config = self._config_type()
        if not self._manager.loadAuthenticationConfig(config_id, config, True):
            return self._memory.load()
        try:
            payload = json.loads(config.config("password"))
            return TokenSet(
                access_token=payload["access_token"],
                refresh_token=payload.get("refresh_token"),
                expires_at=datetime.fromisoformat(payload["expires_at"]),
            )
        except (KeyError, TypeError, ValueError):
            return None

    def save(self, token: TokenSet) -> None:
        self._memory.save(token)
        if not token.refresh_token or self._manager.masterPasswordIsSet() is False:
            return
        payload = json.dumps(
            {
                "access_token": token.access_token,
                "refresh_token": token.refresh_token,
                "expires_at": token.expires_at.isoformat(),
            }
        )
        config = self._config_type()
        config.setName("Lithica Drive Sync OAuth")
        config.setMethod("Basic")
        config.setConfig("username", "oauth")
        config.setConfig("password", payload)
        existing = self._settings.value(self.SETTINGS_KEY, "", type=str)
        if existing:
            config.setId(existing)
            stored = self._manager.updateAuthenticationConfig(config)
        else:
            stored = self._manager.storeAuthenticationConfig(config)
        if stored:
            self._settings.setValue(self.SETTINGS_KEY, config.id())

    def clear(self) -> None:
        self._memory.clear()
        config_id = self._settings.value(self.SETTINGS_KEY, "", type=str)
        if config_id:
            self._manager.removeAuthenticationConfig(config_id)
        self._settings.remove(self.SETTINGS_KEY)
