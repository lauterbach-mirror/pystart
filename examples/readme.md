The examples within this folder should ease the first use of `lauterbach-trace32-pystart`.

## Configuration Examples
These examples only focus on how to set up TRACE32 PowerView. The examples just print the used executables and the
resulting config files. Therefore this examples can be executed, even if TRACE32 is not installed.
* `connection_*.py`: examples for setting up different connections (How does PowerView communicate with the debugger).
* `interface_*.py`: examples for configuring several interfaces (How can a client communicate with PowerView)
* `settings_*.py`: examples for configuring PowerView (e.g. screen, license, paths, ...)
* `util.py`: contains some functions for printing the executable and the configuration file.

## Run Examples
These examples actually start a PowerView instance. For this we assume either TRACE32 is installed at "C:\T32" or
environment variable "T32SYS" points to the installation path and the "t32marm" executable is available. Due to
executing `dotenv.load_dotenv()` within these examples it is also possible to add a file called ".env", containing the
line `T32SYS=<your install path>`.
* `run_*.py`: examples starting some PowerView instances.
