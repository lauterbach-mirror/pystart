import time
from typing import Any, Dict

import dotenv
import lauterbach.trace32.rcl as pyrcl

import lauterbach.trace32.pystart as pystart

dotenv.load_dotenv()
rcl_params: Dict[str, Any] = {"port": 20000, "protocol": "UDP", "packlen": 1024}

pv2 = pystart.PowerView(pystart.SimulatorConnection(), "t32marm")
pv2.add_interface(pystart.RCLInterface(**rcl_params))

pv2.start(delay=0.5)
with pyrcl.connect(**rcl_params, timeout=5.0) as dbg:
    dbg.cmd("AREA")
    dbg.print("rcl.connect(port=...)")
    time.sleep(3.0)

pv2.stop()
# use the stop() method just in case
# 1) you are running a software debugger (e.g. Simulator) or
# 2) if you powercycle your hardware debugger anyway
