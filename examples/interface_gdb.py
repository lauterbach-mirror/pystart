from util import show_configuration

from lauterbach.trace32.pystart import GDBInterface, PowerView, USBConnection

powerview = PowerView(USBConnection(), "t32marm")

powerview.add_interface(GDBInterface(port=30000, protocol="TCP", packlen=16384))

show_configuration(powerview)
