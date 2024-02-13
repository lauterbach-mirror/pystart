from util import show_configuration

from lauterbach.trace32.pystart import IntercomInterface, PowerView, USBConnection

connection = USBConnection()
powerview = PowerView(connection, "t32marm")

powerview.add_interface(IntercomInterface(name="<Intercom Name>", port=10000, packlen=1024))

show_configuration(powerview)
