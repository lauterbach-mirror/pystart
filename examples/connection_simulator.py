from util import show_configuration

from lauterbach.trace32.pystart import PowerView, SimulatorConnection

connection = SimulatorConnection()

powerview = PowerView(connection, "t32marm")

show_configuration(powerview)
