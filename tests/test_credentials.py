from datetime import datetime, timezone

from lithica_drive_sync.credential_store import MemoryCredentialStore
from lithica_drive_sync.oauth import TokenSet


def test_memory_store_round_trips_and_clears_token():
    store = MemoryCredentialStore()
    token = TokenSet(
        access_token="access",
        refresh_token="refresh",
        expires_at=datetime(2026, 6, 27, tzinfo=timezone.utc),
    )

    store.save(token)
    assert store.load() == token

    store.clear()
    assert store.load() is None
