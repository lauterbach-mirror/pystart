import time

import dotenv
import lauterbach.trace32.rcl as pyrcl

import lauterbach.trace32.pystart as pystart

dotenv.load_dotenv()
port1 = 20000
port2 = port1 + 1

connection = pystart.USBConnection()

powerview1 = pystart.PowerView(connection, "t32marm")
powerview1.add_interface(pystart.RCLInterface(port1))

powerview2 = pystart.PowerView(connection, "t32marm")
powerview2.add_interface(pystart.RCLInterface(port2))

powerview1.start(delay=2)
powerview2.start(delay=2)

with pyrcl.connect(port=port2) as dbg:
    dbg.cmd("AREA")
    dbg.print("Hello PowerView2")
    print("Version(powerview2):", dbg.fnc.version_software())
    time.sleep(1.0)
    dbg.cmd("QUIT")  # close PowerView instance
powerview2.wait()

with pyrcl.connect(port=port1) as dbg:
    dbg.print("Hello PowerView1")
    print("Version(powerview1):", dbg.fnc.version_software())

powerview1.wait()  # wait for user to close PowerView instance
