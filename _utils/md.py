from pathlib import Path

from _utils.misc import (
    cmd_exec,
)

from conf.conf import IMAGES_MOUNT_BASE_PATH


class MemDisk:
    def __init__(self, image_path, unit):
        self.image_path = image_path
        self.unit = unit
        self.md_path = f"/dev/md{self.unit}"
        self.mount_path = Path(IMAGES_MOUNT_BASE_PATH) / str(self.unit)

    def __del__(self):
        self.unmount()

    def __delete(self):
        _, stderr = cmd_exec(f"sudo mdconfig -d -u {self.unit}")
        if stderr:
            raise Exception(f"error deleting memdisk: {stderr}")

    def __create(self, replace=True):
        stdout, stderr = cmd_exec(f"sudo mdconfig -a -t vnode -f {self.image_path} -u {self.unit}")
        if stderr:
            if replace:
                self.unmount()
                self.__create(replace=False)
                return
            raise Exception(f"error creating memdisk: {stderr}")

    def mount(self, fs_type="cd9660"):
        self.__create()
        if self.mount_path.exists():
            self.unmount()
        else:
            _, stderr = cmd_exec(f"sudo mkdir -p {self.mount_path}")
            if stderr:
                raise Exception(f"error mounting memdisk: {stderr}")
        _, stderr = cmd_exec(f"sudo mount -t {fs_type} {self.md_path} {self.mount_path}")
        if stderr:
            raise Exception(f"error mounting memdisk: {stderr}")
        return self.mount_path

    def unmount(self, delete=True):
        if self.mount_path.exists():
            _, stderr = cmd_exec(f"sudo umount -f {self.mount_path}")
            # if stderr:
            # raise Exception(f"error umounting memdisk: {stderr}")
            if delete:
                _, stderr = cmd_exec(f"sudo rm -rf {self.mount_path}")
                if stderr:
                    raise Exception(f"error umounting memdisk: {stderr}")
        if delete:
            self.__delete()
