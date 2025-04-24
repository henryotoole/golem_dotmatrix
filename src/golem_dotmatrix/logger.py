"""
Setup / configuration for logging.

Some notes on the strategy here:
I'm experimenting with the principles set down here:
https://www.structlog.org/en/stable/logging-best-practices.html
https://12factor.net/logs

That is, logging to STDOUT and letting it handle the rest. By default this will wind up in systemd's journaling
system and can be accessed with the usual journalctl -f -u golnet (or whatever the service file is named by the
sysadmin)

In development, of course, it shall simply hit the terminal.
"""
__author__ = "Josh Reed"

# Our code

# Other libs
import structlog
from structlog.stdlib import LoggerFactory

# Base python
import sys


# I'll need this eventually...
#def testproc(logger, log_method, event_dict):
#	print(log_method)
#	event_dict['key'] = 'value'
#	return event_dict

### Configure Structlog ###
# Processors that have nothing to do with output, e.g., add timestamps or log level names.
shared_processors = [
	# None yet
]

if sys.stderr.isatty():
	# Pretty printing when we run in a terminal session.
	# Automatically prints pretty tracebacks when "rich" is installed
	processors = shared_processors + [
		structlog.dev.ConsoleRenderer(),
	]
else:
	# Print JSON when we run, e.g., in a Docker container.
	# Also print structured tracebacks.
	processors = shared_processors + [
		structlog.processors.dict_tracebacks,
		structlog.processors.JSONRenderer(),
	]

structlog.configure(
	processors=processors
)