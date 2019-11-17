from pathlib import Path
from pytest import raises

from _utils.md import MemDisk

from conf.conf import IMAGES_MOUNT_BASE_PATH


def test_mount():
    md = MemDisk("data/test.iso", 0)
    assert(md.mount() == Path(IMAGES_MOUNT_BASE_PATH) / "0")
    md.unmount()


def test_wrong_mount():
    md = MemDisk("data/askdjgh.iso", 0)
    with raises(Exception):
        md.mount()


def test_double_mount():
    md = MemDisk("data/test.iso", 0)
    assert(md.mount() == Path(IMAGES_MOUNT_BASE_PATH) / "0")
    with raises(Exception):
        md.mount("data/test.iso", 0)
    md.unmount()


def test_multi_mount():
    md = MemDisk("data/test.iso", 0)
    assert(md.mount() == Path(IMAGES_MOUNT_BASE_PATH) / "0")
    md2 = MemDisk("data/test.iso", 1)
    assert(md2.mount() == Path(IMAGES_MOUNT_BASE_PATH) / "1")
    md.unmount()
    md2.unmount()
