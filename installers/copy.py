from pathlib import Path

from conf.conf import *

from installers.base_installer import BaseInstaller

from _utils.md import MemDisk

from _utils.misc import (
    cmd_exec,
    copy_ex,
    eval_path,
)


class Copy(BaseInstaller):
    def __init__(self, title):
        super().__init__(title)
        self.mounts = {}
        self.memdisks = []

    def mount(self):
        images = self.conf.get("images", {})
        images = list(images.keys())
        for i in range(len(images)):
            img_path = Path(IMAGES_STORAGE_PATH) / self.title / images[i]
            if not img_path.exists():
                raise Exception(f"invalid image: {img_path}")
            md = MemDisk(img_path, i)
            self.mounts[images[i]] = md.mount()
            self.memdisks.append(md)

    def copy(self):
        images = self.conf.get("images", {})
        for img_name, dst_src in images.items():
            for dst, src_files in dst_src.items():
                dst = eval_path(dst, self.env)
                if isinstance(src_files, list):
                    Path(dst).mkdir(parents=True, exist_ok=True)
                    for s in src_files:
                        src = self.mounts[img_name] / s
                        copy_ex(Path(src), Path(dst))
                else:
                    src = self.mounts[img_name] / src_files
                    copy_ex(src, Path(dst))

            # perform inside a loop to avoid permission issues on copying same files from diff images
            cmd_exec(f"chmod -R 755 {self.game_path}")

    def install(self):
        self.mount()
        self.copy()
        self.patch()
        self.handle_saves()
