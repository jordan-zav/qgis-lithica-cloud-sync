from pathlib import Path

import pytest

from lithica_drive_sync.cache import CacheError, ProjectCache


def test_promote_replaces_current_atomically(tmp_path):
    cache = ProjectCache(tmp_path)
    pending = cache.prepare_pending("p1")
    (pending / "observations.gpkg").write_bytes(b"new")

    current = cache.promote("p1")

    assert (current / "observations.gpkg").read_bytes() == b"new"
    assert not pending.exists()


def test_clear_rejects_path_outside_cache(tmp_path):
    cache = ProjectCache(tmp_path / "cache")
    outside = tmp_path / "outside"
    outside.mkdir()

    with pytest.raises(CacheError, match="outside"):
        cache.clear_path(outside)
