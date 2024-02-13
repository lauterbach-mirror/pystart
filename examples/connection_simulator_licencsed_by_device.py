from util import show_configuration

from lauterbach.trace32.pystart import (
    ConnectMode,
    PowerView,
    SimulatorConnection,
    USBConnection,
)

license_connection = USBConnection("Name", ConnectMode.QUERYCONNECT, True)

connection = SimulatorConnection(license_connection=license_connection)

powerview = PowerView(connection, "t32marm")

show_configuration(powerview)
