import re
import unittest
from pathlib import Path

import lauterbach.trace32.pystart as pystart


class TestCreateConnection(unittest.TestCase):
    def testConnectionWithPathParameter(self):
        connections = [pystart.MCDConnection, pystart.CADIConnection, pystart.IRISConnection, pystart.GDIConnection]
        for con in connections:
            with self.subTest(cls=con.__name__, type="str"):
                c = con("some/string/path")
                c._get_config_string(None)
            with self.subTest(cls=con.__name__, type="Path"):
                c = con(Path("some/path/object"))
                c._get_config_string(None)


class TestConnection(unittest.TestCase):
    def test_ViewerConnection(self):
        x = pystart.ViewerConnection()

        self.assertTrue(isinstance(x, pystart._connection._SingleConnection))
        self.assertRegex(x._get_config_string(None), re.compile("^PBI=VIEWER$", flags=re.MULTILINE))

    def test_InteractiveConnection(self):
        x = pystart.InteractiveConnection()

        self.assertTrue(isinstance(x, pystart._connection._SingleConnection))
        self.assertRegex(x._get_config_string(None), re.compile("^PBI=INTERACTIVECONNECTION$", flags=re.MULTILINE))


if __name__ == "__main__":
    unittest.main()
