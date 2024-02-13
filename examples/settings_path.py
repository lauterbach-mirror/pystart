import tempfile

from util import show_configuration

from lauterbach.trace32.pystart import PowerView, USBConnection, defaults

# Variant 0: Default on Windows environments is r"C:\T32"
# Variant 1: via environment variable "T32SYS"
# Variant 2: via library global variable:
defaults.system_path = r"C:\Some\other\path"

# Varaint 3: Specify system_path via constructor
powerview1 = PowerView(USBConnection(), "t32mxtensa", system_path=r"C:\T32")

print("powerview1:")
show_configuration(powerview1)


# Variant 4: Specify each individual path
powerview2 = PowerView(USBConnection(), "t32marm")
powerview2.system_path = r"C:\T32"
powerview2.temp_path = tempfile.gettempdir()
powerview2.help_path = r"C:\T32\pdf"
powerview2.force_32bit_executable = False

print("powerview2:")
show_configuration(powerview2)
