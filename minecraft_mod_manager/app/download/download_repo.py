from pathlib import Path
from typing import Union

from ...core.entities.mod import Mod, ModArg
from ...core.entities.version_info import VersionInfo


class DownloadRepo:
    def get_latest_version(self, mod: ModArg) -> VersionInfo:
        raise NotImplementedError()

    def download(self, url: str, filename: str = "") -> Path:
        raise NotImplementedError()

    def get_mod(self, mod: ModArg) -> Union[Mod, None]:
        raise NotImplementedError()

    def update_mod(self, mod: Mod) -> None:
        raise NotImplementedError()