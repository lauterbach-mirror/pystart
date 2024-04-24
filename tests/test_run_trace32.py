import os
import unittest
from subprocess import TimeoutExpired
from typing import List

import dotenv
import lauterbach.trace32.rcl as pyrcl

import lauterbach.trace32.pystart as pystart


def setUpModule():
    dotenv.load_dotenv()


class TestRunTrace32(unittest.TestCase):
    def setUp(self) -> None:
        self.first_rcl_port = 20000
        self.target = os.getenv("T32TARGET", "t32marm")

    def test_many_simulators(self):
        N = 20
        instances = [pystart.PowerView(pystart.SimulatorConnection(), self.target) for _ in range(N)]
        self.open_close_instances(instances)

    def test_many_simulators_different_id(self):
        N = 20
        instances = [pystart.PowerView(pystart.SimulatorConnection(), self.target) for _ in range(N)]
        for i, pv in enumerate(instances):
            pv.id = f"inst{i:02}"
        self.open_close_instances(instances)

    def test_usb_amp_setup(self):
        N = 4
        con = pystart.USBConnection()
        instances = [pystart.PowerView(con, self.target) for _ in range(N)]
        self.open_close_instances(instances)

    def open_close_instances(self, instances: "List[pystart.PowerView]", timeout: float = 10) -> None:
        for port, pv in enumerate(instances, start=self.first_rcl_port):
            pv.add_interface(pystart.RCLInterface(port))

        try:
            for pv in instances:  # run start() calls as close together as possible
                pv.start(timeout=timeout)

            for port in range(self.first_rcl_port, self.first_rcl_port + len(instances)):
                with pyrcl.connect(port=port) as dbg:
                    self.assertFalse(dbg.fnc.error_occurred())
                    dbg.cmd("QUIT")
        except Exception as ex:
            for pv in instances:
                try:
                    pv.stop()
                except TimeoutExpired:
                    pv._process.kill()
            self.fail(ex)

        for pv in instances:
            pv.wait(timeout=1.1)


if __name__ == "__main__":
    unittest.main()
