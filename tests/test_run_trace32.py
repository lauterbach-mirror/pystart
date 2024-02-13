import os
import unittest
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
        DELAY = 0.4
        instances = [pystart.PowerView(pystart.SimulatorConnection(), self.target) for _ in range(N)]
        self.open_close_instances(instances, DELAY)

    def test_many_simulators_different_id(self):
        N = 20
        DELAY = 0
        instances = [pystart.PowerView(pystart.SimulatorConnection(), self.target) for _ in range(N)]
        for i, pv in enumerate(instances):
            pv.id = f"inst{i:02}"
        self.open_close_instances(instances, DELAY)

    def test_usb_amp_setup(self):
        N = 4
        DELAY = 2
        con = pystart.USBConnection()
        instances = [pystart.PowerView(con, self.target) for _ in range(N)]
        self.open_close_instances(instances, DELAY)

    def open_close_instances(self, instances: "List[pystart.PowerView]", delay: float) -> None:
        for port, pv in enumerate(instances, start=self.first_rcl_port):
            pv.add_interface(pystart.RCLInterface(port))

        for pv in instances:  # run start() calls as close together as possible
            pv.start(delay=delay)

        err_lst = ["PowerView instances started with unexpected output:"]
        try:
            for port in range(self.first_rcl_port, self.first_rcl_port + len(instances)):
                with pyrcl.connect(port=port) as dbg:
                    line = dbg.fnc.area_line("A000", 0)
                    if line and not line.startswith(("INFO:", "Detected two whisker cables.")):
                        err_lst.append(line)
                    dbg.cmd("QUIT")
        except Exception as ex:
            for pv in instances:
                pv.stop()
            self.fail(ex)

        for pv in instances:
            pv.wait(timeout=1.1)

        self.assertEqual(len(err_lst) - 1, 0, "\n  - ".join(err_lst))


if __name__ == "__main__":
    unittest.main()
