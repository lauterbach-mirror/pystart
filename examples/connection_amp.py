from util import show_configuration

from lauterbach.trace32.pystart import PowerView, USBConnection

connection = USBConnection()

powerview1 = PowerView(connection, "t32marm")
powerview2 = PowerView(connection, "t32marm")

print("powerview1:")
show_configuration(powerview1)
print("powerview2:")
show_configuration(powerview2)
