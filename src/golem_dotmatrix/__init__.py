"""
Baseline module imports for the dotmatrix runner.
2022 2025
"""
__author__ = "Josh Reed"

# Other libs
from dispatch_client_py.dispatch_client import DispatchClient
from hacutils import config as hac_config
import structlog
import urllib3

# Base python
import pathlib
import os

project_path = pathlib.Path(__file__).parent.parent.parent.resolve()
"""This is the root path to the project and git repository.
"""

from golem_dotmatrix.cfg import Config, CONFIG_DEFAULTS

# Import the config
try:
	config: Config = hac_config.load_config(hac_config.find_config(project_path, 'golem_dotmatrix'))
except ValueError as e:
	hac_config.generate_from_defaults("./golem_dotmatrix.default.cfg", CONFIG_DEFAULTS)
	print(f"A default config file has been placed at {os.path.abspath('./golem_dotmatrix.default.cfg')}")
	raise
hac_config.defaults_apply(config, CONFIG_DEFAULTS)

# Configure the logger
import golem_dotmatrix.logger
logger: structlog.stdlib.BoundLogger = structlog.get_logger()

# Setup dispatch client.
dispatcher = DispatchClient(
	f"{config['PROTOCOL']}://{config['SERVER_HOSTNAME']}", verbose=True, client_name='dotmatrix'
)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Import structure
from golem_dotmatrix.dotmatrix import DotMatrix, DotMatrixEmulator