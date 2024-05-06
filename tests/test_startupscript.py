import itertools
import os
import tempfile
import time
import typing
import unittest

import dotenv
import lauterbach.trace32.rcl as pyrcl

import lauterbach.trace32.pystart as pystart

STARTUP_SCRIPT_CONTENT = """ON ERROR CONTinue
GLOBAL &entry_a &entry_b &entry_c &entry_d &entry_e
GLOBAL &sLine
ENTRY &entry_a &entry_b &entry_c &entry_d &entry_e
ENTRY %LINE &sLine
PARAMETERS &parameters_a &parameters_b &parameters_c &parameters_d &parameters_e
pstep ; extend lifetime of PRIVATE parameters
"""


def setUpModule():
    dotenv.load_dotenv()


class TestRunWithStartupScript(unittest.TestCase):
    _powerview_delay = 0.2  # Delay between starting trace32 and connecting via pyrcl
    _startup_script = ""
    _rcl_ports = itertools.count(20000)

    @classmethod
    def setUpClass(cls):
        with tempfile.NamedTemporaryFile("w", suffix=".cmm", delete=False) as f:
            cls._startup_script = f.name
            f.write(STARTUP_SCRIPT_CONTENT)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls._startup_script)

    def setUp(self) -> None:
        self.target = os.getenv("T32TARGET", "t32marm")
        self.pv = pystart.PowerView(pystart.SimulatorConnection(), self.target)
        self.pv.startup_script = self._startup_script

    def test_no_parameter_without_script(self):
        self.pv.startup_script = None
        self.pv.startup_parameter = ["PARAMETER"]
        self.assertNotIn("PARAMETER", self.pv._get_popen_args())

    def test_parameter_and_script_list(self):
        self.pv.startup_parameter = ["PARAMETER1", "PARAMETER2"]

        args = self.pv._get_popen_args()
        self.assertIn("-s", args)
        idx = args.index("-s")
        self.assertEqual(args[idx + 1], self._startup_script)
        self.assertEqual(args[idx + 2], "PARAMETER1")
        self.assertEqual(args[idx + 3], "PARAMETER2")

    def test_startup_parameter_list(self):
        self.pv.startup_parameter = ["a", "b c", '"d"', "KEY=value with space"]
        expected = {
            "%LINE": {
                "&sLine": 'a "b c" "d" "KEY=value with space"',
            },
            "ENTRY": {
                "&entry_a": "a",
                "&entry_b": '"b c"',
                "&entry_c": '"d"',
                "&entry_d": '"KEY=value with space"',
                "&entry_e": "",
            },
        }
        self._check_macros(expected)

    def test_startup_parameter_quoted(self):
        self.pv.startup_parameter = ['"a"', '"b c"', '"d"', '"KEY=value with space"']
        expected = {
            "PARAMETERS": {
                "&parameters_a": "a",
                "&parameters_b": "b c",
                "&parameters_c": "d",
                "&parameters_d": "KEY=value with space",
                "&parameters_e": "",
            },
            "%LINE": {"&sLine": '"a" "b c" "d" "KEY=value with space"'},
        }
        self._check_macros(expected)

    def _check_macros(self, expected: typing.Dict[str, typing.Dict[str, str]]) -> None:
        """Check if practice macros match the expacted value

        Args:
            expected (typing.Dict[str, typing.Dict[str, str]]): expected values in the format:
                {"GROUPNAME": {"MACRO_NAME": "MACRO_VALUE", [...]}, [...]}
        """
        macros = dict()
        port = next(self._rcl_ports)
        self.pv.add_interface(pystart.RCLInterface(port=port))
        self.pv.start(delay=self._powerview_delay)

        i = 0
        success = False
        while i < 20 and not success:
            try:
                with pyrcl.connect(port=port) as rcl:
                    for name in [
                        "&entry_a",
                        "&entry_b",
                        "&entry_c",
                        "&entry_d",
                        "&entry_e",
                        "&sLine",
                        "&parameters_a",
                        "&parameters_b",
                        "&parameters_c",
                        "&parameters_d",
                        "&parameters_e",
                    ]:
                        macros[name] = rcl.practice.get_macro(name).value
                    rcl.cmd("QUIT")
                    success = True
            except Exception:
                time.sleep(0.2)
                i += 1

        self.pv.wait()
        if not success:
            self.fail("Was not able to connect via RCL")

        for strategy, entries in expected.items():
            for param_name, expected_value in entries.items():
                with self.subTest(strategy=strategy, param_name=param_name):
                    self.assertEqual(macros[param_name], expected_value)


if __name__ == "__main__":
    unittest.main(verbosity=1)
