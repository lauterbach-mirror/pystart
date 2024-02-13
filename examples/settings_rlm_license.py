from util import show_configuration

from lauterbach.trace32.pystart import PowerView, SimulatorConnection

powerview = PowerView(SimulatorConnection(), "t32marm")

powerview.rlm_port = 5055
powerview.rlm_server = "<RLM-Server>"
powerview.rlm_timeout = None

show_configuration(powerview)
