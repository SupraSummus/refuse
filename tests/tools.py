from contextlib import contextmanager
from threading import Thread
import subprocess
import tempfile
import time

from refuse.high import FUSE, Operations
from refuse.low import FUSELL


class MountTimeout(Exception):
    pass


class FUSEThread(Thread):
    def __init__(
        self,
        mountpoint,
        fuse_class,
        **fuse_kwargs,
    ):
        super().__init__()
        self.mountpoint = mountpoint
        self.fuse_class = fuse_class
        self.fuse_kwargs = fuse_kwargs

    def run(self):
        self.exc = None
        try:
            self.mount()
        except Exception as e:
            self.exc = e

    def join(self):
        super().join()
        if self.exc:
            raise self.exc

    def mount(self):
        self.fuse_class(
            mountpoint=self.mountpoint,
            **self.fuse_kwargs,
        )

    def unmount(self):
        # fuse.fuse_exit() causes segafult
        subprocess.run(
            ['fusermount', '-u', self.mountpoint, '-q'],
            check=self.is_alive(),  # this command has to succeed only if fuse thread is feeling good
        )

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.unmount()
        self.join()


@contextmanager
def fuse_mountpoint(
    *args,
    mount_timeout=5.0,  # seconds
    **kwargs,
):
    with tempfile.TemporaryDirectory() as mountpoint:
        with FUSEThread(mountpoint, *args, **kwargs) as fuse_thread:

            # dirty dirty active waiting for now
            # no idea how to do it the clean way
            waiting_start = time.monotonic()
            while fuse_thread.is_alive() and not is_mountpoint_ready(mountpoint):
                if time.monotonic() - waiting_start > mount_timeout:
                    raise MountTimeout()
                time.sleep(0.01)

            # do wrapped things
            yield mountpoint


def fuse_high_mountpoint():
    operations = Operations()
    setattr(operations, 'use_ns', True)
    return fuse_mountpoint(FUSE, operations=operations, foreground=True)


class FUSELLNS(FUSELL):
    use_ns = True


def fuse_low_mountpoint():
    return fuse_mountpoint(FUSELLNS)


def is_mountpoint_ready(mountpoint):
    # AFAIK works only under linux. More platform-agnostic version may come later.
    with open('/proc/mounts', 'rt') as mounts:
        for mount in mounts:
            typ, this_mountpoint, *_ = mount.split(' ')
            if this_mountpoint == mountpoint:
                return True
    return False
