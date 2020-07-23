from unittest import mock
import os

from refuse.high import Operations

from tests.tools import fuse_high_mountpoint


def test_init_gets_called():
    with mock.patch.object(Operations, 'init') as mocked:
        mocked.return_value = None
        with fuse_high_mountpoint():
            mocked.assert_called_once_with('/')


def test_destroy_gets_called():
    with mock.patch.object(Operations, 'destroy') as mocked:
        mocked.return_value = None
        with fuse_high_mountpoint():
            mocked.assert_not_called()
        mocked.assert_called_once_with('/')


def test_readdir_root():
    with fuse_high_mountpoint() as mountpoint:
        assert os.listdir(mountpoint) == []


def test_readdir_root_nonempty():
    with fuse_high_mountpoint() as mountpoint:
        with mock.patch.object(Operations, 'readdir') as mocked_readdir:
            mocked_readdir.return_value = ['.', '..', 'omg_an_entry']
            assert os.listdir(mountpoint) == ['omg_an_entry']
            mocked_readdir.assert_called_once_with('/', 0)
