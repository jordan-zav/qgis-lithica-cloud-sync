from pathlib import Path


def test_metadata_declares_experimental_qgis_plugin():
    path = (
        Path(__file__).resolve().parents[1]
        / "lithica_drive_sync"
        / "metadata.txt"
    )
    text = path.read_text(encoding="utf-8")

    assert "name=Lithica Drive Sync" in text
    assert "qgisMinimumVersion=3.34" in text
    assert "experimental=True" in text
