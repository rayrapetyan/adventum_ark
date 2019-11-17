from pathlib import Path

from conf.conf import *

from _utils.misc import (
    cmd_exec,
)

from runners.base_runner import BaseRunner


class DosBox(BaseRunner):
    def __init__(self, title):
        super().__init__(title)

    def __del__(self):
        super(DosBox, self).__del__()

    def run(self):
        cmd_list = []

        cmd_list.append(f"MOUNT C {GAMES_BASE_PATH}")

        cdrom_drive_letter = "D"

        if 'images' in self.conf:
            img_paths = []
            for img in self.conf["images"]:
                img_paths.append(str(Path(IMAGES_STORAGE_PATH) / self.title / img))
            img_paths = " ".join(img_paths)
            cmd_list.append(f"IMGMOUNT {cdrom_drive_letter} {img_paths} -t iso")

        if self.cdrom_folder:
            cmd_list.append(f"MOUNT {cdrom_drive_letter} {self.cdrom_folder} -t cdrom")

        cmd_list.append("C:")

        dos_folder = self.title.upper()
        if len(dos_folder) > 8:
            dos_folder = dos_folder[:6] + "~1"
        cmd_list.append(f"cd {dos_folder}")

        cmd_list.append(self.conf["exec_file"])

        cmd_list.append("exit")

        cmd_line = ""
        conf_path = Path(DOSBOX_CONF_PATH)
        cmd_line += f"dosbox -conf {conf_path}"
        for c in cmd_list:
            cmd_line += f' -c "{c}"'

        _, stderr = cmd_exec(cmd_line)
        if stderr:
            print(f"dosbox errors: {stderr}")
