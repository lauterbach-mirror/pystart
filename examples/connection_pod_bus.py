# Debugger-Configuration:
#
# USB --> PowerDebugPro ----------------> T32(ARM)
#         |-- Debugger via PodBus ------> T32(XTENSA), T32(ARC) # AMP setup
#         |-- Some other PodBus Device
#         |-- Debugger via PodBus ------> T32(C2000)

from util import show_configuration

from lauterbach.trace32.pystart import PowerView, USBConnection

connection = USBConnection()

powerview1 = PowerView(connection, "t32marm", pbi_index=0)
powerview2 = PowerView(connection, "t32mxtensa", pbi_index=1)
powerview3 = PowerView(connection, "t32marc", pbi_index=1)
powerview4 = PowerView(connection, "t32m2000", pbi_index=3)

show_configuration(powerview1)
show_configuration(powerview2)
show_configuration(powerview3)
show_configuration(powerview4)
