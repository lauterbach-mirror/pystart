## Change Log

### v0.6.0
* add parameter setting for `connection_script`.
* Make `Connection` optional for `connection_script` not being ignored.
* add generic argument setting for starting TRACE32.

### v0.5.0
* add `connection_script` setting
* fix InteractiveConnection
* start windows 32bit executable only if `force_32bit_executable==True`, don't search for it, if 64bit executable is not available

### v0.4.0
* fix broken compatibility to python <3.9
* allow `PowerView` to be used as ContextManager

### v0.3.0
* add settings `REMOTEHOSTALLOW` and `REMOTEHOSTDENY` for some T32Interfaces

### v0.2.1
* use builtin `TimeoutError` instead of `TimeoutExpiredError`
* use builtin `RuntimeError` instead of `AlreadyRunningError`
* add `ViewerConnection`
* add `InteractiveConnection`
* put temporary config file also in T32TMP path
* throw on premature termination of PowerView process
* add `device_path` option to `USBConnection` and `USBProxyConnection`

### v0.2.0
* use binaries from `PATH` if no system_path is specified
* gently stop Trace32 on Windows OS
* added timeout for `PowerView.stop()`
* wait necessary time in `PowerView.start()` instead of waiting for a predefined amount of time
* added exeptions `TimeoutExpiredError` and `AlreadyRunningError`
* limit startup script parameter to be of type `Iterable[str]`
* send `stdout` and `stderr` output of PowerView instance to a logger

### v0.1.7
* fix datatype of `library_file` parameters in some Connection classes to allow `pathlib.Path`'s.
* add `TCPConnection` for Lauterbach X-Series debugger.
* rename `EthernetConnection` to `UDPConnection`

### v0.1.6
* initial release
