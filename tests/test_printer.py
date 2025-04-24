
# Project code
from golem_dotmatrix.dotmatrix import DotMatrix, DotMatrixEmulator

# Other libs
import pytest

# Base python

PRINTER_AVAIL = True

@pytest.mark.skipif(not PRINTER_AVAIL, reason="No printer available.")
def test_actual_print():
	"""Test use of real printer"""

	with DotMatrix.print_context() as dmprinter:
		dmprinter.print_block("One\ntwo\nthree")

def test_print_blocks():
	"""Test that we can print a block properly
	"""

	test_block = ""
	test_block += "This is line one of test block. It should be at the top of a page.\n"
	test_block += "This is line two of test block\n"
	test_block += "These should all be on different lines\n\n"
	test_block += "There should be an empty line above this.\n"
	test_block += "Now for 20 empty lines\n"
	test_block += "\n"*20
	test_block += "Now for 20 empty lines\n"
	test_block += "\n"*20
	test_block += "Now for 20 empty lines\n"
	test_block += "\n"*20
	test_block += "Now for 20 empty lines\n"
	test_block += "\n"*20
	test_block += "Last line..."

	with DotMatrixEmulator.print_context() as dmprinter:
		dmprinter.print_block(test_block)
		dmprinter.print_block(test_block)

def test_print_block_newlines():
	"""Test that we handle newlines correctly in big blocks.
	"""
	test_block = "Each line should have another right below it.\n"
	test_block += "Each line should have another right below it.\n"
	test_block += "Each line should have another right below it.\n"
	test_block += "Each line should have another right below it.\n"
	test_block += "Each line should have another right below it.\n\n"
	test_block += "Except for this, which should have an empty line above.\n"

	with DotMatrixEmulator.print_context() as dmprinter:
		dmprinter.print_block(test_block)

def test_textwrap():
	"""Test that we can wrap text correctly
	"""
	test_block = ""
	test_block += "Ensure that none of these words is split across lines." * 20
	test_block += "\n"
	test_block += "NEWLINE\n\n"
	test_block += "NEWLINE TWICE"

	with DotMatrixEmulator.print_context() as dmprinter:
		dmprinter.print_block(test_block)

def test_v_margins():
	"""Test that vertical margins work
	"""
	with DotMatrixEmulator.print_context() as dmprinter:
		for x in range(int(dmprinter.page_lines_get() * 1.5)):
			dmprinter.write_line("Line " + str(x))