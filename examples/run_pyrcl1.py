import dotenv
import lauterbach.trace32.rcl as pyrcl

import lauterbach.trace32.pystart as pystart

dotenv.load_dotenv()
port = 20000

powerview = pystart.PowerView(pystart.SimulatorConnection(), "t32marm")
powerview.add_interface(pystart.RCLInterface(port))
powerview.start(delay=0.5)

with pyrcl.connect(port=port) as dbg:
    dbg.cmd("AREA")
    dbg.print("Hello PowerView1")
    print("Version(powerview1):", dbg.fnc.version_software())
    # dbg.cmd("QUIT")  # close PowerView instance from script

powerview.wait()  # wait for termination of PowerView
