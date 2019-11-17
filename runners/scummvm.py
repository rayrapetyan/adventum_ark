from pathlib import Path

from conf.conf import *

from _utils.misc import (
    cmd_exec,
)

from runners.base_runner import BaseRunner

class ScummVM(BaseRunner):
    def __init__(self, title):
        super().__init__(title)

    def __del__(self):
        super(ScummVM, self).__del__()

    def run(self):
        conf_path = Path(SCUMMVM_CONF_PATH)
        _, stderr = cmd_exec(f"scummvm --config={conf_path} --game={self.conf['scummvm_gameid']} --path={self.game_path} --savepath={self.saves_path} --auto-detect")
        if stderr:
            print(f"scummvm errors: {stderr}")
