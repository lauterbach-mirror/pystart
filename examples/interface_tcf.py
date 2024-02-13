from util import show_configuration

from lauterbach.trace32.pystart import PowerView, TCFInterface, USBConnection

powerview = PowerView(USBConnection(), "t32marm")

powerview.add_interface(TCFInterface())

show_configuration(powerview)
