from util import show_configuration

from lauterbach.trace32.pystart import PowerView, SimulatorConnection

powerview = PowerView(SimulatorConnection(), "t32marm")
powerview.license_file = "<license file outside of sys_paths root directory>"

show_configuration(powerview)
