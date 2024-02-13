import itertools

from util import show_configuration

from lauterbach.trace32.pystart import PowerView, RCLInterface, USBConnection

tcp_port = itertools.count(start=20000)
powerview = PowerView(USBConnection(), "t32marm")

for _ in range(3):
    powerview.add_interface(RCLInterface(port=next(tcp_port), protocol="TCP"))

for _ in range(2):
    powerview.add_interface(RCLInterface(port=next(tcp_port), packlen=1024, protocol="UDP"))

show_configuration(powerview)
