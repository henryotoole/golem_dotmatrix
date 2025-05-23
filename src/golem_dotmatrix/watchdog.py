# watchdog.py
# Josh Reed 2022
#
# Ticker file used to watch dispatch for printer jobs.

# Our code
from golem_dotmatrix import dispatcher, logger
from golem_dotmatrix.dotmatrix import DotMatrix, DotMatrixEmulator
from golem_dotmatrix.usb import port_connect

# Other libs

# Base python
import time
import os
import traceback

def watchdog_loop(emulate=False, interval=15):
	"""
	Loop forever, at 15 second interval, checking if there's a new print job.

	Args:
		emulate (bool, optional): Whether to run in emulation-only mode. Default False.
	"""

	while True:

		try:
			job_data = dispatcher.call_server_function(
				'dotmatrix_get_from_queue'
			)

			if job_data is not None and not job_data == {}:

				if emulate:
					with port_connect(0x002d, 0x06bc) as endpoint:
						with DotMatrix.print_context(endpoint) as dmprinter:
							dmprinter.print_job(job_data)
				else:
					with DotMatrixEmulator.print_context(None) as dmprinter:
						dmprinter.print_job(job_data)
			
		except Exception:
			job_data = None
			logger.error(traceback.format_exc())


		time.sleep(interval)