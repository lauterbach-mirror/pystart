import unittest
from typing import Optional

import lauterbach.trace32.pystart as pystart


class TestAddInterface(unittest.TestCase):
    def setUp(self) -> None:
        self.pv = pystart.PowerView(pystart.SimulatorConnection(), "t32marm")

    def test_addWrongType(self):
        with self.assertRaises(ValueError):
            self.pv.add_interface(123)

    def test_addRCLInterface(self):
        self.pv.add_interface(pystart.RCLInterface())
        x = self.pv.get_configuration_string()
        self.assertRegex(x, "RCL=")

    def test_addMoreRCLInterfaces(self):
        for _ in range(200):
            self.pv.add_interface(pystart.RCLInterface())

    def test_addTCFInterface(self):
        self.pv.add_interface(pystart.TCFInterface())
        x = self.pv.get_configuration_string()
        self.assertRegex(x, "TCF=")

    def test_addMoreTCFInterfaces(self):
        self.pv.add_interface(pystart.TCFInterface())
        with self.assertRaises(ValueError):
            self.pv.add_interface(pystart.TCFInterface())

    def test_addIntercomInterface(self):
        self.pv.add_interface(pystart.IntercomInterface())
        x = self.pv.get_configuration_string()
        self.assertRegex(x, "IC=")

    def test_addMoreIntercomInterfaces(self):
        self.pv.add_interface(pystart.IntercomInterface())
        with self.assertRaises(ValueError):
            self.pv.add_interface(pystart.IntercomInterface())

    def test_addGDBInterface(self):
        self.pv.add_interface(pystart.GDBInterface())
        x = self.pv.get_configuration_string()
        self.assertRegex(x, "GDB=")

    def test_addMoreGDBInterfaces(self):
        self.pv.add_interface(pystart.GDBInterface())
        with self.assertRaises(ValueError):
            self.pv.add_interface(pystart.GDBInterface())

    def test_addSimulinkInterface(self):
        self.pv.add_interface(pystart.SimulinkInterface(1234))
        x = self.pv.get_configuration_string()
        self.assertRegex(x, "SIMULINK=")

    def test_addMoreSimulinkInterfaces(self):
        self.pv.add_interface(pystart.SimulinkInterface(1234))
        with self.assertRaises(ValueError):
            self.pv.add_interface(pystart.SimulinkInterface(1234))

    class MockInterface(pystart._powerview.T32Interface):  # type: ignore
        def _get_config_string(self) -> str:
            return "Mock"

        @classmethod
        def _get_max_instances(cls) -> Optional[int]:
            return 5

    def test_addMockInterface(self):
        self.pv.add_interface(self.MockInterface())
        x = self.pv.get_configuration_string()
        self.assertRegex(x, "Mock")

    def test_addMoreMockInterfaces(self):
        for _ in range(5):
            self.pv.add_interface(self.MockInterface())

    def test_addTooMuchMockInterfaces(self):
        for _ in range(5):
            self.pv.add_interface(self.MockInterface())
        with self.assertRaises(ValueError):
            self.pv.add_interface(self.MockInterface())

    def test_noInterface(self):
        x = self.pv.get_configuration_string()
        self.assertNotRegex(x, "RCL=")
        self.assertNotRegex(x, "TCF=")
        self.assertNotRegex(x, "GDB=")
        self.assertNotRegex(x, "IC=")
        self.assertNotRegex(x, "SIMULINK=")
        self.assertNotRegex(x, "Mock")

    def test_addDifferentInterfaces(self):
        self.pv.add_interface(pystart.RCLInterface())
        self.pv.add_interface(pystart.TCFInterface())
        self.pv.add_interface(pystart.GDBInterface())
        self.pv.add_interface(pystart.IntercomInterface())
        self.pv.add_interface(pystart.SimulinkInterface(1234))
        self.pv.add_interface(self.MockInterface())

        x = self.pv.get_configuration_string()

        self.assertRegex(x, "RCL=")
        self.assertRegex(x, "TCF=")
        self.assertRegex(x, "GDB=")
        self.assertRegex(x, "IC=")
        self.assertRegex(x, "SIMULINK=")
        self.assertRegex(x, "Mock")


if __name__ == "__main__":
    unittest.main()
