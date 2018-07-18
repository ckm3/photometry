#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Command-line utility to run TESS photometry from command-line.

Example:
	To run a random star from the TODO list:

	>>> python run_tessphot.py --random

Example:
	To run a specific star, you can provide the TIC-identifier:

	>>> python run_tessphot.py 182092046

Example:
	You can be very specific in the photometry methods and input to use.
	The following example runs PSF photometry on Target Pixel Files (tpf) of TIC 182092046,
	and produces plots in the output directory as well.

	>>> python run_tessphot.py --source=tpf --method=psf --plot 182092046

Note:
	run_tessphot is only meant for small tests and running single stars.
	For large scale calculation with many stars, you should use m:py:func:`mpi_scheduler`.

.. codeauthor:: Rasmus Handberg <rasmush@phys.au.dk>
"""

from __future__ import with_statement, print_function
import os
import argparse
import logging
import functools
from photometry import tessphot, TaskManager

#------------------------------------------------------------------------------
if __name__ == '__main__':

	# Parse command line arguments:
	parser = argparse.ArgumentParser(description='Run TESS Photometry pipeline on single star.')
	parser.add_argument('-m', '--method', help='Photometric method to use.', default=None, choices=('aperture', 'psf', 'linpsf', 'diffimg'))
	parser.add_argument('-s', '--source', help='Data-source to load.', default='ffi', choices=('ffi', 'tpf'))
	parser.add_argument('-d', '--debug', help='Print debug messages.', action='store_true')
	parser.add_argument('-q', '--quiet', help='Only report warnings and errors.', action='store_true')
	parser.add_argument('-p', '--plot', help='Save plots when running.', action='store_true')
	parser.add_argument('-r', '--random', help='Run on random target from TODO-list.', action='store_true')
	parser.add_argument('-t', '--test', help='Use test data and ignore TESSPHOT_INPUT environment variable.', action='store_true')
	parser.add_argument('starid', type=int, help='TIC identifier of target.', nargs='?', default=None)
	args = parser.parse_args()

	# Make sure at least one setting is given:
	if args.starid is None and not args.random:
		parser.error("Please select either a specific STARID or RANDOM.")

	# Set logging level:
	logging_level = logging.INFO
	if args.quiet:
		logging_level = logging.WARNING
	elif args.debug:
		logging_level = logging.DEBUG

	# Setup logging:
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	console = logging.StreamHandler()
	console.setFormatter(formatter)
	logger = logging.getLogger(__name__)
	logger.addHandler(console)
	logger.setLevel(logging_level)
	logger_parent = logging.getLogger('photometry')
	logger_parent.addHandler(console)
	logger_parent.setLevel(logging_level)

	# Get input and output folder from environment variables:
	test_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'tests', 'input'))
	if args.test:
		input_folder = test_folder
	else:
		input_folder = os.environ.get('TESSPHOT_INPUT', test_folder)
	output_folder = os.environ.get('TESSPHOT_OUTPUT', os.path.abspath('.'))
	logger.info("Loading input data from '%s'", input_folder)
	logger.info("Putting output data in '%s'", output_folder)

	# Create partial function of tessphot, setting the common keywords:
	f = functools.partial(tessphot, input_folder=input_folder, output_folder=output_folder, plot=args.plot)

	# Run the program:
	with TaskManager(input_folder) as tm:
		if args.starid is not None:
			task = tm.get_task(starid=args.starid)
			if args.method: task['method'] = args.method
			if args.source: task['datasource'] = args.source
		elif args.random:
			task = tm.get_random_task()

		del task['priority']
		pho = f(**task)

	# Write out the results?
	if not args.quiet:
		print("=======================")
		print("STATUS: {0}".format(pho.status.name))
