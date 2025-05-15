from __future__ import annotations

import enum
import itertools
import logging
import os
import pathlib
import platform
import shutil
import subprocess
import tempfile
import threading
from abc import ABC, abstractmethod
from types import TracebackType
from typing import Any, Dict, Iterable, List, Optional, TextIO, Union

PathType = Union[str, pathlib.Path]
logger = logging.getLogger("lauterbach.trace32.pystart")
logger_stdout = logger.getChild("stdout")
logger_stderr = logger.getChild("stderr")
__all__ = ["PowerView", "Connection", "T32Interface"]


_BIN_SUBFOLDER = {
    "Windows": "windows",
    "Linux": "pc_linux64",
    "Darwin": "macosx64",
}


class PowerView:
    """PowerView is a class to manage TRACE32 PowerView instances.

    Args:
        connection: Specifies how to communicate with the target.
        target: Name of the executable without file extension e.g. 't32marm'
        system_path: Directory where the executable and system files of TRACE32 are located.
        force_executable: Overrides ``system_path`` and ``target`` settings when deriving the executable.
        pbi_index: In case of using a PBIConnection, the 0 based index in the pbi-chain else must be 0.
    """

    def __init__(
        self,
        connection: "Connection",
        target: str = "",
        *,
        system_path: "PathType" = "",
        force_executable: "PathType" = "",
        pbi_index: int = 0,
    ) -> None:
        self.target: str = target
        """name of executable (t32m*) without file extension. This value is not required if ``force_executable`` is set.
        """
        self._connection: "Connection" = connection
        self._connection._register(self, pbi_index)
        self._process: Optional[subprocess.Popen[str]] = None
        self.interfaces: Dict[Any, List[T32Interface]] = dict()
        self._config_file_name: str = ""
        self._thread_stdout: Optional[threading.Thread] = None
        self._thread_stderr: Optional[threading.Thread] = None
        self._event_started = threading.Event()

        # paths
        self.system_path: "PathType" = system_path
        """Directory where the executable and system files of TRACE32 are located."""
        self.temp_path: "PathType" = ""
        """Directory, where temporary files can be created. The source files are copied to the temporary directory while
        debugging."""
        self.id: str = ""
        """Prefix for all files that are saved by the TRACE32 PowerView instance into the TMP directory. We recommend to
        set a unique id for every PowerView instance running simultaneously."""
        self.help_path: "PathType" = ""
        """Directory where the pdf-files for the TRACE32 online help are located."""
        self.license_file: "PathType" = ""
        """Directory where a license file can be located. A license file provides the software maintenance keys."""
        self.force_executable: Optional["PathType"] = pathlib.Path(force_executable) if force_executable else None
        """Overrides ``system_path`` and ``target`` settings when deriving the executable.

        Use this option only if you know what you are doing.
        """
        self.force_32bit_executable: Optional[bool] = None
        """If set, pystart will start the 32-bit executable located under ``bin/windows`` instead of the 64-bit
        executable located under ``bin/windows64`` if the executable is derived from system_path. This could be e.g.
        needed if a 32-bit DLL has to be loaded in TRACE32 PowerView."""
        # rlm license
        self.rlm_port: int = 5055
        """The Floating License Client (RLM Client) needs to know which (RLM) port number should be used to get the
        license."""
        self.rlm_server: str = ""
        """The Floating License Client (RLM Client) needs to know which (RLM) Server to contact to get the license."""
        self.rlm_file: "PathType" = ""
        """Sets a license file (.lic) which includes the floating license parameters."""
        self.rlm_timeout: Optional[int] = None
        """RLM timeout in minutes"""
        self.rlm_pool_port: Optional[int] = None
        """TCP/IP port for license pool. Refer to the chapter “Floating License Pools” in Floating Licenses, page 19
        (floatinglicenses.pdf) for more information."""
        # screen
        self.screen: Optional[bool] = None
        """If ``False`` the main window of TRACE32 and all other dialogs and windows of TRACE32 remain hidden - even if
        an error occurs. If ``None`` the global default is used."""
        self._screen_off: bool = False
        self.title: str = ""
        """Sets the window title of the TRACE32 instance."""
        self.font_size: Optional[FontSize] = None
        """Selects the used font size used by the TRACE32 instance (Normal, Small or Large)."""
        self.clear_type: Optional[bool] = None
        """Select if Cleartype display of fonts is switched ON or OFF.

            ``True``: ON if it is supported by the OS. The monospaced truetype font "Lucida Console" is used as basic
            font and should be installed.

            ``False``: OFF, TRACE32 fonts are used (t32font.fon).

            ``None``: Use global setting.
        """
        self.palette: Optional[Palette] = None
        """Sets up display theme."""
        self.full_screen: Optional[bool] = None
        """If set to true, the TRACE32 instance is started in full screen mode."""
        self.ionic: Optional[bool] = None
        """If True: Startup iconized (minimized)"""
        self.invisible: Optional[bool] = None
        """If True: The main window of TRACE32 remains hidden. However, dialogs and other windows of TRACE32 can still
        be opened."""
        self.window_mode: Optional[WindowMode] = None
        """Specify how child windows appear."""
        self.language: Optional[Language] = None
        """Set up the language used by TRACE32."""
        # startup script
        self.startup_script: "PathType" = ""
        """A cmm script being executed on start of TRACE32."""
        self.startup_parameter: Iterable[str] = []
        """Parameter for ``startup_script``. If you want to retrieve the parameters by ``PARAMETERS`` command, consider
        adding additional quotes at beginning and ending of each string."""
        self.safe_start: bool = False
        """Suppresses the automatic execution of any PRACTICE script after starting TRACE32. This allows you to test or
        debug the scripts that are normally executed automatically."""

    def __del__(self) -> None:
        if self._config_file_name:
            os.remove(self._config_file_name)

    def __enter__(self) -> PowerView:
        return self

    def __exit__(
        self, exc_type: type[BaseException], exc_value: Optional[BaseException], traceback: Optional[TracebackType]
    ) -> None:
        self.stop()

    def _create_config_file(self) -> str:
        dir = self.temp_path or defaults.temp_path or os.environ.get("T32TMP")
        with tempfile.NamedTemporaryFile("w+", delete=False, dir=dir) as config_file:
            filename = config_file.name
            config_file.write(self.get_configuration_string())
        logger.debug(f"temporary config file created: {filename}")
        return filename

    def _get_popen_args(self) -> List[str]:
        cmd = [str(self.executable), "--t32-bootstatus"]
        if self.startup_script and self.safe_start:
            cmd.append("--t32-safestart")
        self._config_file_name = self._create_config_file()
        cmd.extend(["-c", self._config_file_name])
        if self.startup_script:
            cmd.append("-s")
            cmd.append(str(self.startup_script))
            if self.startup_parameter:
                cmd.extend(self.startup_parameter)
        return cmd

    def start(self, *, timeout: float = 20.0, delay: Optional[float] = None) -> PowerView:
        """generates a config file, starts TRACE32 and blocks until TRACE32 has fully started

        Args:
            timeout: timeout for complete start of TRACE32 in seconds. (default=20.0)
            delay: (deprecated) If not `None` value is used to overwrite `timeout` parameter, at the same time
                    `TimeoutError` exception is disabled. Please set `delay` parameter to an appropriate value
                    for TRACE32 installations with a build number below 166336.

        Returns:
            self

        Raises:
            FileNotFoundError: if the executable can not be found within the specified path
            TimeoutError: after waiting for the time specified by `timeout`
            RuntimeError: if process is already running
            ChildProcessError: if process terminated prematurely
        """
        if self._process and self._process.poll() is None:
            raise RuntimeError("process is already running")

        if not self.executable.exists() and not self.executable.is_file():
            raise FileNotFoundError(f"Executable {self.executable} not found")

        if delay is not None:
            timeout = delay

        if platform.system() == "Windows" and not self._screen_off and delay is None:
            logger.debug("create Windows event for waiting until PowerView has started")
            t = threading.Thread(
                target=_wait_started_windows_signal, args=(self._event_started, timeout + 1), daemon=True
            )
            t.start()

        cmd = self._get_popen_args()
        logger.info("starting PowerView instance")
        self._process = subprocess.Popen(
            cmd, env=os.environ, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        assert self._process.stdout is not None
        assert self._process.stderr is not None
        self._thread_stdout = threading.Thread(
            target=_handle_console_out, args=(self._process.stdout, logger_stdout, self._event_started), daemon=True
        )
        self._thread_stderr = threading.Thread(
            target=_handle_console_out, args=(self._process.stderr, logger_stderr, self._event_started), daemon=True
        )
        self._thread_stdout.start()
        self._thread_stderr.start()
        threading.Thread(
            target=_event_on_terminate, args=(self._process, self._event_started, timeout), daemon=True
        ).start()

        logger.info("waiting for start of PowerView instance")
        if not self._event_started.wait(timeout) and delay is None:
            raise TimeoutError("Timeout expired on waiting for complete start of PowerView")
        if self._process.poll() is not None:
            raise ChildProcessError("PowerView instance terminated prematurely")
        logger.info("PowerView instance started")
        return self

    def wait(self, timeout: Optional[float] = None) -> None:
        """wait for process to terminate

        Args:
            timeout: optional timeout in seconds.

        Raises:
            TimeoutError: on timeout
        """
        if self._process:
            try:
                self._process.wait(timeout)
            except subprocess.TimeoutExpired as exc:
                raise TimeoutError from exc
        self._event_started.clear()

    def stop(self, timeout: Optional[float] = None) -> None:
        """stops the process gently

        This function blocks until the process is stoppped.
        When TRACE32 build number is below 165929, you are on Windows and screen is disabled, TRACE32 does not get
        stopped.

        Args:
            timeout: optional timeout in seconds. If `None` wait for an infinite amount of time. Default is `None`.

        Raises:
            TimeoutError: on timeout
        """
        if self._process is None:
            return

        if platform.system() == "Windows":
            if self._screen_off:
                assert self._process.stdin is not None
                try:
                    logger.debug('send "QUIT" to PowerView instance via stdin')
                    self._process.stdin.write("quit\n")
                except subprocess.TimeoutExpired as exc:
                    raise TimeoutError from exc
            else:
                import ctypes

                @ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_ulong, ctypes.c_long)
                def close_message_to_t32(hwnd, _):  # type: ignore
                    hwnd = ctypes.c_ulong(hwnd)
                    window_pid = ctypes.c_longlong()
                    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
                    GW_OWNER = 4
                    if (
                        window_pid.value == self._process.pid  # type: ignore
                        and ctypes.windll.user32.GetWindow(hwnd, GW_OWNER) == 0
                        and ctypes.windll.user32.IsWindowVisible(hwnd)
                    ):
                        WM_CLOSE = 0x0010
                        logger.debug('Post Windows message "WM_CLOSE"')
                        ctypes.windll.user32.PostMessageA(hwnd, WM_CLOSE, 0, 0)
                    return 1

                ctypes.windll.user32.EnumWindows(close_message_to_t32, None)
        else:
            logger.debug("send SIGTERM to PowerView instance")
            self._process.terminate()

        try:
            self._process.wait(timeout)
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError from exc

    def get_pid(self) -> Optional[int]:
        """Returns the process id

        Returns:
            process id of the PowerView instance or ``None`` if process is not running
        """
        if self._process and self._process.poll() is None:
            return self._process.pid
        return None

    @property
    def executable(self) -> pathlib.Path:
        """Getter for the executable being used to start a PowerView instance.

        Returns:
            The executable being used to start the PowerView instance.

        Raises:
            ValueError: If the executable could not be derived because of missing settings
        """
        if self.force_executable is not None:
            return pathlib.Path(self.force_executable)

        if not self.target:
            raise ValueError("no target specified")

        system = platform.system()
        system_path = self.system_path or defaults.system_path or os.environ.get("T32SYS")

        if not system_path:
            executable = shutil.which(self.target)
            if executable:
                return pathlib.Path(executable)

            if system == "Windows":
                system_path = r"C:\T32"
            elif system == "Linux":
                system_path = "/opt/t32"
            else:
                raise ValueError("no system_path specified")

        sys_specific = _BIN_SUBFOLDER[system]
        extension = ""

        if system == "Windows":
            extension = ".exe"
            if not self.force_32bit_executable:
                sys_specific += "64"

        path = pathlib.Path(system_path, "bin", sys_specific, f"{self.target}{extension}")
        if path.exists():
            return path

        if system == "Windows" and not self.force_32bit_executable:
            sys_specific = _BIN_SUBFOLDER[system]
        return pathlib.Path(system_path, "bin", sys_specific, f"{self.target}{extension}")

    def add_interface(self, interface: "T32Interface") -> "T32Interface":
        """Add a interface for inter-process communication

        Args:
            interface: interface to add

        Returns:
            added interface

        Raises:
            ValueError: raised if an interface which can be added only once is already added
        """
        if not isinstance(interface, T32Interface):
            raise ValueError("parameter is not of type _T32Interface")

        interface_type = type(interface)

        interfaces_same_type = self.interfaces.get(interface_type)
        if interfaces_same_type is None:
            interfaces_same_type = []
            self.interfaces[interface_type] = interfaces_same_type

        limit = interface_type._get_max_instances()
        if limit is not None and limit <= len(interfaces_same_type):
            class_name = interface.__class__.__name__
            raise ValueError(f"maximum number of {class_name} already set")

        interfaces_same_type.append(interface)
        return interface

    def get_configuration_string(self) -> str:
        """Generates the content of the config file.

        Returns:
            generated config file content
        """
        fragments = [
            "; THIS FILE IS GENERATED BY PYSTART, CHANGES WILL BE DISCARDED",
            self._get_configuration_string_os(),
            self._connection._get_config_string(self),
            self._get_config_string_license(),
            self._get_config_string_screen(),
            self._get_config_string_interface(),
        ]

        if self.license_file:
            fragments.append(f"LICENSE={self.license_file}")
        elif defaults.license_file:
            fragments.append(f"LICENSE={defaults.license_file}")

        return "\n\n".join(filter(None, fragments))

    def _get_configuration_string_os(self) -> str:
        args = ["OS="]

        t32id = self.id or os.environ.get("T32ID")
        if t32id:
            args.append(f"ID={t32id}")

        t32tmp = self.temp_path or defaults.temp_path or os.environ.get("T32TMP")
        if t32tmp:
            args.append(f"TMP={t32tmp}")

        # global system_path
        t32sys = self.system_path or defaults.system_path or os.environ.get("T32SYS")
        if t32sys:
            args.append(f"SYS={t32sys}")

        help_path = self.help_path or defaults.help_path
        if help_path:
            args.append(f"HELP={help_path}")

        return "\n".join(args) if len(args) > 1 else ""

    def _get_config_string_license(self) -> str:
        args = ["LICENSE="]

        rlm_pool_port = self.rlm_pool_port or defaults.rlm_pool_port
        if rlm_pool_port:
            args.append(f"POOLPORT={rlm_pool_port}")

        if self.rlm_file:
            args.append(f"RLM_LICENSE={self.rlm_file}")
        elif self.rlm_server:
            args.append(f"RLM_LICENSE={self.rlm_port}@{self.rlm_server}")
        elif defaults.rlm_file:
            args.append(f"RLM_LICENSE={defaults.rlm_file}")
        elif defaults.rlm_server:
            args.append(f"RLM_LICENSE={defaults.rlm_port}@{defaults.rlm_server}")

        rlm_timeout = self.rlm_timeout or defaults.rlm_timeout
        if rlm_timeout:
            args.append(f"TIMEOUT={self.rlm_timeout}")

        if len(args) - bool(self.rlm_timeout) > 1:
            return "\n".join(args)
        else:
            return ""

    def _get_config_string_screen(self) -> str:
        self._screen_off = self.screen is False or (self.screen is None and defaults.screen is False)
        if self._screen_off:
            return "SCREEN=OFF"
        args = ["SCREEN="]

        if self.window_mode is None:
            if defaults.window_mode != WindowMode.MDI:
                args.append(defaults.window_mode.value)
        elif self.window_mode != WindowMode.MDI:
            args.append(self.window_mode.value)

        if self.full_screen or (self.full_screen is None and defaults.full_screen):
            args.append("VFULL")
        if self.ionic or (self.ionic is None and defaults.ionic):
            args.append("VICON")
        if self.invisible or (self.invisible is None and defaults.invisible):
            args.append("INVISIBLE")

        if self.font_size is None:
            if defaults.font_size != FontSize.MEDIUM:
                args.append(f"FONT={defaults.font_size.value}")
        elif self.font_size != FontSize.MEDIUM:
            args.append(f"FONT={self.font_size.value}")

        if self.clear_type is None:
            if defaults.clear_type is not None:
                args.append("CLEARTYPE" if defaults.clear_type else "NOCLEARTYPE")
        elif self.clear_type is not None:
            args.append("CLEARTYPE" if self.clear_type else "NOCLEARTYPE")

        if self.language is None:
            if defaults.language != Language.ENGLISH:
                args.append(f"LANGUAGE={defaults.language.value}")
        elif self.language != Language.ENGLISH:
            args.append(f"LANGUAGE={self.language.value}")

        if self.title:
            args.append(f"HEADER={self.title}")

        if self.palette is None:
            if defaults.palette not in (Palette.DEFAULT, Palette.KEEP):
                args.append(defaults.palette.value)
        elif self.palette not in (Palette.DEFAULT, Palette.KEEP):
            args.append(self.palette.value)
        return "\n".join(args)

    def _get_config_string_interface(self) -> str:
        cfg = [x._get_config_string() for x in itertools.chain.from_iterable(self.interfaces.values())]
        return "\n\n".join(cfg)


def _wait_started_windows_signal(event_started: threading.Event, timeout: float) -> None:
    import ctypes

    WAIT_TIMEOUT = 0x00000102
    WAIT_FAILED = 0xFFFFFFFF

    event = ctypes.c_long(ctypes.windll.kernel32.CreateEventW(0, 0, 0, "T32_STARTUP_COMPLETED"))
    assert event != ctypes.c_long(0), "no eventhandler was created"
    rc = ctypes.windll.kernel32.WaitForSingleObject(event, int(timeout * 1000))
    if rc == WAIT_TIMEOUT:
        if event_started.is_set():
            logger.debug("ignoring Windows event timeout because of formerly event_started")
        else:
            logger.error("timeout expired on waiting for Windows event")
    elif rc == WAIT_FAILED:
        logger.error("waiting for Windows event failed (WAIT_FAILED)")
    else:
        logger.debug("set event_started due to received T32_STARTUP_COMPLETED event")
        event_started.set()


def _event_on_terminate(process: subprocess.Popen[str], event_started: threading.Event, timeout: float) -> None:
    try:
        process.wait(timeout + 1)
    except subprocess.TimeoutExpired:
        return
    logger.debug("Process terminated formerly")
    event_started.set()


def _handle_console_out(stdout: TextIO, console_logger: logging.Logger, event_started: threading.Event) -> None:
    for line in stdout:
        line = line.rstrip()
        if line == "TRACE32 is up and running...":
            logger.debug('set event_started due to "TRACE32 is up and running..." message')
            event_started.set()
        elif line.startswith("Fatal Error:"):
            logger.debug('set event_started due to "Fatal Error"')
            event_started.set()
        console_logger.info(line)


class Connection(ABC):
    """An interface for different debug connections.

    A Connection is used to specify with which hardware (e.g. USB-Debugger) or software (e.g. Simulator) to work for
    your debug session.
    """

    @abstractmethod
    def _get_config_string(self, power_view: "PowerView") -> str:
        """return the Connection-Specific part of a TRACE32 config file"""
        raise NotImplementedError()

    @abstractmethod
    def _register(self, power_view: "PowerView", pbi_index: int) -> None:
        """register a PowerView-Instance

        Args:
            power_view: PowerView-Instance
            pbi_index: in case of a PBIConnection, the 0 based index in the pbi-chain else ignored
        """
        pass


class T32Interface(ABC):
    """An interface for several TRACE32 interfaces.

    A T32Interface enables the use of TRACE32 as backend being controlled from an other process.
    """

    @abstractmethod
    def _get_config_string(self) -> str:
        pass

    @classmethod
    @abstractmethod
    def _get_max_instances(cls) -> Optional[int]:
        pass


####################
# Screen setting types:
####################
class FontSize(enum.Enum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}.{self.name}"


class Palette(enum.Enum):
    """Enumeration of basic color schemes."""

    DEFAULT = "DEFAULT"
    KEEP = "KEEP"
    """Keep last used palette"""
    DARK_THEME = """PALETTE 0 = 181 181 181
PALETTE 1 = 41 49 52
PALETTE 2 = 63 75 78
PALETTE 5 = 255 111 111
PALETTE 7 = 255 255 206
PALETTE 8 = 192 192 192
PALETTE 11 = 160 130 189
PALETTE 13 = 102 116 123
PALETTE 19 = 192 192 192
PALETTE 20 = 192 192 192
PALETTE 21 = 192 192 192
PALETTE 22 = 192 192 192
PALETTE 23 = 192 192 192
PALETTE 25 = 192 192 192
PALETTE 26 = 192 192 192
PALETTE 27 = 47 57 60
PALETTE 28 = 192 192 192
PALETTE 29 = 47 57 60
PALETTE 30 = 47 57 60
PALETTE 31 = 192 192 192
PALETTE 36 = 232 172 99
PALETTE 37 = 147 199 99
PALETTE 47 = 47 57 60
PALETTE 54 = 255 255 255"""

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}.{self.name}"


class WindowMode(enum.Enum):
    MDI = "MDI"
    """Multiple Document Interface (default).
        All child windows appear inside the TRACE32 main window.
    """
    FDI = "FDI"
    """Floating Document Interface.
        All child windows can be placed on any position on the desktop independently form the main window. Minimizing
        the main window, minimizes also the child windows. Only the main window appears in the task bar.
    """
    MTI = "MTI"
    """Multiple Top-level window Interface
        All child windows can be placed on any position on the desktop independently form the main window. Minimizing
        the main window, minimizes none of the child windows. Both the main and all child windows appear in the task
        bar.
    """

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}.{self.name}"


class Language(enum.Enum):
    ENGLISH = "EN"
    JAPANESE = "JP"

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}.{self.name}"


class PowerViewGlobalDefaults:
    """A class to handle ``PowerView`` default settings on a centralized place."""

    def __init__(self) -> None:
        # paths
        self.system_path: "PathType" = ""
        """Directory where the executable and system files of TRACE32 are located.

        Initially the value is set to environment variable ``T32SYS``. If the environment variable is not set, on
        Windows systems ``"C:\\T32"`` is taken, on Linux system a value must be set before start."""

        self.temp_path: "PathType" = ""
        """Directory, where temporary files can be created. The source files are copied to the temporary directory while
        debugging.

        Initially the value is set to environment variable ``T32TMP``. If the environment variable is not set TRACE32 is
        responsible for the path being used."""
        self.help_path: "PathType" = ""
        """Directory where the pdf-files for the TRACE32 online help are located."""
        self.license_file: "PathType" = ""
        """Directory where a license file can be located. A license file provides the software maintenance keys."""
        self.force_32bit_executable: bool = False
        """If set, pystart will start the 32-bit executable located under ``bin/windows`` instead of the 64-bit
        executable located under ``bin/windows64``. This could be e.g. needed if a 32-bit DLL has to be loaded in
        TRACE32 PowerView."""
        # rlm license
        self.rlm_port: int = 5055
        """The Floating License Client (RLM Client) needs to know which (RLM) port number should be used to get the
        license. Defaults to 5055."""
        self.rlm_server: str = ""
        """The Floating License Client (RLM Client) needs to know which (RLM) Server to contact to get the license."""
        self.rlm_file: "PathType" = ""
        """Sets a license file (.lic) which includes the floating license parameters."""
        self.rlm_timeout: Optional[int] = None
        """RLM timeout in minutes"""
        self.rlm_pool_port: Optional[int] = None
        """TCP/IP port for license pool. Refer to the chapter “Floating License Pools” in Floating Licenses, page 19
        (floatinglicenses.pdf) for more information."""
        # screen
        self.screen: bool = True
        """If ``False`` the main window of TRACE32 and all other dialogs and windows of TRACE32 remain hidden - even if
        an error occurs."""
        self.font_size: FontSize = FontSize.MEDIUM
        """Selects the used font size used by the TRACE32 instance (Normal, Small or Large)."""
        self.clear_type: Optional[bool] = None
        """Select if Cleartype display of fonts is switched ON or OFF.

            ``True``: ON if it is supported by the OS. The monospaced truetype font "Lucida Console" is used as basic
            font and should be installed.

            ``False``: OFF, TRACE32 fonts are used (t32font.fon).

            ``None``: Use DEFAULT.
        """
        self.palette: Palette = Palette.KEEP
        """Sets up display theme."""
        self.full_screen: bool = False
        """If set to true, the TRACE32 instance is started in full screen mode."""
        self.ionic: bool = False
        """If True: Startup iconized (minimized)"""
        self.invisible: bool = False
        """If True: The main window of TRACE32 remains hidden. However, dialogs and other windows of TRACE32 can still
        be opened."""
        self.window_mode: WindowMode = WindowMode.MDI
        """Specify how child windows appear."""
        self.language: Language = Language.ENGLISH
        """Set up the language used by TRACE32."""


defaults: PowerViewGlobalDefaults = PowerViewGlobalDefaults()
"""If attributes of a ``PowerView`` instance are not set, the values are taken from the attribute with same name from
this object. Therefore, even for multiple instances of ``PowerView`` some attributes can be set on a single point."""
