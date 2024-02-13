from util import show_configuration

from lauterbach.trace32.pystart import EthernetConnection, PowerView

connection = EthernetConnection("<URI of Debugger>")

powerview = PowerView(connection, "t32marm")

show_configuration(powerview)
