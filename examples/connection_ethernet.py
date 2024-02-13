from util import show_configuration

from lauterbach.trace32.pystart import PowerView, UDPConnection

connection = UDPConnection("<URI of Debugger>")

powerview = PowerView(connection, "t32marm")

show_configuration(powerview)
