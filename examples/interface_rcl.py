from util import show_configuration

from lauterbach.trace32.pystart import PowerView, RCLInterface, USBConnection

powerview = PowerView(USBConnection(), "t32marm")

powerview.add_interface(RCLInterface(port=20000, packlen=16384, protocol="TCP"))
powerview.add_interface(RCLInterface(port=20001, packlen=1024, protocol="UDP"))

show_configuration(powerview)
