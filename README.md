# lauterbach-trace32-pystart
Since 2020, Python programs can control TRACE32 via the lauterbach-trace32-rcl module (pyrcl). Up to now, TRACE32 must be started using a config file, which requires familiarization with the TRACE32 configuration file syntax or the use of the configuration tool t32start.exe. Now Lauterbach offers a new
lauterbach-trace32-pystart module (pystart) which allows the configuration and start of TRACE32 directly from Python.

For feedback and questions, please contact support@lauterbach.com (include "pystart" in the subject).

## Example
```python
import lauterbach.trace32.pystart as pystart

pystart.defaults.system_path = r"C:\T32"

powerview = pystart.PowerView(pystart.USBConnection(), "t32marm")
powerview.title = f"TRACE32 PowerView for ARM 0"
powerview.id = "T32_arm0"

powerview.start()
powerview.wait()
```

## Release Notes
### v*
* use binaries from `PATH` if no system_path is specified
* gently stop Trace32 on Windows OS
* added timeout for `PowerView.stop()`
* wait necessary time in `PowerView.start()` instead of waiting for a predefined amount of time

### v0.1.7
* fix datatype of `library_file` parameters in some Connection classes to allow `pathlib.Path`'s.
* add `TCPConnection` for Lauterbach X-Series debugger.
* rename `EthernetConnection` to `UDPConnection`

### v0.1.6
* initial release
