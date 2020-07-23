from unittest import mock

from refuse.low import FUSELL

from tests.tools import fuse_low_mountpoint


def test_init_gets_called():
    with mock.patch.object(FUSELL, 'init') as mocked:
        mocked.return_value = None
        with fuse_low_mountpoint():
            # TODO - verify parameters (second parameter `conn` is hard)
            mocked.assert_called_once()


def test_destroy_gets_called():
    with mock.patch.object(FUSELL, 'destroy') as mocked:
        mocked.return_value = None
        with fuse_low_mountpoint():
            mocked.assert_not_called()
        mocked.assert_called_once_with(None)
