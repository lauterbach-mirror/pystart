import dotenv

from lauterbach.trace32.pystart import PowerView, SimulatorConnection

dotenv.load_dotenv()

powerview = PowerView(SimulatorConnection(), "t32marm")

# If neither environment variable "T32SYS" is set to the path to the TRACE32 installation nor you have an installation
# in "C:\T32\" you have to specify a system_path
# powerview.set_system_path("path/to/TRACE32")

powerview.start()  # SimulatorConnections start relatively fast

powerview.wait()  # wait until TRACE32 instance is closed
