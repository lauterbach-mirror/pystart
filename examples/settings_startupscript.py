from util import show_configuration

from lauterbach.trace32.pystart import PowerView, SimulatorConnection

powerview = PowerView(SimulatorConnection(), "t32marm")

# Set startup script
powerview.startup_script = "startup_script.cmm"

# eventually you want to provide some parameters
powerview.startup_parameter = ["param1", "param2", "param3", "KEY=value with spaces"]
# if you want to retrive parameters by "PARAMETERS" command consider adding additional quotes:
powerview.startup_parameter = ['"param1"', '"param2"', '"param3"', '"KEY=value with spaces"']

show_configuration(powerview)
