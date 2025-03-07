import enum
import platform
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

from ._powerview import Connection

if TYPE_CHECKING:
    from ._powerview import PathType, PowerView

__all__ = [
    "ConnectMode",
    "USBConnection",
    "UDPConnection",
    "CitrixConnection",
    "USBProxyConnection",
    "MCIServerConnection",
    "SimulatorConnection",
    "GDBConnection",
    "HostConnection",
    "MCILibConnection",
    "SerialRomMonitorConnection",
    "MCDConnection",
    "CADIConnection",
    "IRISConnection",
    "ARCINTConnection",
    "GDIConnection",
    "MDIConnection",
    "SCSConnection",
    "SIMTSIConnection",
    "ViewerConnection",
    "TCPConnection",
    "InteractiveConnection",
]


class _SingleConnection(Connection):
    """Abstract Connection class containing at most 1 PowerView-Instance (e.g. Simulator)"""

    def __init__(self) -> None:
        self._registry: Optional["PowerView"] = None

    def _register(self, power_view: "PowerView", pbi_index: int = 0) -> None:
        assert pbi_index == 0, "the specified connection does not support pbi_index"
        if self._registry:
            raise RuntimeError("this connection already has registered a PowerView instance")
        self._registry = power_view


class _MultiConnection(Connection):
    """Abstract Connection class containing arbitrary many PowerView-Instances (e.g. MCI-Server)"""

    def __init__(self) -> None:
        super().__init__()
        self._registry: List["PowerView"] = []

    def _register(self, power_view: "PowerView", pbi_index: int = 0) -> None:
        assert pbi_index == 0, "the specified connection does not support pbi_index"
        self._registry.append(power_view)

    def _get_core_num(self, power_view: "PowerView") -> int:
        try:
            idx = self._registry.index(power_view)
        except ValueError:
            raise ValueError("this PowerView instance is not registered within this connection")
        return idx + 1 if len(self._registry) > 1 else 0


class _PBIConnection(Connection):
    """Abstract Connection class containing multiple PowerView-Instances arranged corresponding to their position in a
    PodBusChain (e.g. USBConnection)"""

    def __init__(self) -> None:
        self._registry: List[List["PowerView"]] = [[]]

    # TODO: there exists PBI-devices which allocate 2 podbus indices
    def _register(self, power_view: "PowerView", pbi_index: int = 0) -> None:
        while len(self._registry) <= pbi_index:
            self._registry.append([])
        self._registry[pbi_index].append(power_view)

    def _get_pbi_string(self, power_view: "PowerView") -> str:
        if len(self._registry) == 1:
            return ""
        tmp = ""
        for pbi in self._registry:
            tmp += "1" if power_view in pbi else "0"
        return f"USE={tmp}"

    def _get_core_num(self, power_view: "PowerView") -> int:
        for pbi in self._registry:
            try:
                idx = pbi.index(power_view)
                # power_view is in the list, else an exception would have been raised
                return idx + 1 if len(pbi) > 1 else 0
            except ValueError:
                pass
        raise ValueError("this PowerView instance is not registered within this connection")

    @abstractmethod
    def _get_connection_config(self) -> str:
        """return PowerView independent part of configuration"""
        pass


class ConnectMode(enum.Enum):
    """Specify reaction if debugger is already in use.

    The connection modes are not applicable for multi-core debugging.
    """

    NORMAL = enum.auto()
    """If PowerDebug device is already in use, warn user and close application after confirmation."""
    AUTOABORT = enum.auto()
    """ If PowerDebug device is already in use, the TRACE32 executable will be closed automatically without any user
    interaction."""
    QUERYCONNECT = enum.auto()
    """If PowerDebug device is already in use, ask user if connection shall be forced."""
    AUTOCONNECT = enum.auto()
    """The TRACE32 executable will automatically take over control over the PowerDebug device, even if the debugger is
    already in use."""
    AUTORETRY = enum.auto()
    """If PowerDebug device is already in use, the TRACE32 executable will wait until the current TRACE32 session ends.
    """

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}.{self.name}"


@dataclass
class USBConnection(_PBIConnection):
    """Connection class for USB hardware debugger.

    This Connection is a subtype of PBIConnection.
    """

    device_name: str = ""
    """A name is required if several debug modules are connected via USB and used simultaneously.
    The manufacturing default device name is the serial number of the debug module. e.g. NODE=E18110012345"""
    device_path: "PathType" = ""
    """Linux only: Use this option to select the debug module to use if several debug modules are connected via USB."""
    connect_mode: ConnectMode = ConnectMode.NORMAL
    """Specify reaction if debugger is already in use."""
    exclusive: bool = False
    """If set no other TRACE32 executable can connect to this particular PowerDebug module."""

    def __post_init__(self) -> None:
        super().__init__()

    def _get_connection_config(self) -> str:
        args = ["PBI=", "USB"]
        if self.device_name:
            args.append(f"NODE={self.device_name}")
        if self.device_path and platform.system() == "Linux":
            args.append(f"DEVPATH={self.device_path}")
        if self.connect_mode is not ConnectMode.NORMAL:
            args.append(f"CONNECTIONMODE={self.connect_mode.name}")
        return "\n".join(args)

    def _get_config_string(self, power_view: "PowerView") -> str:
        args = [self._get_connection_config()]
        index = self._get_core_num(power_view)
        if self.exclusive:
            if index != 0:
                raise ValueError("GUI index too high to generate config files using exclusive mode!")
            args.append("CORE=0")
        if index > 0:
            args.append(f"CORE={index}")
        pbi_string = self._get_pbi_string(power_view)
        if pbi_string:
            args.append(pbi_string)

        return "\n".join(args)


@dataclass
class UDPConnection(_PBIConnection):
    """Connection class for ethernet hardware debugger via UDP.

    This Connection is a subtype of PBIConnection.
    """

    node_name: str
    """The key value specifies the node name of the PowerDebug device to connect to. This should be either a DNS
    name or an IP address."""
    port: int = 0
    """UDP Port to which PowerView should send its packets on debugger module. If 0, a default port is used."""
    host_port: int = 0
    """Defines the UDP communication port from the debugger module to the host. If 0, an available port will be derived
    from your OS."""
    max_udp_packet_size: int = 1024
    """Limit the maximum UDP packet size."""
    packet_burst_limitation: bool = False
    """Sends only very small packets."""
    compression: bool = False
    """If ``True`` reduces the packet size by compression."""
    delay: int = 0
    """Delay UDP packets send from host by specifed time in milliseconds."""
    connect_mode: ConnectMode = ConnectMode.NORMAL
    """Specify reaction if debugger is already in use."""
    exclusive: bool = False
    """Tells TRACE32 that there can be only one TRACE32 PowerView instance to connect."""

    def __post_init__(self) -> None:
        super().__init__()

    def _get_connection_config(self) -> str:
        args = ["PBI=", "NET", f"NODE={self.node_name}"]
        if self.port:
            args.append(f"PORT={self.port}")
        if self.host_port:
            args.append(f"HOSTPORT={self.host_port}")
        if self.max_udp_packet_size != 1024:
            args.append(f"PACKLEN={self.max_udp_packet_size}")
        if self.packet_burst_limitation:
            args.append("SMALLBLOCKS")
        if self.compression:
            args.append("COMPRESS")
        if self.delay:
            args.append(f"DELAY={self.delay}")
        if self.connect_mode != ConnectMode.NORMAL:
            args.append(f"CONNECTIONMODE={self.connect_mode.name}")
        return "\n".join(args)

    def _get_config_string(self, power_view: "PowerView") -> str:
        args = [self._get_connection_config()]
        index = self._get_core_num(power_view)
        if self.exclusive:
            if index != 0:
                raise ValueError("GUI index too high to generate config files using exclusive mode!")
            args.append("CORE=0")
        if index > 0:
            args.append(f"CORE={index}")
        pbi_string = self._get_pbi_string(power_view)
        if pbi_string:
            args.append(pbi_string)

        return "\n".join(args)


@dataclass
class TCPConnection(_PBIConnection):
    """Connection class for ethernet hardware debugger via TCP.

    This Connection is a subtype of PBIConnection and is only available for debugger from the X-Series.
    """

    node_name: str
    """The key value specifies the node name of the PowerDebug device to connect to. This should be either a DNS
    name or an IP address."""
    port: int = 0
    """TCP Port to which PowerView should send its packets on debugger module. If 0, a default port is used."""
    compression: bool = False
    """If ``True`` reduces the packet size by compression."""
    connect_mode: ConnectMode = ConnectMode.NORMAL
    """Specify reaction if debugger is already in use."""
    exclusive: bool = False
    """Tells TRACE32 that there can be only one TRACE32 PowerView instance to connect."""

    def __post_init__(self) -> None:
        super().__init__()

    def _get_connection_config(self) -> str:
        args = ["PBI=", "NETTCP", f"NODE={self.node_name}"]
        if self.port:
            args.append(f"PORT={self.port}")
        if self.compression:
            args.append("COMPRESS")
        if self.connect_mode != ConnectMode.NORMAL:
            args.append(f"CONNECTIONMODE={self.connect_mode.name}")
        return "\n".join(args)

    def _get_config_string(self, power_view: "PowerView") -> str:
        args = [self._get_connection_config()]
        index = self._get_core_num(power_view)
        if self.exclusive:
            if index != 0:
                raise ValueError("GUI index too high to generate config files using exclusive mode!")
            args.append("CORE=0")
        if index > 0:
            args.append(f"CORE={index}")
        pbi_string = self._get_pbi_string(power_view)
        if pbi_string:
            args.append(pbi_string)

        return "\n".join(args)


@dataclass
class CitrixConnection(_PBIConnection):
    node_name: str = ""
    """The key value specifies the node name of the PowerDebug device to connect to. This should be either a DNS name or
    an IP address."""

    def __post_init__(self) -> None:
        super().__init__()

    def _get_connection_config(self) -> str:
        args = ["PBI=", "CITRIX"]
        if self.node_name:
            args.append(f"NODE={self.node_name}")
        return "\n".join(args)

    def _get_config_string(self, power_view: "PowerView") -> str:
        args = [self._get_connection_config()]
        index = self._get_core_num(power_view)
        if index > 0:
            args.append(f"CORE={index}")
        pbi_string = self._get_pbi_string(power_view)
        if pbi_string:
            args.append(pbi_string)
        return "\n".join(args)


@dataclass
class USBProxyConnection(_PBIConnection):
    """TRACE32 allows to communicate with a usb debug module from a remote PC.

    In order to implement this communication, the command line tool ``t32tcpusb`` has to be started on the PC to which
    the debug module is connected. ``t32tcpusb`` can be found in the ``bin/<target_os>`` directory of your TRACE32
    installation (e.g. ``bin/windows64``).
    """

    node_name: str
    """DNS name or IP address of PC that runs ``t32tcpusb``."""
    port: int
    """Port number that was specified when ``t32tcpusb`` was started."""
    device_name: str = ""
    """A name is required if several debug modules are connected via USB and used simultaneously.
    The manufacturing default device name is the serial number of the debug module. e.g. ``NODE=E18110012345``"""
    device_path: "PathType" = ""
    """Linux only: Use this option to select the debug module to use if several debug modules are connected via USB."""

    def __post_init__(self) -> None:
        super().__init__()

    def _get_connection_config(self) -> str:
        args = ["PBI=", "USB"]
        if self.device_name:
            args.append(f"NODE={self.device_name}")
        if self.device_path and platform.system() == "Linux":
            args.append(f"DEVPATH={self.device_path}")
        args.extend((f"PROXYNAME={self.node_name}", f"PROXYPORT={self.port}"))
        return "\n".join(args)

    def _get_config_string(self, power_view: "PowerView") -> str:
        args = [self._get_connection_config()]
        index = self._get_core_num(power_view)
        if index > 0:
            args.append(f"CORE={index}")
        pbi_string = self._get_pbi_string(power_view)
        if pbi_string:
            args.append(pbi_string)
        return "\n".join(args)


@dataclass
class MCIServerConnection(_MultiConnection):
    """start a TRACE32 as a back-end using an MCI server (t32mciserver)."""

    node_name: str = "localhost"
    """The key value specifies the node name of the PowerDebug device to connect to. This should be either a DNS
    name or an IP address."""
    port: int = 30000
    """TCP-port number of MCI-Server. All started PowerView GUIs that belong to one target system must use the same PORT
    and NODE in order to connect to the same MCI-server. The used port of the dedicated MCI-Server is passed by a
    command line parameter of t32mciserver[.exe]."""
    dedicated: bool = False
    """Prohibits to start the integrated MCI-server when there is no response from an already started MCI-server at
    localhost. Use this option when t32mciserver shall be started explicitly at localhost."""

    def __post_init__(self) -> None:
        super().__init__()

    def _get_config_string(self, power_view: "PowerView") -> str:
        args = ["PBI=MCISERVER"]
        if self.dedicated:
            args.append("DEDICATED")
        if self.node_name:
            args.append(f"NODE={self.node_name}")
        if self.port != 30000:
            args.append(f"PORT={self.port}")
        index = self._get_core_num(power_view)
        if index > 0:
            args.append(f"CORE={index}")
        return "\n".join(args)


@dataclass
class SimulatorConnection(_SingleConnection):
    license_connection: Optional[_PBIConnection] = None
    """Specifies a hardware-based TRACE32 debugger connection to use its license

    Available are:
        ``USBConnection``
        ``UDPConnection``
        ``TCPConnection``
        ``CitrixConnection``
        ``USBProxyConnection``
    """

    def __post_init__(self) -> None:
        super().__init__()

    def _get_config_string(self, power_view: "PowerView") -> str:
        if self.license_connection:
            cfg = self.license_connection._get_connection_config()
            return cfg.replace("PBI=", "PBI=*SIM") + "\nINSTANCE=AUTO"
        else:
            return "PBI=SIM"


# TODO: Is there also a license connection like in SimulatorConnection?
class ViewerConnection(_SingleConnection):
    """Connection to perform off-line analysis of memory dumps and trace recordings

    Available since TRACE32 build 158910.
    """

    def __init__(self) -> None:
        super().__init__()

    def _get_config_string(self, power_view: "PowerView") -> str:
        return "PBI=VIEWER"


class InteractiveConnection(_SingleConnection):
    """This mode allows to start PowerView without a connection to a debug module / simulator etc.
    Several windows will guide through the connection process.

    Available since TRACE32 build 167333.
    """

    def __init__(self) -> None:
        super().__init__()

    def _get_config_string(self, power_view: "PowerView") -> str:
        return "PBI=INTERACTIVECONNECTION"


class GDBConnection(_SingleConnection):
    """TRACE32 as GDB Front-End."""

    def __init__(self) -> None:
        super().__init__()

    def _get_config_string(self, power_view: "PowerView") -> str:
        return "PBI=GDB"


class HostConnection(_SingleConnection):
    """TRACE32 as host process debugger."""

    def __init__(self) -> None:
        super().__init__()

    def _get_config_string(self, power_view: "PowerView") -> str:
        return "PBI=HOST"


class MCILibConnection(_SingleConnection):
    """TRACE32 as a back-end using the Lauterbach debug driver library hostmci."""

    def __init__(self) -> None:
        super().__init__()

    def _get_config_string(self, power_view: "PowerView") -> str:
        return "PBI=MCILIB"


@dataclass
class SerialRomMonitorConnection(_SingleConnection):
    port: str = "COM1"
    baudrate: int = 57600

    def __post_init__(self) -> None:
        super().__init__()

    def _get_config_string(self, power_view: "PowerView") -> str:
        return f"PBI={self.port} BAUD={self.baudrate}"


@dataclass
class MCDConnection(_SingleConnection):
    """TRACE32 to debug via the MultiCore Debug interface MCD.

    Refer to “Virtual Targets User’s Guide” (virtual_targets.pdf) for more information."""

    library_file: "PathType"
    """Required library file.

    Please contact the manufacturer of the virtual target for the required .dll file.
    """

    def __post_init__(self) -> None:
        super().__init__()

    def _get_config_string(self, power_view: "PowerView") -> str:
        arg = "PBI=MCD"
        if self.library_file:
            arg = " ".join([arg, str(self.library_file)])
        return arg


@dataclass
class CADIConnection(_SingleConnection):
    """Arm Cycle Accurate Debug Interface CADI."""

    library_file: "PathType" = ""
    """Optional library file.

    The library file is provided by Lauterbach and is installed together with TRACE32. Specifying a library file
    (.dll) is optional
    """

    def __post_init__(self) -> None:
        super().__init__()

    def _get_config_string(self, power_view: "PowerView") -> str:
        arg = "PBI=CADI"
        if self.library_file:
            arg = " ".join([arg, str(self.library_file)])
        return arg


@dataclass
class IRISConnection(_SingleConnection):
    """TRACE32 to debug via the Arm Cycle Accurate Debug Interface.

    Refer to “Virtual Targets User’s Guide” (virtual_targets.pdf) for more information."""

    library_file: "PathType" = ""
    """Optional library file.

    The library file is provided by Lauterbach and is installed together with TRACE32. Specifying a library file
    (.dll) is optional
    """

    def __post_init__(self) -> None:
        super().__init__()

    def _get_config_string(self, power_view: "PowerView") -> str:
        arg = "PBI=IRIS"
        if self.library_file:
            arg = " ".join([arg, str(self.library_file)])
        return arg


class ARCINTConnection(_SingleConnection):
    """TRACE32 for debugging using the ARCINT interface.

    Refer to “Simulator for ARC” (simulator_arc.pdf) for more information."""

    def __init__(self) -> None:
        super().__init__()

    def _get_config_string(self, power_view: "PowerView") -> str:
        return "PBI=ARCINT"


@dataclass
class GDIConnection(_SingleConnection):
    """TRACE32 to debug via the Generic Debug Instrument Interface GDI.

    Refer to “Virtual Targets User’s Guide” (virtual_targets.pdf) for more information."""

    library_file: "PathType" = ""
    """Required library file.

    Please contact the manufacturer of the virtual target for the required .dll file."""

    def __post_init__(self) -> None:
        super().__init__()

    def _get_config_string(self, power_view: "PowerView") -> str:
        arg = "PBI=GDI"
        if self.library_file:
            arg = " ".join([arg, str(self.library_file)])
        return arg


class MDIConnection(_SingleConnection):
    """TRACE32 to debug via MDI (MIPS Debug Interface) simulator.

    Refer to “Virtual Targets User’s Guide” (virtual_targets.pdf) for more information."""

    def __init__(self) -> None:
        super().__init__()

    def _get_config_string(self, power_view: "PowerView") -> str:
        return "PBI=MDI"


class SCSConnection(_SingleConnection):
    """TRACE32 to debug via the SCS StarCore simulator."""

    def __init__(self) -> None:
        super().__init__()

    def _get_config_string(self, power_view: "PowerView") -> str:
        return "PBI=SCS"


class SIMTSIConnection(_SingleConnection):
    """TRACE32 to debug via the Target Server from Texas Instruments.

    Refer to “Virtual Targets User’s Guide” (virtual_targets.pdf) for more information."""

    def __init__(self) -> None:
        super().__init__()

    def _get_config_string(self, power_view: "PowerView") -> str:
        return "PBI=SIMTSI"
