from util import show_configuration

from lauterbach.trace32.pystart import PowerView, USBConnection

connection = USBConnection()

powerview = PowerView(connection, "t32mxtensa")

show_configuration(powerview)
