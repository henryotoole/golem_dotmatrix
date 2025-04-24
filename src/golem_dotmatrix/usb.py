"""
USB Utilities
"""

# Project code
from golem_dotmatrix import logger

# Other libs
import usb.core
import usb.util

# Base python
from contextlib import contextmanager


def list_usb_devices():

	devices = usb.core.find(find_all=True)
	print("Scanning for all devices.")
	for dev in devices:
		print(dev)

@contextmanager
def port_connect(id_product, id_vendor):

	port = usb.core.find(idProduct=id_product, idVendor=id_vendor)

	if port is None:
		raise ValueError("Can not find OKI Microline 321 in USB listings.")

	# get an endpoint instance
	cfg = port.get_active_configuration()
	intf = cfg[(0,0)]

	ep = usb.util.find_descriptor(
		intf,
		# match the first OUT endpoint
		custom_match = \
		lambda e: \
			usb.util.endpoint_direction(e.bEndpointAddress) == \
			usb.util.ENDPOINT_OUT)

	assert ep is not None

	if port.is_kernel_driver_active(0):
		try:
			port.detach_kernel_driver(0)
			logger.info("kernel driver detached")
		except usb.core.USBError as e:
			sys.exit("Could not detach kernel driver: %s" % str(e))

	logger.info("Connected to USB")
	yield ep

	usb.util.dispose_resources(port)
	logger.info("Disconnected from USB")