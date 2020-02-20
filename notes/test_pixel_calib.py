# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 14:11:53 2020

@author: au195407
"""

import os.path
import numpy as np
import logging
from astropy.io import fits
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from photometry.pixel_calib import PixelCalibrator
from photometry.plots import plt

#--------------------------------------------------------------------------------------------------
if __name__ == '__main__':

	plt.switch_backend('Qt5Agg')

	logging_level = logging.DEBUG

	# Configure the standard console logger
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	console = logging.StreamHandler()
	console.setFormatter(formatter)

	# Configure this logger
	logger = logging.getLogger('photometry')
	if not logger.hasHandlers():
		logger.addHandler(console)
	logger.setLevel(logging_level)

	with fits.open('tess2018210095942-s0001-3-4-0120-s_ffir.fits', mode='readonly') as ffi:
		with PixelCalibrator(camera=ffi[1].header['CAMERA'], ccd=ffi[1].header['CCD']) as pcal:
			print(pcal)

			ffi_cal = pcal.calibrate_ffi(ffi)

"""
	with fits.open('tess2018206045859-s0001-0000000008195886-0120-s_tp.fits.gz', mode='readonly') as tpf:

		with PixelCalibrator(camera=tpf[0].header['CAMERA'], ccd=tpf[0].header['CCD']) as pcal:
			print(pcal)

			pcal.plot_flatfield()
			pcal.plot_twodblack()

			tpf_cal = pcal.calibrate_tpf(tpf)

			plt.show()
"""
