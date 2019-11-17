from pathlib import Path

from conf.conf import *
from _utils.misc import (
    copy_ex,
    eval_path,
)


class BaseRunner:
    def __init__(self, title):
        self.title = title
        self.conf = GAMES_CONF[title]["run"]
        self.game_path = Path(GAMES_BASE_PATH) / title
        assert(self.game_path.exists())
        self.saves_path = Path(SAVES_BASE_PATH) / title
        assert(self.saves_path.exists())
        self.env = {
            "GAME_PATH": str(self.game_path),
            "SAVES_PATH": str(self.saves_path)
        }
        self.conf["copy_saves"] = GAMES_CONF[title].get("copy_saves", None)

        self.cdrom_folder = self.conf.get("cdrom_folder", None)
        if self.cdrom_folder:
            self.cdrom_folder = eval_path(self.cdrom_folder, self.env)

    def __del__(self):
        if self.conf["copy_saves"]:
            # stupid game stores saves in its working dir, so we have to copy them back and forth
            portable_saves_path = Path(SAVES_BASE_PATH) / self.title
            actual_saves = eval_path(self.conf["copy_saves"], self.env)
            copy_ex(actual_saves, portable_saves_path)
