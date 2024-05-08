import unittest
from typing import Optional

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


DEFAULTARGS = {
    RCLInterface: (),
    TCFInterface: (),
    IntercomInterface: (),
    GDBInterface: (),
    SimulinkInterface: (1234,),
    MockInterface: (),
}

CONFIGKEYS = {
    RCLInterface: "RCL=",
    TCFInterface: "TCF=",
    IntercomInterface: "IC=",
    GDBInterface: "GDB=",
    SimulinkInterface: "SIMULINK=",
    MockInterface: "Mock=",
}


class TestAddInterface(unittest.TestCase):
    def test_addWrongType(self):
        pv = PowerView(SimulatorConnection(), "t32marm")
        with self.assertRaises(ValueError):
            pv.add_interface(123)

    def test_addMultipleInterfaces_when_mostly_one_allowed(self):
        interfaces = [TCFInterface, IntercomInterface, GDBInterface, SimulinkInterface]
        for interface in interfaces:
            args = DEFAULTARGS[interface]
            with self.subTest(interface=interface.__name__):
                pv = PowerView(SimulatorConnection(), "t32marm")
                pv.add_interface(interface(*args))
                with self.assertRaises(ValueError):
                    pv.add_interface(interface(*args))

    def test_addMultipleInterfaces_when_multiple_allowed(self):
        interfaces = [RCLInterface]
        for interface in interfaces:
            args = DEFAULTARGS[interface]
            with self.subTest(interface=interface.__name__):
                pv = PowerView(SimulatorConnection(), "t32marm")
                for _ in range(100):
                    pv.add_interface(interface(*args))

    def test_addMoreMockInterfaces(self):
        pv = PowerView(SimulatorConnection(), "t32marm")
        for _ in range(5):
            pv.add_interface(MockInterface())

    def test_addTooMuchMockInterfaces(self):
        pv = PowerView(SimulatorConnection(), "t32marm")
        for _ in range(5):
            pv.add_interface(MockInterface())
        with self.assertRaises(ValueError):
            pv.add_interface(MockInterface())

    def test_addInterface_results_in_entry(self):
        interfaces = [RCLInterface, TCFInterface, IntercomInterface, GDBInterface, SimulinkInterface, MockInterface]
        for interface in interfaces:
            key = CONFIGKEYS[interface]
            args = DEFAULTARGS[interface]
            with self.subTest(interface=interface.__name__, key=key):
                pv = PowerView(SimulatorConnection(), "t32marm")
                pv.add_interface(interface(*args))
                self.assertIn(key, pv.get_configuration_string())

    def test_noAddedInterfaces(self):
        pv = PowerView(SimulatorConnection(), "t32marm")
        x = pv.get_configuration_string()
        for key in CONFIGKEYS.values():
            with self.subTest(key=key):
                self.assertNotIn(key, x)

    def test_addDifferentInterfaces(self):
        pv = PowerView(SimulatorConnection(), "t32marm")
        pv.add_interface(RCLInterface())
        pv.add_interface(TCFInterface())
        pv.add_interface(GDBInterface())
        pv.add_interface(IntercomInterface())
        pv.add_interface(SimulinkInterface(1234))
        pv.add_interface(MockInterface())

        x = pv.get_configuration_string()

        self.assertRegex(x, "RCL=")
        self.assertRegex(x, "TCF=")
        self.assertRegex(x, "GDB=")
        self.assertRegex(x, "IC=")
        self.assertRegex(x, "SIMULINK=")
        self.assertRegex(x, "Mock")

    def test_RCLInterface(self):
        with self.subTest(protocol="TCP"):
            x = RCLInterface(port=42, protocol="TCP")._get_config_string()
            self.assertIn("RCL=NETTCP\n", x)
            self.assertIn("PORT=42", x)
            self.assertNotIn("PACKLEN=", x)

        with self.subTest(protocol="UDP"):
            x = RCLInterface(port=43, packlen=9999, protocol="UDP")._get_config_string()
            self.assertIn("RCL=NETASSIST\n", x)
            self.assertIn("PORT=43", x)
            self.assertIn("PACKLEN=9999", x)

    def test_TCFInterface(self):
        x = TCFInterface(port=9876)._get_config_string()
        self.assertIn("TCF=\n", x)
        self.assertIn("PORT=9876", x)

    def test_IntercomInterface(self):
        x = IntercomInterface(name="ABCDE", port=1234, packlen=9876)._get_config_string()
        self.assertIn("IC=NETASSIST\n", x)
        self.assertIn("PORT=1234", x)
        self.assertIn("PACKLEN=9876", x)
        self.assertIn("NAME=ABCDE", x)

    def test_GDBInterface(self):
        with self.subTest(protocol="TCP"):
            x = GDBInterface(port=1233, protocol="TCP", packlen=9876)._get_config_string()
            self.assertIn("GDB=NETASSIST\n", x)
            self.assertIn("PROTOCOL=TCP", x)
            self.assertIn("PORT=1233", x)
            self.assertNotIn("PACKLEN=", x)
        with self.subTest(protocol="UDP"):
            x = GDBInterface(port=1234, protocol="UDP", packlen=9876)._get_config_string()
            self.assertIn("GDB=NETASSIST\n", x)
            self.assertIn("PROTOCOL=UDP", x)
            self.assertIn("PORT=1234", x)
            self.assertIn("PACKLEN=9876", x)

    def test_SimulinkInterface(self):
        x = SimulinkInterface(1234)._get_config_string()
        self.assertIn("SIMULINK=NETASSIST\n", x)
        self.assertIn("PORT=1234", x)


if __name__ == "__main__":
    unittest.main()
