import unittest
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

from lauterbach.trace32.pystart._connection import (
    _MultiConnection,
    _PBIConnection,
    _SingleConnection,
)

if TYPE_CHECKING:
    from lauterbach.trace32.pystart import PowerView


class TestPBIConnection(unittest.TestCase):
    class PBIConMock(_PBIConnection):
        def _get_connection_config(self) -> str:
            return ""

        def _get_config_string(self, power_view: "PowerView") -> str:
            return ""

    def setUp(self) -> None:
        self.connection = TestPBIConnection.PBIConMock()

    def test_add(self):
        mock1 = MagicMock()
        mock2 = MagicMock()

        self.connection._register(mock1)
        self.connection._register(mock2, pbi_index=2)

        r = self.connection._registry

        self.assertEqual(len(r[0]), 1)
        self.assertEqual(len(r[1]), 0)
        self.assertEqual(len(r[2]), 1)
        self.assertIs(r[0][0], mock1)
        self.assertIs(r[2][0], mock2)

    def test_get_core_num_single(self):
        mock1 = MagicMock()
        mock2 = MagicMock()

        self.connection._register(mock1)
        self.connection._register(mock2, pbi_index=2)

        core_num1 = self.connection._get_core_num(mock1)
        self.assertEqual(core_num1, 0)
        core_num2 = self.connection._get_core_num(mock2)
        self.assertEqual(core_num2, 0)

    def test_get_core_num_multiple(self):
        dev_pbi0 = [MagicMock() for _ in range(3)]
        dev_pbi3 = [MagicMock() for _ in range(5)]

        for dev in dev_pbi0:
            self.connection._register(dev)
        for dev in dev_pbi3:
            self.connection._register(dev, pbi_index=3)

        for i, dev in enumerate(dev_pbi0, start=1):
            core_num = self.connection._get_core_num(dev)
            self.assertEqual(core_num, i)
        for i, dev in enumerate(dev_pbi3, start=1):
            core_num = self.connection._get_core_num(dev)
            self.assertEqual(core_num, i)

    def test_get_pbi_string_single_device(self):
        mock1 = MagicMock()
        self.connection._register(mock1)
        pbi_str = self.connection._get_pbi_string(mock1)
        self.assertEqual(pbi_str, "")

    def test_get_pbi_string_multiple_device(self):
        mock1 = MagicMock()
        mock2 = MagicMock()
        mock3 = MagicMock()

        self.connection._register(mock1)
        self.connection._register(mock2, pbi_index=3)
        self.connection._register(mock3, pbi_index=2)
        self.connection._register(mock3, pbi_index=3)

        pbi_str1 = self.connection._get_pbi_string(mock1)
        pbi_str2 = self.connection._get_pbi_string(mock2)
        pbi_str3 = self.connection._get_pbi_string(mock3)

        self.assertEqual(pbi_str1, "USE=1000")
        self.assertEqual(pbi_str2, "USE=0001")
        self.assertEqual(pbi_str3, "USE=0011")


class TestMultiConnection(unittest.TestCase):
    class MultiConMock(_MultiConnection):
        def _get_config_string(self, power_view: "PowerView") -> str:
            return ""

    def setUp(self) -> None:
        self.connection = TestMultiConnection.MultiConMock()

    def test_add(self):
        devices = [MagicMock() for _ in range(5)]

        for dev in devices:
            self.connection._register(dev)

        self.assertListEqual(self.connection._registry, devices)

    def test_error_on_pbi_index(self):
        dev = MagicMock()

        with self.assertRaises(Exception):
            self.connection._register(dev, pbi_index=1)

    def test_get_core_num_single(self):
        mock1 = MagicMock()
        self.connection._register(mock1)
        core_num1 = self.connection._get_core_num(mock1)
        self.assertEqual(core_num1, 0)

    def test_get_core_num_multiple(self):
        devices = [MagicMock() for _ in range(3)]

        for dev in devices:
            self.connection._register(dev)

        for i, dev in enumerate(devices, start=1):
            core_num = self.connection._get_core_num(dev)
            self.assertEqual(core_num, i)


class TestSingleConnection(unittest.TestCase):
    class SingleConMock(_SingleConnection):
        def _get_config_string(self, power_view: "PowerView") -> str:
            return ""

    def setUp(self) -> None:
        self.connection = TestSingleConnection.SingleConMock()

    def test_add_single(self):
        mock1 = MagicMock()
        mock2 = MagicMock()

        self.connection._register(mock1)
        self.assertIs(self.connection._registry, mock1)

        with self.assertRaises(Exception):
            self.connection._register(mock2)

    def test_error_on_pbi_index(self):
        dev = MagicMock()

        with self.assertRaises(Exception):
            self.connection._register(dev, pbi_index=1)


if __name__ == "__main__":
    unittest.main()
