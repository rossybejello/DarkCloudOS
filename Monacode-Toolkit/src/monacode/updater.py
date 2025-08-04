import sys
import subprocess
import json
import shutil
import tempfile
from pathlib import Path
from typing import Optional

import requests

from .utils import EnvManager


PYPI_JSON_URL = "https://pypi.org/pypi/monacode-toolkit/json"
GITHUB_API_RELEASES = "https://api.github.com/repos/rossybejello/DarkCloudOS/releases/latest"


class UpdateError(Exception):
    pass


class Updater:
    """
    Self-update capabilities: compare versions and install updates via PyPI or GitHub.
    """

    def __init__(self):
        self.env = EnvManager()
        from . import __version__ as current
        self.current_version = current

    def get_latest_pypi_version(self) -> str:
        """
        Fetch latest version from PyPI JSON API.
        """
        resp = requests.get(PYPI_JSON_URL, timeout=10)
        data = resp.json()
        return data["info"]["version"]

    def get_latest_github_version(self) -> Dict[str, str]:
        """
        Fetch latest GitHub release tag and download URL.
        """
        resp = requests.get(GITHUB_API_RELEASES, timeout=10)
        release = resp.json()
        return {
            "tag_name": release["tag_name"],
            "zipball_url": release["zipball_url"]
        }

    def update_via_pypi(self) -> None:
        """
        Upgrade package with pip.
        """
        latest = self.get_latest_pypi_version()
        if latest == self.current_version:
            print(f"Already up to date (v{latest}).")
            return
        print(f"Updating Monacode Toolkit: {self.current_version} → {latest}")
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "monacode-toolkit"]
        subprocess.check_call(cmd)
        print("Update complete.")

    def update_via_github(self, target_dir: Optional[str] = None) -> None:
        """
        Download latest source from GitHub, replace local install.
        """
        info = self.get_latest_github_version()
        tag = info["tag_name"]
        url = info["zipball_url"]
        print(f"Fetching GitHub release {tag}...")
        tmpdir = Path(tempfile.mkdtemp())
        archive = tmpdir / "release.zip"
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            archive.write_bytes(r.content)
        # Extract
        extract_dir = tmpdir / "src"
        shutil.unpack_archive(str(archive), str(extract_dir))
        # Find inner folder
        inner = next(extract_dir.iterdir())
        dest = Path(target_dir or Path(__file__).parents[2])
        # Copy files
        for item in inner.iterdir():
            dst = dest / item.name
            if dst.exists():
                if dst.is_dir():
                    shutil.rmtree(dst)
                else:
                    dst.unlink()
            if item.is_dir():
                shutil.copytree(item, dst)
            else:
                shutil.copy2(item, dst)
        print(f"Monacode Toolkit updated to {tag} via GitHub.")

    def choose_update(self, method: Optional[str] = None) -> None:
        """
        Prompt or auto-select update path.
        """
        method = method or self.env.get("MONACODE_UPDATE_METHOD", "pypi")
        if method == "pypi":
            self.update_via_pypi()
        elif method == "github":
            self.update_via_github()
        else:
            raise UpdateError(f"Unknown update method: {method}")
