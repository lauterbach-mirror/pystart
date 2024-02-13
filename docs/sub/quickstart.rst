##########
Quickstart
##########

***************
Getting Started
***************

For starting TRACE32 follow these steps:

#. Set :obj:`~lauterbach.trace32.pystart.defaults` members depending to your environment

   * Most default settings should be appropriate

#. Create a :class:`~lauterbach.trace32.pystart.PowerView` object

   * Define a :ref:`T32Connection`
   * Specify your target

#. Configure your :class:`~lauterbach.trace32.pystart.PowerView` instance as needed (e.g. add a :ref:`T32Interface`)
#. :meth:`~lauterbach.trace32.pystart.PowerView.start` your created :class:`~lauterbach.trace32.pystart.PowerView`
   instance
#. Do your work.
#. Either :meth:`~lauterbach.trace32.pystart.PowerView.wait` for termination or
   :meth:`~lauterbach.trace32.pystart.PowerView.stop` the :class:`~lauterbach.trace32.pystart.PowerView` instance
   manually.

****************************
Minimal USB debugger example
****************************
.. code-block:: python

	import lauterbach.trace32.pystart as pystart

	# If installation is not located at "C:\T32" and environment variable "T32SYS" is not
	# pointing to the installation directory of TRACE32 add following line:
	# pystart.defaults.system_path = "</path/to/TRACE32/installation>"

	pv = pystart.PowerView(pystart.USBConnection(), "t32marm")
	pv.start()
	pv.wait()


*********************************
Minimal ethernet debugger example
*********************************
.. code-block:: python

	import lauterbach.trace32.pystart as pystart

	# If installation is not located at "C:\T32" and environment variable "T32SYS" is not
	# pointing to the installation directory of TRACE32 add following line:
	# pystart.defaults.system_path = "</path/to/TRACE32/installation>"

	connection = pystart.EthernetConnection("<IP address or DNS name of the debugger>")
	pv = pystart.PowerView(connection, "t32marm")
	pv.start()
	pv.wait()
