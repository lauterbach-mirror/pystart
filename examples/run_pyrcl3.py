import time
from typing import Any, Dict

import lauterbach.trace32.rcl as pyrcl

import lauterbach.trace32.pystart as pystart

rcl_params: Dict[str, Any] = {"port": 20000, "protocol": "UDP", "packlen": 1024}

powerview = pystart.PowerView(pystart.SimulatorConnection(), "t32marm")
powerview.add_interface(pystart.RCLInterface(**rcl_params))

powerview.start()

with pyrcl.connect(**rcl_params, timeout=5.0) as dbg:
    dbg.cmd("AREA")
    dbg.print("rcl.connect(port=...)")
    time.sleep(2.0)
    dbg.cmd("QUIT")
