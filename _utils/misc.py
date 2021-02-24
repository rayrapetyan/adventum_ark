import glob
import re
import shlex
import shutil
import subprocess

from distutils.dir_util import copy_tree
from pathlib import Path
from typing import (
    Dict,
)


def copy_ex(src: Path, dst: Path) -> None:
    """
    Copy src to dst evaluating paths

    :param src: source path (file, dir or mask)
    :param dst: destination path (file or dir)
    :return: None

    ex:
    src: /a/dir
    dst: /b
    copies all files from /a/dir to /b/dir overwriting existing files and creating a new dir

    src: /a/dir/*
    dst: /b/dir
    same as above

    src: /a/dir/*
    dst: /b
    copies all files from /a/dir to /b overwriting existing files and creating new dirs

    src: /a/file
    dst: /b/file
    copies file /a/file to /b/file overwriting existing file

    src: /a/file
    dst: /b/dir
    copies file /a/file to /b/dir/file overwriting existing file
    """
    if "*" in str(src):
        print(f"copying {src} to {dst}")
        for file in glob.glob(str(src)):
            file = Path(file)
            copy_ex(file, dst)
    elif src.is_dir():
        d = dst / src.name
        print(f"copying {src} to {d}")
        copy_tree(str(src), str(d))
    else:
        print(f"copying {src} to {dst}")
        shutil.copy(src, dst)


def find_replace_text(file_path, find, replace):
    find = find.replace("\\", "\\\\")
    replace = replace.replace("\\", "\\\\")
    _, stderr = cmd_exec(f"sed -i \"\" 's~{find}~{replace}~g' {file_path}")
    if stderr:
        raise Exception(f"error replacing text: {stderr}")


def set_screen_resolution(mode):
    # TODO: move video output name to config
    _, stderr = cmd_exec(f'xrandr --output HDMI-1 --mode {mode}')
    if stderr:
        raise Exception(f"error setting screen resolution: {stderr}")


def restore_screen_resolution():
    # TODO: make generic for any system
    return set_screen_resolution("1920x1200 --panning 0x0+0+0 --scale 1x1")


def gen_win_reg_file(registry, env):
    file = '/tmp/patch.reg'
    with open(file, 'w+t') as f:
        f.write("Windows Registry Editor Version 5.00\n\n")
        for k, v in registry.items():
            f.write(f"[{k}]\n")
            for sv in v:
                (subkey, val), = sv.items()
                val = eval_str(val, env)
                f.write(f'"{subkey}"="{val}"\n')
            f.write("\n")
    return file


def rm_dir(p: Path) -> None:
    print(f"removing {p}")
    shutil.rmtree(p)


def cmd_exec(cmd: str, env=None, cwd=None, echo=True) -> None:
    if echo:
        print(cmd)
    return subprocess.Popen(
        shlex.split(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=cwd
    ).communicate()


def get_var_val_by_name(name):
    import conf.conf as conf
    return getattr(conf, name)


def eval_str(str_in: str, extra_var_val: Dict[str, str] = {}) -> str:
    if "{" not in str_in:
        return str_in
    str_out = str_in
    for v in re.findall("{(.*?)}", str_in):
        if v in extra_var_val:
            new_val = extra_var_val[v]
        else:
            new_val = get_var_val_by_name(v)
        str_out = str_out.replace(f"{{{v}}}", new_val)
    return str_out


def eval_path(path: Path, extra_var_val: Dict[str, str] = {}) -> Path:
    return Path(eval_str(str(path), extra_var_val))
