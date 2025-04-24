# golem_dotmatrix/__main__.py
# Josh Reed 2022 2025
#
# Runner file for the module

import sys

if len(sys.argv) < 2:
	raise ValueError("You want to add 'watchdog'")

if sys.argv[1] == 'watchdog':
	
	from golem_dotmatrix.watchdog import watchdog_loop
	watchdog_loop()