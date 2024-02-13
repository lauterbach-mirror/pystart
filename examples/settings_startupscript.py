from util import show_configuration

from lauterbach.trace32.pystart import PowerView, SimulatorConnection

powerview = PowerView(SimulatorConnection(), "t32marm")

# Set startup script
powerview.startup_script = "startup_script.cmm"

# eventually you want to provide some parameters
powerview.startup_parameter = "param1 param2 param3"
# or
powerview.startup_parameter = ["param1", "param2", "param3"]

show_configuration(powerview)
