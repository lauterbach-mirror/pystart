from util import show_configuration

from lauterbach.trace32.pystart import PowerView, USBConnection

powerview = PowerView(USBConnection(), force_executable="<Custom Executable>")
# or as an alternative:
# powerview.force_executable = "<Custom Executable>"

show_configuration(powerview)
