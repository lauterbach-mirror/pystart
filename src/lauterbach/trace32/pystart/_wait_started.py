import ctypes
import platform
import time
from abc import ABC, abstractmethod
from typing import IO

from ._exceptions import TimeoutExpiredError


class _WaitStarted(ABC):
    @abstractmethod
    def __call__(self, timeout: float, stdout: IO[bytes]) -> None:
        raise NotImplementedError()


def _get_wait_started_handler(use_delay: bool = False, screen_off: bool = False) -> _WaitStarted:
    if use_delay:
        return _WaitStartedDelay()
    elif platform.system() == "Windows":
        if screen_off:
            return _WaitStartedConsoleWindows()
        else:
            return _WaitStartedWindowsSignal()
    else:
        return _WaitStartedConsoleLinux()


class _WaitStartedWindowsSignal(_WaitStarted):
    GW_OWNER = 4
    WM_CLOSE = 0x0010
    WM_USER = 0x0400
    WAIT_TIMEOUT = 0x00000102
    WAIT_FAILED = 0xFFFFFFFF

    def __init__(self) -> None:
        self.event = ctypes.c_long(ctypes.windll.kernel32.CreateEventW(0, 0, 0, "T32_STARTUP_COMPLETED"))
        assert self.event != ctypes.c_long(0), "no eventhandler was created"

    def __call__(self, timeout: float, stdout: IO[bytes]) -> None:
        assert self.event
        rc = ctypes.windll.kernel32.WaitForSingleObject(self.event, int(timeout * 1000))
        if rc == self.WAIT_TIMEOUT:
            raise TimeoutExpiredError
        elif rc == self.WAIT_FAILED:
            raise RuntimeError("Waiting for Windows event failed")


class _WaitStartedDelay(_WaitStarted):
    def __call__(self, timeout: float, stdout: IO[bytes]) -> None:
        time.sleep(timeout)


class _WaitStartedConsoleWindows(_WaitStarted):
    def __call__(self, timeout: float, stdout: IO[bytes]) -> None:
        buffer = bytearray()
        start_time = time.monotonic()
        for line in stdout:
            buffer += line
            if b"TRACE32 is up and running" in buffer:
                break
            if time.monotonic() - start_time > timeout:
                raise TimeoutExpiredError


class _WaitStartedConsoleLinux(_WaitStarted):
    def __call__(self, timeout: float, stdout: IO[bytes]) -> None:
        import os

        os.set_blocking(stdout.fileno(), False)  # type: ignore
        buffer = bytearray()
        end_time = time.monotonic() + timeout
        while True:
            time.sleep(0.1)
            tmp = stdout.read()
            if tmp is not None:
                buffer += tmp
                if b"TRACE32 is up and running..." in buffer:
                    break
            elif time.monotonic() > end_time:
                raise TimeoutExpiredError
