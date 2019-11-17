import os
import simplejson as json
import sys

ROOT_FOLDER = "/ara/adventum_ark"

USER = "robert"

TEST = "pytest" in sys.modules

IMAGES_STORAGE_PATH = f"{ROOT_FOLDER}/images"
IMAGES_MOUNT_BASE_PATH = "/mnt/md"

GAMES_BASE_PATH = f"{ROOT_FOLDER}/games"
SAVES_BASE_PATH = f"{ROOT_FOLDER}/saves"
PATCHES_BASE_PATH = f"{ROOT_FOLDER}/devel/aa/patches"

WINE_ENVS_BASE_PATH = f"{ROOT_FOLDER}/envs/wine"
WINE_GAMES_BASE_PATH = "C:\\GAMES"
WINE_CDROM_DRIVE = "D:"

DOSBOX_CONF_PATH = f"{ROOT_FOLDER}/devel/aa/conf/dosbox.conf"

SCUMMVM_CONF_PATH = f"{ROOT_FOLDER}/devel/aa/conf/scummvm.ini"

with open(os.path.join(os.path.dirname(__file__), 'games.json')) as f:
    GAMES_CONF = json.load(f)
