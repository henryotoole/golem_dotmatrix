"""
Tests for the watchdog loop
"""

# Project code
from golem_dotmatrix.watchdog import watchdog_loop

# Other libs
import pytest

# Base python

@pytest.mark.skip(reason="Manual test.")
def test_watchdog():
	"""Test the watchdog in emulation mode.
	"""
	print("Running watchdog in emulator mode. Must CTRL+C to break.")
	watchdog_loop(emulate=True, interval=3)