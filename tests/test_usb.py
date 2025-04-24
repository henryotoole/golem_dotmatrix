"""
Tests for USB
"""

# Project code
from golem_dotmatrix.usb import list_usb_devices, port_connect

# Other libs

# Base python

def test_list():

	list_usb_devices()
	
def test_port_connect():

	with port_connect(0x002d, 0x06bc) as endpoint:
		pass