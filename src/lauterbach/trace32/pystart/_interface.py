from dataclasses import dataclass
from typing import Optional

from ._powerview import T32Interface


@dataclass
class RCLInterface(T32Interface):
    """TRACE32 Remote API for TCP/IP and UDP.

    It defines the parameters for the TRACE32 Remote API for TCP/IP and UDP. Even if the
    configuration is performed for both protocols, it is recommended to use TCP/IP. Please refer to “API for Remote
    Control and JTAG Access in C” (api_remote_c.pdf) for more information and “Controlling TRACE32 via Python 3”
    (app_python.pdf). Multiple instances are allowed.
    """

    _RCL_PROTOCOLS = {
        "TCP": "NETTCP",
        "UDP": "NETASSIST",
    }

    port: int = 20000
    """ Lets the TRACE32 instance listen to the UDP/TCP port."""
    packlen: int = 1024
    """Specifies the maximum data package length for UDP. No operation for TCP."""
    protocol: str = "TCP"
    """Starting from the TRACE32 release 09.2020, the API supports per default TCP socket
    streams. Previous TRACE32 versions only support a communication via UDP
    sockets."""
    allow_remote_host: Optional[bool] = None
    """If set to `false`, only connections from `localhost` are allowed. If set to `true` also connections from remote
    hosts != localhost are allowed. If set to `None`, the default set in Trace32 is used.

    Available since TRACE32 build 172541."""

    def _get_config_string(self) -> str:
        interface_name = self._RCL_PROTOCOLS[self.protocol]
        args = [
            f";T32 API Access ({self.protocol})",
            f"RCL={interface_name}",
            f"PORT={self.port}",
        ]
        if interface_name == "NETASSIST":
            args.append(f"PACKLEN={self.packlen}")
        if self.allow_remote_host is not None:
            args.append("REMOTEHOSTALLOW" if self.allow_remote_host else "REMOTEHOSTDENY")
        return "\n".join(args)

    @classmethod
    def _get_max_instances(cls) -> Optional[int]:
        return None


@dataclass
class IntercomInterface(T32Interface):
    """Over this interface the PowerView instance can be controlled via an other PowerView instance.

    It defines the parameter for the communication between multiple TRACE32 PowerView
    instances. Only one instance is allowed.
    """

    name: str = ""
    """Assign a name to the TRACE32 PowerView interface. This name can then be
    used with the ``InterCom`` commands. The selected name can be displayed in
    TRACE32 PowerView using the ``SYnch.state`` command."""
    port: int = 10000
    """Lets the TRACE32 instance listen to specified port."""
    packlen: int = 1024
    """Specifies the maximum data package length for UDP."""

    def _get_config_string(self) -> str:
        args = [
            "IC=NETASSIST",
            f"PORT={self.port}",
            f"PACKLEN={self.packlen}",
        ]
        if self.name:
            args.append(f"NAME={self.name}")
        return "\n".join(args)

    @classmethod
    def _get_max_instances(cls) -> Optional[int]:
        return 1


@dataclass
class GDBInterface(T32Interface):
    """Over this interface TRACE32 can be used as a GDB backend.

    It defines the parameters for controlling TRACE32 PowerView as GDB Back-End. Please
    refer to “TRACE32 as GDB Back-End” (backend_gdb.pdf) for more information. Only one instance is allowed.
    """

    _GDB_PROTOCOLS = ["TCP", "UDP"]

    port: int = 30000
    """Lets the TRACE32 instance listen to the UDP/TCP port."""
    protocol: str = "TCP"
    """``"TCP"`` (default) or ``"UDP"``."""
    packlen: int = 1024
    """Specifies the maximum data package length for UDP. No operation for TCP."""

    def _get_config_string(self) -> str:
        if self.protocol not in self._GDB_PROTOCOLS:
            raise ValueError(f"protocol must be one of {self._GDB_PROTOCOLS}")

        args = [
            # ";T32 GDB",
            "GDB=NETASSIST",
            f"PORT={self.port}",
            f"PROTOCOL={self.protocol}",
        ]
        if self.protocol == "UDP":
            args.append(f"PACKLEN={self.packlen}")
        return "\n".join(args)

    @classmethod
    def _get_max_instances(cls) -> Optional[int]:
        return 1


@dataclass
class TCFInterface(T32Interface):
    """Control TRACE32 via Target Communication Framework (TCF) from an Eclipse-based interface.

    It defines the parameter for controlling TRACE32 PowerView via Target Communication
    Framework (TCF) from an Eclipse-based interface. Please refer to “TRACE32 as TCF Agent” (app_tcf_setup.pdf) for
    more information. Only one instance is allowed.
    """

    port: Optional[int] = None
    """Lets the TRACE32 instance listen to the TCP port. ``None`` is used for TCF's default port."""
    allow_remote_host: Optional[bool] = None
    """If set to `false`, only connections from `localhost` are allowed. If set to `true` also connections from remote
    hosts != localhost are allowed. If set to `None`, the default set in Trace32 is used.

    Available since TRACE32 build 172541."""

    def _get_config_string(self) -> str:
        args = ["TCF="]
        if self.port is not None:
            args.append(f"PORT={self.port}")
        if self.allow_remote_host is not None:
            args.append("REMOTEHOSTALLOW" if self.allow_remote_host else "REMOTEHOSTDENY")
        return "\n".join(args)

    @classmethod
    def _get_max_instances(cls) -> Optional[int]:
        return 1


@dataclass
class SimulinkInterface(T32Interface):
    """Interface for TRACE32 Integration for Simulink."""

    port: int
    """Lets the TRACE32 instance listen to the UDP port."""
    allow_remote_host: Optional[bool] = None
    """If set to `false`, only connections from `localhost` are allowed. If set to `true` also connections from remote
    hosts != localhost are allowed. If set to `None`, the default set in Trace32 is used.

    Available since TRACE32 build 172541."""

    def _get_config_string(self) -> str:
        args = ["SIMULINK=NETASSIST", f"PORT={self.port}"]
        if self.allow_remote_host is not None:
            args.append("REMOTEHOSTALLOW" if self.allow_remote_host else "REMOTEHOSTDENY")
        return "\n".join(args)

    @classmethod
    def _get_max_instances(cls) -> Optional[int]:
        return 1
