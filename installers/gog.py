from pathlib import Path

from conf.conf import *
from installers.base_installer import BaseInstaller
from _utils.misc import (
    cmd_exec,
    copy_ex,
    rm_dir,
)


class Gog(BaseInstaller):
    def __init__(self, title):
        super().__init__(title)

    def extract(self):
        tmp_path = Path("/tmp") / self.title
        if tmp_path.exists():
            rm_dir(tmp_path)
        installer_path = Path(IMAGES_STORAGE_PATH) / self.title / self.conf["installer"]
        _, stderr = cmd_exec(f"innoextract --extract --exclude-temp --color --progress --gog --output-dir {tmp_path} {installer_path}")
        if stderr:
            print(f"innoextract error: {stderr}")
        for file in self.conf["app_files"]:
            copy_ex(tmp_path / file, self.game_path)
        rm_dir(tmp_path)

    def install(self):
        self.extract()
        self.handle_saves()
        self.patch()
