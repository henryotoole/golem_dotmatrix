# dotmatrix.py
# Josh Reed 2022
#
# The primary class file which is used to manipulate the dot matrix printer.

# Our code
from golem_dotmatrix import logger

# Other libs
import usb.core
import textwrap

# Base python
import math
import re
from contextlib import contextmanager

FONT_NLQ = "NLQ"
FONT_NLQ_GOTHIC = "NLQ_GOTHIC"
FONT_UTIL = "UTIL"
FONT_HSD = "HSD"

FONTS = {
	"NLQ": {
		'code': chr(27) + chr(45)
	},
	"NLQ_GOTHIC": {
		'code': chr(27) + chr(51)
	},
	"UTIL": {
		'code': chr(27) + chr(48)
	},
	"HSD": {
		'code': chr(27) + chr(35) + chr(48)
	},
}

CPIS = {
	"10CPI": {
		'code': chr(30),
		'cpi': 10
	},
	"12CPI": {
		'code': chr(28),
		'cpi': 12
	},
	"15CPI": {
		'code': chr(27) + chr(103),
		'cpi': 15
	},
	"17.1CPI": {
		'code': chr(29),
		'cpi': (120 / 7)
	},
	"20CPI": {
		'code': chr(27) + chr(35) + chr(51),
		'cpi': 20
	},
}

class DotMatrix():

	# Some notes:
	# There appear to be 66 lines in a 11in sheet of paper.
	# That's 6 lines per inch.

	def __init__(self, port_endpoint):
		"""Instantiate the dot matrix printer.
		"""		
		
		self.port_endpoint = port_endpoint

		self.font_mode_set("UTIL")

		# We assume that we start at 
		self._line_number = 0
		self._page_number = 0
		self._current_cpi_block = None # Set by cpi_set
		self._line_width_chars = None # Set by margin_set
		self._vmargin_lines = 0 # Set by margin_set

		# Determined this experimentally, doesn't appear possible to change.
		self.lpi = 6
		self.page_width = 8.5
		self.page_height = 11
		# The offset for the 'left' side of the carriage.
		self.carriage_home_offset = -0.3

		# Set default cpi
		self.cpi_set("12CPI")
		# Set default margins
		self.margin_set(0.5, 0.5)

	@classmethod
	@contextmanager
	def print_context(cls, endpoint):
		"""While not required, it's best practice to print from within a scope like this so certain
		finishing actions are always completed after a print job.

		Yields:
			cls instance (will extend DotMatrix)
		"""
		dmprinter = cls(endpoint)
		try:
			yield dmprinter
		finally:
			dmprinter.page_new()

	def print_job(self, job_data):
		"""Print standard-format job data.

		Job Instruction Format:
		{
			blocks: [
				str,
				str,
				str,...
			],
			printer_setup: CURRENTLY UNUSED
			# Reserved for setting CPI, font, etc.
		}

		Args:
			job_data (dict): Job data object
		"""

		job_name = job_data.get('name')
		dashes = '-'*len(str(job_name))

		logger.info("###---------------" + dashes + "--###")
		logger.info("###- Printing job " + str(job_name) + " -###")
		logger.info("###---------------" + dashes + "--###")

		blocks = job_data['blocks']
		for block in blocks:

			self.print_block(block)

	def print_block(self, block_text):
		"""Print a 'block', which is just a bunch of text that must start at the beginning of a page
		
		Args:
			block (str): Text to print
		"""

		# Go to top of page
		self.page_goto_line(0)
		# Ensure we're at start of line
		self.line_return()

		# Loop thru all sections designated by newline
		page_text_bits = block_text.splitlines()
		for text_bit in page_text_bits:

			# Special case to preserve empty lines
			if text_bit == "":
				self.write_line("")
			else:
				# For each of those, apply text wrap.
				lines_out = textwrap.wrap(text_bit, width=self._line_width_chars)
				for line in lines_out:
					self.write_line(line)

		# Go to top of page
		self.page_goto_line(0)

	def write_line(self, text):
		"""Write a line on the printer under its current configuration. This is the ONLY method that should
		be used to actually print a line of readable text so that vertical position is tracked right.

		Args:
			text (str): The text to write.
		"""
		if len(text) > self._line_width_chars:
			raise ValueError("Tried to print a line that was too long.")

		# Check and see if current line position is suitable for writing (e.g. not in a margin.)
		lines_adv = self.linepos_get_lines_out_of_margin()
		if lines_adv > 0:
			self.line_skip(lines_adv)
		
		# Write the line
		self.port_write(text + "\n")
		# Mark that we advanced.
		self.linepos_advance(1)

	def paper_type_set(self, width, height):
		"""Set the width and height of the paper being used, in inches.

		Args:
			width (int): The width in inches
			height (int): The height in inches
		"""
		self.page_width = width
		self.page_height = height

	def margin_set(self, horiz_margin, vert_margin):
		"""Set the margins being used

		Args:
			horiz_margin (int): The width in inches of the horizontal margin (width of left and right)
			vert_margin (int): The height in inches of the vertical margin
		"""

		# HORIZONTAL MARGIN SET
		# This is handled by the printer itself.
		left_dist = self.carriage_home_offset + horiz_margin
		right_dist = self.carriage_home_offset + self.page_width - horiz_margin
		left_dist = int(left_dist * 120)
		right_dist = int(right_dist * 120)
		
		text_width_in = (right_dist - left_dist) / 120
		self._line_width_chars = int(math.floor(text_width_in * self._current_cpi_block['cpi']))

		left_dist = str(left_dist).rjust(3, '0')
		right_dist = str(right_dist).rjust(4, '0')
		self.port_write(chr(27) + chr(37) + chr(67) + left_dist)
		self.port_write(chr(27) + chr(37) + chr(82) + right_dist)
		logger.info("Set horizontal margins to " + str(left_dist) + " and " + str(right_dist))

		# VERTICAL MARGIN SET
		# We have to keep track of this.
		# First convert to a number of lines, rounding up
		vert_margin_lines = int(math.ceil(vert_margin * self.lpi))
		logger.info("Set vertical margins to " + str(vert_margin_lines) + " lines.")
		self._vmargin_lines = vert_margin_lines

	def line_feed(self):
		"""Perform a line feed. This rolls to a new line and does a carriage return.
		"""
		self.port_write(chr(10))

		# Record that we advanced.
		self.linepos_advance(1)

	def line_skip(self, n):
		"""Skip the provided number of lines.

		Args:
			n (int): The number of lines to skip.
		"""
		if n > 99:
			raise ValueError("Can skip max of 99 lines")
		logger.info("Skipping " + str(n) + " lines")
		self.port_write(chr(27))
		self.port_write(chr(11))
		nstr = str(n).rjust(2, '0')
		self.port_write(nstr)

		# Record that we advanced.
		self.linepos_advance(n)

	def line_return(self):
		"""Send print head to left
		"""
		self.port_write("\r")

	def linepos_advance(self, n):
		"""Advance our internal tracker of line position by n lines. This accounts for incrementing 
		everything, including page tracker.
		"""
		self._line_number += n
		while self._line_number > self.page_lines_get():

			self._page_number += 1
			self._line_number -= self.page_lines_get()

	def linepos_is_suitable_for_text(self):
		"""Get whether the current line position is suitable for text.

		Returns:
			bool: True if we can write text or false if we are in a margin
		"""
		return self.linepos_get_lines_out_of_margin() > 0

	def linepos_get_lines_out_of_margin(self):
		"""Get the number of lines we need to advance to get out of the margin, given our current
		line position.

		Returns:
			int: 0 if we aren't in a margin, or a number of lines to advance to escape a margin
		"""

		# We are in top margin
		if self._line_number < self._vmargin_lines:
			return self._vmargin_lines - self._line_number
		elif self._line_number >= self.page_lines_get() - self._vmargin_lines:
			# Dist to end of page plus next top margin
			return (self.page_lines_get() - self._line_number) + self._vmargin_lines
		else:
			# Not in margin
			return 0

	def form_feed(self):
		"""Perform a form feed. This rolls to a new page and does a carriage return.
		"""
		raise ValueError("WE DO NOT USE THIS")
		self.port_write(chr(12))

	def font_mode_set(self, mode):
		"""Set font mode. This is one of the FONT_ objects at the top of this file.

		Args:
			mode (str): The font mode to select
		"""
		if mode in FONTS:
			self.port_write(FONTS[mode]['code'])
		else:
			raise ValueError("Invalid font")

	def cpi_set(self, cpi):
		"""Set cpi of the printer. This is one of CPIS at top of file.

		Args:
			cpi (str): The cpi to select (like 12CPI)
		"""
		if cpi in CPIS:
			self.port_write(CPIS[cpi]['code'])
			self._current_cpi_block = CPIS[cpi]
		else:
			raise ValueError("Invalid CPI")

	def page_lines_get(self):
		"""Get the number of lines in a page given current config
		"""
		return self.page_height * self.lpi
	
	def page_goto_line(self, line_number):
		"""Go to the specified line number
		"""
		# If we're already there, just return
		if self._line_number == line_number:
			return

		lines_total = self.page_lines_get()
		if line_number > lines_total:
			raise ValueError("Cannot go to line number " + str(line_number) + " as it's higher than max " + str(lines_total))

		adv_dist = 0

		# Simple forwards
		if self._line_number < line_number:
			adv_dist = line_number - self._line_number
		# We want to go 'behind' where we are now, and must go to next page to do so
		else:
			adv_dist = (lines_total - self._line_number) + line_number

		self.line_skip(adv_dist)

	def page_new(self):
		"""Send printer to start of next page.
		"""
		self.page_goto_line(0)

	def port_write(self, chars):
		"""Write data straight to the port. This can be pure text to be printed, or an ASCII control char.

		Args:
			chars (str): The characters to print or control codes to fire.
		"""
		try:
			self.port_endpoint.write(chars)
		except usb.core.USBTimeoutError as e:
			logger.error(
				"USB Timeout error detected! This is likely because the 'SEL' button needs to be " + \
				"pressed on the physical printer. SEL should be lit as well as a PRINT QUALITY and CHARACTER " + \
				"pitch option."
			)

class DotMatrixEmulator(DotMatrix):

	def __init__(self, endpoint=None):
		"""An emulator which sort of simulates what the code here does without actually making
		the printer print stuff (which saves on paper)
		"""

		self.printed = ""

		super().__init__(endpoint)

	def port_connect(self):
		"""Prevent connection
		"""
		logger.info("Faux-connected to port.")

	def port_write(self, chars):
		"""Does nothing
		"""
		self.printed += chars


		chars_conv = ""
		for c in chars:
			if not c.isalnum():
				if c == "\n" or c ==" ":
					chars_conv += c
				else:
					chars_conv += "[" + str(ord(c)) + "]"
			else:
				chars_conv += c

		if chars_conv[-1] == "\n":
			chars_conv = chars_conv[:-1]
		logger.info(">> " + chars_conv)

	def print_to_console(self):
		"""Print all that's been printed so far to console
		"""
		print(self.printed)