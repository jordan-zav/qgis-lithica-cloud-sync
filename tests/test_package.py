import subprocess
import zipfile
from pathlib import Path


def test_package_uses_portable_zip_paths():
    plugin_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(plugin_root / "package_plugin.ps1"),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    target = plugin_root.parent / "artifacts" / "lithica_drive_sync-0.1.0.zip"

    with zipfile.ZipFile(target) as package:
        names = package.namelist()

    assert "lithica_drive_sync/metadata.txt" in names
    assert not any("\\" in name for name in names)
