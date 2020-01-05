from distutils.util import strtobool
from pathlib import Path

from conf.conf import *
from runners.wine import Wine
from _utils.misc import (
    cmd_exec,
    copy_ex,
    eval_path,
    find_replace_text,
    get_var_val_by_name,
    rm_dir,
)


class BaseInstaller:
    def __init__(self, title):
        self.title = title
        self.game_path = Path(GAMES_BASE_PATH) / title
        if not TEST:
            if self.game_path.exists():
                if not strtobool(input("title is already installed, do you want to perform a re-install? (all saved data will be preserved) (yes/no): ")):
                    raise Exception(f"title is already installed, ya should perform 'rm -rf {self.game_path}' first")
                rm_dir(self.game_path)
            self.game_path.mkdir(parents=True)

        self.env = {
            "GAME_PATH": str(self.game_path)
        }
        if GAMES_CONF[title]["run"]["engine"] == "wine":
            self.env["WINE_ENV_PATH"] = str(Path(WINE_ENVS_BASE_PATH) / GAMES_CONF[title]["run"].get("wine_env", "win95"))
        self.conf = GAMES_CONF[title]["install"]
        self.conf["copy_saves"] = GAMES_CONF[title].get("copy_saves", None)

    def handle_saves(self):
        portable_saves_path = Path(SAVES_BASE_PATH) / self.title
        portable_saves_path.mkdir(parents=True, exist_ok=True)
        copy_saves = self.conf["copy_saves"]
        if copy_saves:
            # stupid game stores saves in its working dir, so we have to copy them back and forth
            copy_saves = eval_path(copy_saves, self.env)
            portable_saves = portable_saves_path / copy_saves.name
            copy_ex(portable_saves, self.game_path)
            return portable_saves_path
        actual_saves_path = self.conf.get("saves_path", None)
        if actual_saves_path:
            actual_saves_path = eval_path(actual_saves_path, self.env)
            if actual_saves_path.exists():
                if actual_saves_path.is_symlink():
                    return portable_saves_path
                # some games depends on existing files in saves folder even on a first run (faust)
                if os.listdir(str(actual_saves_path)) and not os.listdir(str(portable_saves_path)):
                    copy_ex(actual_saves_path / "*", portable_saves_path)
                rm_dir(actual_saves_path)
            actual_saves_path.parent.mkdir(parents=True, exist_ok=True)
            print(f"creating a symlink: {actual_saves_path}->{portable_saves_path}")
            actual_saves_path.symlink_to(portable_saves_path)
        return portable_saves_path

    def perform_bspatch(self, target_file, patch_file):
        tmp_file = Path(str(target_file) + ".tmp")
        _, stderr = cmd_exec(f"bspatch {target_file} {tmp_file} {patch_file}")
        if stderr:
            raise Exception(f"error patching file: {stderr}")
        tmp_file.replace(target_file)

    def patch(self):
        patches = self.conf.get("patches", {})
        for op, files in patches.items():
            if op == "bspatch":
                for file, patch_file in files.items():
                    target_file = eval_path(Path(file), self.env)
                    self.perform_bspatch(target_file, Path(PATCHES_BASE_PATH) / self.title / patch_file)
            elif op == "copy_file":
                for dst_dir, patch_files in files.items():
                    dst_dir = eval_path(dst_dir, self.env)
                    for p_file in patch_files:
                        p_file = Path(PATCHES_BASE_PATH) / self.title / p_file
                        copy_ex(p_file, dst_dir)
            elif op == "find_replace_text":
                for file, replaces in files.items():
                    target_file = eval_path(Path(file), self.env)
                    for repl in replaces:
                        if "eval" in repl:
                            find = f"{{{repl['eval']}}}"
                            replace = get_var_val_by_name(repl['eval'])
                        else:
                            find = repl["find"]
                            replace = repl["replace"]
                        find_replace_text(target_file, find, replace)
            elif op == "regedit":
                Wine(self.title).upd_reg(files)
            else:
                raise Exception(f"unknown patch type: {op}")
