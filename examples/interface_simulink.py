from util import show_configuration

from lauterbach.trace32.pystart import PowerView, SimulinkInterface, USBConnection

powerview = PowerView(USBConnection(), "t32marm")

powerview.add_interface(SimulinkInterface(port=12345))

show_configuration(powerview)
