"""
A file where we declare and typehint the config that is used for GOLNET. This config is only used for terminal
and library mode.
"""
__author__ = "Josh Reed"

# Our code

# Other libs

from hacutils.config import CfgEntry

# Base python
from typing import TypedDict

# This exists only to typehint the config object.
class Config(TypedDict):
	SERVER_HOSTNAME: str
	PROTOCOL: str

CONFIG_DEFAULTS = [
	CfgEntry('SERVER_HOSTNAME', default="www.theroot.tech", comment="The server hostname e.g. golem.example.com"),
	CfgEntry('PROTOCOL', default="https", comment="The protocol used e.g. http or https. Only https should be " + \
		"used in production"),
]