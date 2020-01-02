from pathlib import Path

from conf.conf import *

from _utils.md import MemDisk
from _utils.misc import (
    cmd_exec,
    eval_path,
    gen_win_reg_file,
    restore_screen_resolution,
    set_screen_resolution,
)

from runners.base_runner import BaseRunner


class Wine(BaseRunner):
    def __init__(self, title):
        super().__init__(title)
        self.env_path = Path(WINE_ENVS_BASE_PATH) / self.conf.get("wine_env", "win95")

        self.games_path = self.env_path / "drive_c" / "games"
        if not self.games_path.exists():
            self.games_path.symlink_to(GAMES_BASE_PATH)

        self.memdisks = []
        self.drives = []

    def __del__(self):
        self.unmount()
        restore_screen_resolution()
        post_cmd = self.conf.get("post_cmd", None)
        if post_cmd:
            _, stderr = cmd_exec(post_cmd)
            if stderr:
                print(f"post_cmd errors: {stderr}")
        super(Wine, self).__del__()

    def run_wine_cmd(self, cmd, cwd=None):
        env = os.environ.copy()
        env["WINEPREFIX"] = str(self.env_path)
        _, stderr = cmd_exec(f'wine {cmd}', env=env, cwd=cwd)
        if stderr:
            print(f"wine errors: {stderr}")

    def upd_reg(self, key, subkey, value):
        reg_file = gen_win_reg_file(key, subkey, value)
        self.run_wine_cmd(f"regedit {reg_file}")

    def remove_drive(self, path):
        _, stderr = cmd_exec(f"rm {path}")
        if stderr:
            raise Exception(f"error removing drive: {stderr}")

    def add_drive(self, letter, path_dst):
        print(f"adding drive {letter} -> {path_dst}")
        path_src = Path(WINE_ENVS_BASE_PATH) / self.env_path / "dosdevices" / str(letter + ":")
        if path_src.exists():
            self.remove_drive(path_src)
        Path(path_src).symlink_to(path_dst)
        return path_src

    def mount(self):
        cdrom_first_letter = self.conf.get("cdrom_first_letter", "d")
        if self.cdrom_folder:
            self.add_drive(cdrom_first_letter, self.cdrom_folder)
            return
        images = self.conf.get("images", [])
        for i in range(len(images)):
            img_path = Path(IMAGES_STORAGE_PATH) / self.title / images[i]
            md = MemDisk(img_path, i)
            mnt_path = md.mount()
            self.memdisks.append(md)
            self.drives.append(self.add_drive(cdrom_first_letter, mnt_path))
            cdrom_first_letter = chr(ord(cdrom_first_letter[0]) + 1)

    def unmount(self):
        for d in self.drives:
            self.remove_drive(d)
        # the rest will happen in MemDisk dtor's

    def run(self):
        self.mount()

        if "screen_resolution" in self.conf:
            set_screen_resolution(self.conf["screen_resolution"])

        pre_cmd = self.conf.get("pre_cmd", None)
        if pre_cmd:
            _, stderr = cmd_exec(pre_cmd)
            if stderr:
                print(f"pre_cmd errors: {stderr}")

        cwd = eval_path(Path(self.conf.get("cwd", self.game_path)), self.env)

        self.run_wine_cmd(
            cmd=f'"{self.conf["exec_file"]}"',
            cwd=str(cwd)
        )
