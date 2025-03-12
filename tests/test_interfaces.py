import re
import unittest
from typing import Any, Dict, Optional

from lauterbach.trace32.pystart import (
    GDBInterface,
    IntercomInterface,
    PowerView,
    RCLInterface,
    SimulatorConnection,
    SimulinkInterface,
    TCFInterface,
)
from lauterbach.trace32.pystart._powerview import T32Interface


class MockInterface(T32Interface):  # type: ignore
    def _get_config_string(self) -> str:
        return "Mock="

    @classmethod
    def _get_max_instances(cls) -> Optional[int]:
        return 5


INTERFACES: Dict[T32Interface, Dict[str, Any]] = {
    RCLInterface: {"CONFIGKEY": "RCL=", "DEFAULTARGS": (), "MAX_INSTANCES": None},
    TCFInterface: {"CONFIGKEY": "TCF=", "DEFAULTARGS": (), "MAX_INSTANCES": 1},
    IntercomInterface: {"CONFIGKEY": "IC=", "DEFAULTARGS": (), "MAX_INSTANCES": 1},
    GDBInterface: {"CONFIGKEY": "GDB=", "DEFAULTARGS": (), "MAX_INSTANCES": 1},
    SimulinkInterface: {"CONFIGKEY": "SIMULINK=", "DEFAULTARGS": (1234,), "MAX_INSTANCES": 1},
    MockInterface: {
        "CONFIGKEY": "Mock=",
        "DEFAULTARGS": (),
        "MAX_INSTANCES": 5,
    },
}


class TestAddInterface(unittest.TestCase):
    def test_addWrongType(self):
        pv = PowerView(SimulatorConnection(), "t32marm")
        with self.assertRaises(ValueError):
            pv.add_interface(int())

    def test_addInterfaces(self):
        for interface, settings in INTERFACES.items():
            args = settings["DEFAULTARGS"]
            max_instances = interface._get_max_instances()
            self.assertEqual(max_instances, settings["MAX_INSTANCES"])
            pv = PowerView(SimulatorConnection(), "t32marm")

            if max_instances is None:
                with self.subTest(interface=interface.__name__, test="add many interfaces"):
                    for _ in range(100):
                        pv.add_interface(interface(*args))
            else:
                with self.subTest(interface=interface.__name__, test="add maximum number of interfaces"):
                    for _ in range(max_instances):
                        pv.add_interface(interface(*args))
                with self.subTest(interface=interface.__name__, test="add too much interfaces"):
                    with self.assertRaises(ValueError):
                        pv.add_interface(interface(*args))

    def test_addInterface_results_in_entry(self):
        for interface, settings in INTERFACES.items():
            key = settings["CONFIGKEY"]
            args = settings["DEFAULTARGS"]
            pv = PowerView(SimulatorConnection(), "t32marm")
            pv.add_interface(interface(*args))
            x = pv.get_configuration_string()

            with self.subTest(interface=interface.__name__, key=key, test="contains key"):
                self.assertRegex(x, re.compile(f"^{key}", flags=re.MULTILINE))
            with self.subTest(interface=interface.__name__, key=key, test="not contain other key"):
                for i2, s2 in INTERFACES.items():
                    if i2 == interface:
                        continue
                    key2 = s2["CONFIGKEY"]
                    self.assertNotRegex(x, re.compile(f"^{key2}"))

    def test_noAddedInterfaces(self):
        pv = PowerView(SimulatorConnection(), "t32marm")
        x = pv.get_configuration_string()
        for key in (tmp["CONFIGKEY"] for tmp in INTERFACES.values()):
            with self.subTest(key=key):
                self.assertNotIn(key, x)

    def test_addDifferentInterfaces(self):
        pv = PowerView(SimulatorConnection(), "t32marm")
        for interface, settings in INTERFACES.items():
            args = settings["DEFAULTARGS"]
            pv.add_interface(interface(*args))

        x = pv.get_configuration_string()

        for interface, settings in INTERFACES.items():
            key = settings["CONFIGKEY"]
            self.assertRegex(x, re.compile(f"^{key}", flags=re.MULTILINE))

    def test_RCLInterface(self):
        with self.subTest(protocol="TCP"):
            x = RCLInterface(port=42, protocol="TCP")._get_config_string()
            self.assertRegex(x, re.compile("^RCL=NETTCP$", flags=re.MULTILINE))
            self.assertRegex(x, re.compile("^PORT=42$", flags=re.MULTILINE))
            self.assertRegex(x, re.compile("^RCL=NETTCP$", flags=re.MULTILINE))
            self.assertNotRegex(x, re.compile("^PACKLEN=", flags=re.MULTILINE))

        with self.subTest(protocol="UDP"):
            x = RCLInterface(port=43, packlen=9999, protocol="UDP")._get_config_string()
            self.assertRegex(x, re.compile("^RCL=NETASSIST$", flags=re.MULTILINE))
            self.assertRegex(x, re.compile("^PORT=43$", flags=re.MULTILINE))
            self.assertRegex(x, re.compile("^PACKLEN=9999$", flags=re.MULTILINE))

    def test_TCFInterface(self):
        x = TCFInterface(port=9876)._get_config_string()
        self.assertRegex(x, re.compile("^TCF=$", flags=re.MULTILINE))
        self.assertRegex(x, re.compile("^PORT=9876$", flags=re.MULTILINE))

    def test_IntercomInterface(self):
        x = IntercomInterface(name="ABCDE", port=1234, packlen=9876)._get_config_string()
        self.assertRegex(x, re.compile("^IC=NETASSIST$", flags=re.MULTILINE))
        self.assertRegex(x, re.compile("^PORT=1234$", flags=re.MULTILINE))
        self.assertRegex(x, re.compile("^PACKLEN=9876$", flags=re.MULTILINE))
        self.assertRegex(x, re.compile("^NAME=ABCDE$", flags=re.MULTILINE))

    def test_GDBInterface(self):
        with self.subTest(protocol="TCP"):
            x = GDBInterface(port=1233, protocol="TCP", packlen=9876)._get_config_string()
            self.assertRegex(x, re.compile("^GDB=NETASSIST$", flags=re.MULTILINE))
            self.assertRegex(x, re.compile("^PROTOCOL=TCP$", flags=re.MULTILINE))
            self.assertRegex(x, re.compile("^PORT=1233$", flags=re.MULTILINE))
            self.assertNotRegex(x, re.compile("^PACKLEN=", flags=re.MULTILINE))
        with self.subTest(protocol="UDP"):
            x = GDBInterface(port=1234, protocol="UDP", packlen=9876)._get_config_string()
            self.assertRegex(x, re.compile("^GDB=NETASSIST$", flags=re.MULTILINE))
            self.assertRegex(x, re.compile("^PROTOCOL=UDP$", flags=re.MULTILINE))
            self.assertRegex(x, re.compile("^PORT=1234$", flags=re.MULTILINE))
            self.assertRegex(x, re.compile("^PACKLEN=9876$", flags=re.MULTILINE))

    def test_SimulinkInterface(self):
        x = SimulinkInterface(1234)._get_config_string()
        self.assertRegex(x, re.compile("^SIMULINK=NETASSIST$", flags=re.MULTILINE))
        self.assertRegex(x, re.compile("^PORT=1234$", flags=re.MULTILINE))


class TestInterface_AllowRemoteHost(unittest.TestCase):
    INTERFACES_OF_INTEREST = [RCLInterface, TCFInterface, SimulinkInterface]
    REMOTEHOSTALLOW = re.compile("^REMOTEHOSTALLOW$", flags=re.MULTILINE)
    REMOTEHOSTDENY = re.compile("^REMOTEHOSTDENY$", flags=re.MULTILINE)

    def test_remotehostallow(self):
        kwargs = {"allow_remote_host": True}
        for interface in self.INTERFACES_OF_INTEREST:
            args = INTERFACES[interface]["DEFAULTARGS"]
            with self.subTest(interface=interface.__name__):
                config_string = interface(*args, **kwargs)._get_config_string()
                self.assertRegex(config_string, self.REMOTEHOSTALLOW)
                self.assertNotRegex(config_string, self.REMOTEHOSTDENY)

    def test_remotehostdeny(self):
        kwargs = {"allow_remote_host": False}
        for interface in self.INTERFACES_OF_INTEREST:
            args = INTERFACES[interface]["DEFAULTARGS"]
            with self.subTest(interface=interface.__name__):
                config_string = interface(*args, **kwargs)._get_config_string()
                self.assertNotRegex(config_string, self.REMOTEHOSTALLOW)
                self.assertRegex(config_string, self.REMOTEHOSTDENY)

    def test_remotehostnone(self):
        kwargs = {"allow_remote_host": None}
        for interface in self.INTERFACES_OF_INTEREST:
            args = INTERFACES[interface]["DEFAULTARGS"]
            with self.subTest(interface=interface.__name__):
                config_string = interface(*args, **kwargs)._get_config_string()
                self.assertNotRegex(config_string, self.REMOTEHOSTALLOW)
                self.assertNotRegex(config_string, self.REMOTEHOSTDENY)


if __name__ == "__main__":
    unittest.main()
